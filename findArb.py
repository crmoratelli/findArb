import ccxt
import itertools
import random
from concurrent.futures import ThreadPoolExecutor
import time
from tabulate import tabulate
import pandas as pd
from utils import exchanges, symbols, logger, minimal_profit, max_profit, max_amount
from helpers import average_asset_price_with_gain

logger.info('Starting the arbitrage bot...')

all_symbols = []
for e in exchanges:
    for s in symbols[e]:
        if s not in all_symbols:
            all_symbols.append(s)

logger.info(f'Find {len(all_symbols)} symbos in {len(exchanges)} exchanges.')

# Initialize the table headers
headers=['Symbol', 'Source', 'Av. Price', 'Destination', 'Av. Price', 'Available (USDT)', 'Price Difference(%)']

# Initialize the exchanges objects
exchange_objs = [getattr(ccxt, exchange)() for exchange in symbols.keys()]

# Initialize the data structure to store the latest prices
prices = {exchange.id: {symbol: { 'bids': None, 'asks': None} for symbol in symbols[exchange.id]} for exchange in exchange_objs}

#Find price differences and amount of assets available for trading on each exchange
def calculate_max_min(prices):
    highest_prices = {symbol: {'price': 0, 'exchange': '', 'available_amount': 0, 'asset_amount': 0} for symbol in all_symbols}
    lowest_prices = {symbol: {'price': 0, 'exchange': '', 'per_gain': 0} for symbol in all_symbols}
    for ex_source in exchange_objs:
        for ex_dest in exchange_objs:
            if ex_source == ex_dest:
                continue
            common_symbols = [s for s in symbols[ex_source.id] if s in symbols[ex_dest.id]]
            for symbol in common_symbols:
                if (prices[ex_source.id][symbol]['asks'] is not None and 
                    prices[ex_dest.id][symbol]['bids'] is not None):

                    available_amount, asset_amount, ask_av_price, bid_av_price = average_asset_price_with_gain(prices[ex_source.id][symbol], prices[ex_dest.id][symbol], max_amount, minimal_profit)    

                    if available_amount > 0:
                        highest_prices[symbol]['price'] = bid_av_price
                        highest_prices[symbol]['exchange'] = ex_dest.id
                        highest_prices[symbol]['available_amount'] = available_amount
                        highest_prices[symbol]['asset_amount'] = asset_amount
                        lowest_prices[symbol]['price'] = ask_av_price
                        lowest_prices[symbol]['exchange'] = ex_source.id
                        lowest_prices[symbol]['per_gain'] = (highest_prices[symbol]['price'] - ask_av_price) / ask_av_price * 100

    return {'highest_prices': highest_prices, 'lowest_prices': lowest_prices}

# Tabulate the prices data structure and print it
def tabulate_prices(price_diff):
    table = []
    for symbol in all_symbols:
        if symbol in price_diff['highest_prices']:
            per_gain = price_diff['lowest_prices'][symbol]['per_gain']
            if per_gain < minimal_profit or per_gain > max_profit :
                continue
            table.append([symbol, 
                          price_diff['lowest_prices'][symbol]['exchange'], 
                          price_diff['lowest_prices'][symbol]['price'], 
                          price_diff['highest_prices'][symbol]['exchange'], 
                          price_diff['highest_prices'][symbol]['price'], 
                          price_diff['highest_prices'][symbol]['available_amount'], 
                          price_diff['lowest_prices'][symbol]['per_gain']])
    
    if len(table) > 0:
        table = sorted(table, key=lambda x: x[1])
        logger.info(tabulate(table, headers = headers))
    
    return table
    
# Fetch the ticker for a given exchange and symbol, call parallelly using ThreadPoolExecutor
def fetch_ticker(exchange, symbol):
    try:
        orderbook = exchange.fetch_order_book(symbol)

        # Update the prices data structure
        prices[exchange.id][symbol]['bids'] = orderbook['bids'] if len(orderbook['bids']) > 0 else None
        prices[exchange.id][symbol]['asks'] = orderbook['asks'] if len(orderbook['asks']) > 0 else None

    except Exception as e:
            if 'does not have market symbol' not in str(e):
                logger.warning(f'Error fetching ticker for {exchange.name} {symbol}: {e}')



def main():
    with ThreadPoolExecutor(max_workers=32) as executor:
        while(True):
            starttime = time.time()
            # Create a list of all possible combinations of exchanges and symbols randomly. Calling exchanges randomically to avoid ban.
            combinations = [(exchange, pair) for exchange in exchange_objs for pair in symbols[exchange.id]]
            random.shuffle(combinations)

            tasks = [executor.submit(fetch_ticker, c[0], c[1]) for c in combinations]
            for task in tasks:
                task.result()
            dff = calculate_max_min(prices)
            tabulate_prices(dff)
            logger.info(f'Execution time: {time.time() - starttime}\n')
            quit()


if __name__ == "__main__":
    main()