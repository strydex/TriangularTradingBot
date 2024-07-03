import time

from binance_parser.api import pair_names
from binance_parser.websoket import tickers

if __name__ == '__main__':
    while True:
        tickers.ws.run_forever()
        time.sleep(1800)
        tickers.ws.close()
