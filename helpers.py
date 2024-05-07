
def average_asset_price_with_gain(orderbook_a, orderbook_b, maximal_quote, min_percentage_gain):
    # Sort the order books by price ascending for orderbook_a (asks) and descending for orderbook_b (bids)
    orderbook_a = sorted(orderbook_a['asks'], key=lambda x: x[0])
    orderbook_b = sorted(orderbook_b['bids'], key=lambda x: x[0], reverse=True)

    #Some exchange delivery a third element in the orderbook, which is not needed
    if len(orderbook_a[0]) > 2:
        orderbook_a = [order[:2] for order in orderbook_a]

    if len(orderbook_b[0]) > 2:
        orderbook_b = [order[:2] for order in orderbook_b]

    # Initialize variables
    total_amount = 0
    total_asset = 0

    # Iterate through both order books simultaneously
    a_idx, b_idx = 0, 0
    ask_price, ask_quantity = orderbook_a[a_idx]
    bid_price, bid_quantity = orderbook_b[b_idx]
    ask_av_price = ask_price
    bid_av_price = bid_price

    while True:
        # Calculate the percentage gain for the current trade
        percentage_gain = (bid_av_price - ask_av_price) / ask_av_price * 100

        # If the percentage gain is less than the minimum percentage gain or ask price is greater than the bid price,
        # there is no valid trade
        if percentage_gain < min_percentage_gain or maximal_quote <= total_amount:
            break

        # Calculate the tradeable amount of the asset
        trade_amount = min(ask_quantity, bid_quantity)

        if (ask_av_price * total_asset + trade_amount * ask_price) > maximal_quote:
            trade_amount = (maximal_quote - ask_av_price * total_asset) / ask_price

        if trade_amount <= 0:
            break

        ask_av_price = (ask_av_price * total_asset + trade_amount * ask_price) / (total_asset + trade_amount)
        bid_av_price = (bid_av_price * total_asset + trade_amount * bid_price) / (total_asset + trade_amount)

        # Update the total price and total asset
        total_amount += trade_amount * ask_price
        total_asset += trade_amount

        # Update the quantities in the order books
        ask_quantity -= trade_amount
        bid_quantity -= trade_amount

        # Update the indices if the quantities are depleted
        if ask_quantity == 0:
            a_idx += 1
            if a_idx == len(orderbook_a):
                break
            ask_price, ask_quantity = orderbook_a[a_idx]

        if bid_quantity == 0:
            b_idx += 1
            if b_idx == len(orderbook_b):
                break
            bid_price, bid_quantity = orderbook_b[b_idx]

    return total_amount, total_asset, ask_av_price, bid_av_price
