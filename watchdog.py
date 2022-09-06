import time
import logging
import telebot
from keys import TG_API_KEY
import sqlite3 as sl
from pycoingecko import CoinGeckoAPI
from help import *
from config import *
import database
from datetime import datetime

bot = telebot.TeleBot(TG_API_KEY)
logging.basicConfig(filename="watchdog.log", level=logging.DEBUG, format="%(asctime)s %(message)s", filemode="w")

connection = database.connect()

database.create_tables(connection)

for item in supported_tokens.items():
    database.add_empty_token_row(connection, item[1])


cg = CoinGeckoAPI()


def get_prices():
    tokens_string = ", ".join(supported_tokens.keys())
    return cg.get_price(ids=tokens_string.lower(), vs_currencies="usd")



def update_price_log(prices_data):
    for key in prices_data:
        try:
            database.set_price_old_to_price_new_by_token(connection, supported_tokens[key.upper()])
        except Exception as e: 
            logging.debug("Exception in set_price_old_to_price_new_by_token :" + str(e))

        database.set_price_new_by_token(connection, str(prices_data[key]["usd"]), supported_tokens[key.upper()])
        connection.commit()


while True:
    data = get_prices()
    update_price_log(data)

    alerts = database.get_alerts_by_target_price_not_null(connection)

    for a in alerts:
        alert_id, chat_id, username, token = a[0], a[1], a[2], a[3]
        token_price_log = database.get_pricelog_by_token(connection, token)
        price_old, price_new, price_target = token_price_log[0][1], token_price_log[0][2], a[4]
        

        if price_crossed(price_old, price_new, price_target):
            if price_increased(price_old, price_new):
                direction = "has increased to"
                circle_emoji = "\U0001F7E2"
            else:
                direction = "has dropped to"
                circle_emoji = "\U0001F534"

            msg = token + " price " + direction + " " + str(price_new) + " $"
            bot.send_message(chat_id, circle_emoji + " " + msg)
            database.add_alertlog(connection, alert_id, chat_id, username, token, price_target, msg, datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            try:
                database.del_alert_by_id(connection, str(alert_id))
            except: 
                logging.debug("Exception when deleting alert")
            connection.commit()

    time.sleep(10)