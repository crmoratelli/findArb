"""
    This script will fetch all trading pairs from all exchanges in the list.

    The list of exchanges is in the utils.py file.
"""
import ccxt
from utils import exchanges
import json, sys

config_file = sys.argv[1]

with open(config_file, 'r') as file:
    configs = json.load(file)

def get_trading_pairs(exchange_name):
    exchange = getattr(ccxt, exchange_name)()
    markets = exchange.load_markets()
    trading_pairs = [symbol.split(":")[0] for symbol in markets.keys()]
    return trading_pairs

def main():
    blacklist = [item['coin'] for item in configs['black_list']]
    exclude = configs['exclude']
    exclude.extend(blacklist)
    exclude = list(set(exclude))    

    pairs = {}
    for exchange_name in exchanges:
        print(f"Trading pairs for {exchange_name}:")
        try:
            trading_pairs = get_trading_pairs(exchange_name)
            pairs[exchange_name] = [item for item in trading_pairs if not any(substring in item for substring in exclude)]
        except Exception as e:
            print(f"Error fetching trading pairs for {exchange_name}: {e}")

    with open(configs['file_pairs'], 'w') as file:
        json.dump(pairs, file, indent=4)

if __name__ == '__main__':
    main()
