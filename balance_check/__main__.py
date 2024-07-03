import time
from balance_check import client_creator
from balance_check.config import redis

if __name__ == '__main__':
    account_data = client_creator.client.get_account()
    for asset in account_data["balances"]:
        if float(asset["free"]) > 0:
            print(asset)




