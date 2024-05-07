import ccxt
import time
import json
from utils import logger
import sys
from helpers import average_asset_price_with_gain

with open(sys.argv[1], 'r') as file:
    configs = json.load(file)

# The symbol to trade
symbol = configs['symbol']

# The exchanges names
ex_source = configs['exchanges']['source']['name']
ex_destination = configs['exchanges']['destination']['name']

#deposit address and chains
ex_source_deposit_address = configs['exchanges']['source']['address']
ex_source_chain = configs['exchanges']['source']['chain']
ex_destination_deposit_address = configs['exchanges']['destination']['address']
ex_destination_chain = configs['exchanges']['destination']['chain']

minimal_margin = float(configs['minimal_margin'])
minimal_quote = float(configs['minimal_quote'])
maximal_quote = float(configs['maximal_quote'])

# Initialize the exchanges
exchange1 = getattr(ccxt, ex_source)(configs['exchanges']['source']['key'])
exchange2 = getattr(ccxt, ex_destination)(configs['exchanges']['destination']['key'])

base_asset, quote_asset = symbol.split('/')

if getattr(exchange1, 'sign_in', None):
    exchange1.sign_in()

if getattr(exchange2, 'sign_in', None):
    exchange2.sign_in()

exchange1.options['createMarketBuyOrderRequiresPrice'] = False
exchange2.options['createMarketBuyOrderRequiresPrice'] = False


def wait_for_deposit(exchange, asset, ts=30):
    balance = exchange.fetch_balance()
    if asset in balance['free']:
        n_asset = float(balance['free'][asset])
    else:
        n_asset = 0

    balance_asset = n_asset
    while n_asset == balance_asset:
        time.sleep(ts)  # Wait for 1 minute
        balance = exchange.fetch_balance()
        if asset in balance['free']:
            balance_asset = float(balance['free'][asset])
        logger.debug(f'Waiting for deposit of {asset} at {ex_source} balance {balance_asset}...')
    
    return balance_asset

def get_balance(exchange, asset):
    balance = exchange.fetch_balance()
    if asset in balance['free']:
        return float(balance['free'][asset])
    else:
        return 0
    
def wait_order(exchange, order, symbol):
    while True:
        updated_order = exchange.fetch_order(order['id'], symbol)
        if updated_order['status'] == 'filled' or updated_order['status'] == 'closed' or updated_order['status'] == 'canceled':
            break
        time.sleep(10)
    return float(updated_order['filled'])

def limit_order_sell(exchange, symbol):
    base_asset, quote_asset = symbol.split('/')

    while True:
        #Qty available to sell
        balance  = exchange.fetch_balance()
        asset_qty = float(balance['free'][base_asset])

        logger.debug(f'Qty available to sell: {asset_qty} {base_asset}')

        #Current price and quantity of the asset
        orderbook = exchange.fetch_order_book(symbol)
        bid, quantity = orderbook['bids']
        qty = min(asset_qty, quantity)

        #finish when there is no more asset to sell
        try:
            amount = float(exchange.amount_to_precision(symbol, qty))
        except:
            break

        #Limit order 
        order = exchange.create_limit_sell_order(symbol, amount, bid)

        wait_order(exchange, order, symbol)

    return order

