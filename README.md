Binance Triangular Arbitrage Trading Bot
=============================

This is a trading bot that performs arbitrage trading on the Binance cryptocurrency exchange. The bot continuously monitors the order book depth for all available trading pairs on Binance, calculates potential profits from arbitrage trades, and executes trades when a profitable opportunity is found. It also checks the account balance and sends notifications to a Telegram group when a trade is executed.

Requirements
------------

* Python 3.7 or higher
* Redis server
* Binance API key and Secret key
* Telegram Bot tokens
* Telegram `chat_id`
* A little bit of patience :)

Installation
------------

1. Clone the repository:
```bash
git clone https://github.com/strydex/TriangularTradingBot.git
```
2. Create a virtual environment:
```bash
python3 -m venv env
```
3. Activate the virtual environment:
```bash
source env/bin/activate
```
4. Install the required packages:
```bash
pip3 install -r requirements.txt
```
5. Rename the `config.example.py` file to `config.py` and edit it with your Binance API key and secret key, as well as your Telegram chat_id (if you want to receive notifications about trades):
```bash
cp config.example.py config.py
nano config.py
```
- (Optional) You can change variable `USDT_ORDER_SIZE`: The size of each USDT order placed by the bot. Default value is 20.

Then fill your Binance API and SECRET keys in `config.example.py` located in balance_check folder, and rename it to `config.py` as well.

6. Start the Redis server:
```bash
redis-server
```

7. Run the `get_all_coins.py` script to fetch all available trading pairs on Binance and store them in Redis:
```bash
python3 get_all_coins.py
```
8. Start the `depth_check.py` script to monitor the order book depth and calculate potential profits from arbitrage trades:
```bash
python3 depth_check.py
```
9. (Optional) Start the `balance_check.py` script to check the account balance:
```bash
python3 balance_check.py
```
10. (Optional) Set up the systemd services to run the bot as a background service on a Linux system:
```bash
sudo cp binance_parser_bot.service /etc/systemd/system/
sudo cp depth_check.service /etc/systemd/system/
sudo cp search_for_perspective.service /etc/systemd/system/
sudo systemctl enable binance_parser_bot.service
sudo systemctl enable depth_check.service
sudo systemctl enable search_for_perspective.service
sudo systemctl start binance_parser_bot.service
sudo systemctl start depth_check.service
sudo systemctl start search_for_perspective.service
```
Alternitavely, you can use PM2 instead.

Note on Telegram Bot Tokens
--------------------------

The `depth_check.py` script uses a list of bot tokens and selects a different bot for each message sent, in a round-robin fashion. This is to avoid exceeding the rate limit of a single bot. It is recommended to create multiple Telegram bots and add their tokens to the `bot_tokens_list` variable in `depth_check.py`.

To create a Telegram bots and get its tokens, follow these steps:

1. Open Telegram and search for BotFather.
2. Start a chat with BotFather and send the `/newbot` command.
3. Follow the instructions to create a new bot and get its token.
4. Repeat the process to create multiple bots.

After creating the bots, update the `bot_tokens_list` variable in `depth_check.py` with their tokens:
```python
bot_tokens_list = ['TOKEN_1', 'TOKEN_2', 'TOKEN_3', 'TOKEN_4', 'TOKEN_5', 'TOKEN_6', 'TOKEN_7', 'TOKEN_8']
```
Replace `TOKEN_1`, `TOKEN_2`, etc. with your actual bot tokens. You also can use only 1 bot in a list.

Usage
-----

Once the bot is running, it will continuously monitor the order book depth for all available trading pairs on Binance and calculate potential profits from arbitrage trades. When a profitable opportunity is found, the bot will execute the trades and send a notification to your Telegram group.

Contributing
------------

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

License
-------

[GPL-3.0]

Disclaimer
----------

This bot is provided for educational purposes only. The author is not responsible for any losses or damages incurred while using this bot. Use at your own risk.
