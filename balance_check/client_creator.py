from binance import Client
from balance_check import config
import time

client = Client(config.binance_api_key, config.binance_secret_key)