def arbitrage():
    while True:
        # 1. Check the price of the asset at exchange 1 using the ask from book order
        logger.debug("Checking the price of the asset at exchange 1 using the ask from book order")
        orderbook1 = exchange1.fetch_order_book(symbol)
        ask = orderbook1['asks'][0][0]
        logger.info(f'{ex_source} Ask Price: {ask}')


        # 2. Check the price of the asset at exchange 2 using the bid from book order
        logger.debug("Checking the price of the asset at exchange 2 using the bid from book order")
        orderbook2 = exchange2.fetch_order_book(symbol)
        bid = orderbook2['bids'][0][0]
        logger.info(f'{ex_destination} Bid Price: {bid}')

        # 3. Check the funds at exchange 1
        logger.debug("Checking the funds at exchange 1")
        balance1 = exchange1.fetch_balance()
        if quote_asset not in balance1['free']:
            logger.warning(f'No {quote_asset} funds at {ex_source} to trade {symbol}!')
            #break

        funds1 = min(float(balance1['free'][quote_asset]), maximal_quote)

        # 4. Calculate the amount of funds to trade based on the amount of funds available and the orderbook
        logger.debug("Calculating the amount of funds to trade based on the amount of funds available and the orderbook")
        available_amount, asset_amount, ask_av_price, bid_av_price = average_asset_price_with_gain(orderbook1, orderbook2, funds1, minimal_margin)
        logger.debug(f'Orderbook availability {available_amount:.2f} {quote_asset} | {asset_amount} {base_asset} | Buy at {ask_av_price:.8f} {quote_asset} | Sell at {bid_av_price:.8f} {quote_asset} | {(bid_av_price-ask_av_price)/ask_av_price*100:.2f}%')
        if available_amount < minimal_quote:
            logger.warning(f'Not enough {base_asset} funds at {ex_source}!')
            time.sleep(10)
            continue

        # 5. Get the withdraw and maker fees
        logger.debug("Getting the withdraw and maker fees")
        try:
            ex1_funding_fees = exchange1.fetchTransactionFees()
            if isinstance(ex1_funding_fees[base_asset]['withdraw'], dict) == False:
                withdraw_fee = float(ex1_funding_fees[base_asset]['withdraw']) * ask_av_price
            else:
                withdraw_fee = float(ex1_funding_fees[base_asset]['withdraw'][ex_destination_chain]) * ask_av_price
        except:
            withdraw_fee = float(configs['exchanges']['source']['withdrawal_fee']) * ask_av_price
        
        ex1_maker_fee = float(exchange1.fees['trading']['maker'])
        ex2_maker_fee = float(exchange2.fees['trading']['maker'])

        logger.info(f'{ex_source} withdraw_fee {withdraw_fee} {quote_asset} maker_fee {ex1_maker_fee}')
        logger.info(f'{ex_destination} maker_fee {ex2_maker_fee}')

        # 5.1 Estimate the margin gain after the arbitrage
        margin = available_amount / ask_av_price * bid_av_price - withdraw_fee - (available_amount * ex1_maker_fee) - (available_amount / ask_av_price * bid_av_price * ex2_maker_fee)
        margin_percentage = (margin - available_amount) / available_amount * 100

        logger.debug(f'Arbitrage gain: {margin:.2f} {quote_asset} ({margin_percentage:.2f}%)')

        # 6. If we have a good margin, execute the arbitrage
        if margin_percentage > minimal_margin:
            # 7 Buy the asset
            logger.debug(f"Buying the asset {base_asset}")
            amount_to_buy = float(exchange1.amount_to_precision(symbol, available_amount))
            order = exchange1.create_market_buy_order(symbol, amount_to_buy)
            amount_bought = wait_order(exchange1, order, symbol)

            # 7.1 check balance
            balance1 = exchange1.fetch_balance()
            amount_bought = float(balance1['free'][base_asset])

            # 8 Move it to exchange 2
            logger.info(f'Withdraw {amount_bought} {base_asset} to {ex_destination}')
            exchange1.withdraw(base_asset, amount_bought, ex_destination_deposit_address, None, {'network': ex_destination_chain})

            # 8.1 Wait for the transfer to complete
            logger.debug(f"Waiting for the transfer to complete")
            balance2_asset = wait_for_deposit(exchange2, base_asset)

            # 9 Sell the asset at exchange 2
            logger.info(f"Selling the asset {balance2_asset} {base_asset} at {ex_destination}")
            amount_to_sell = float(exchange2.amount_to_precision(symbol, balance2_asset))
            try:
                order = exchange2.create_market_sell_order(symbol, amount_to_sell)
                amount_selled = wait_order(exchange2, order, symbol)
            except:
                logger.error(f"Using limit order to sell {balance2_asset} {base_asset} at {ex_destination}")
                limit_order_sell(exchange2, symbol)
                

            # 10 Move the funds back to exchange 1
            balance2 = exchange2.fetch_balance()
            amount_selled = float(balance2['free'][quote_asset])

            exchange2.withdraw(quote_asset, amount_selled, ex_source_deposit_address, None, {'network': ex_source_chain})

            # 10.1 Wait for the transfer to complete before going back to step 1
            wait_for_deposit(exchange1, quote_asset)

if __name__ == '__main__':
    arbitrage()
