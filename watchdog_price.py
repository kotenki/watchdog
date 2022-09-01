import time
import logging
import telebot
from keys import TG_API_KEY
import sqlite3 as sl
from pycoingecko import CoinGeckoAPI
from help import *
from sql import *
from config import *

bot = telebot.TeleBot(TG_API_KEY)
logging.basicConfig(filename="debug.log", level=logging.DEBUG, format="%(asctime)s %(message)s", filemode="w")
conn = sl.connect("watchdog.db")
c = conn.cursor()
cg = CoinGeckoAPI()


def get_prices():
    tokens = "bitcoin, cosmos, polkadot"
    return cg.get_price(ids=tokens, vs_currencies="usd")


def update_price_log(prices_data):
    for key in prices_data:
        c.execute(update_query("pricelog", "price_old", "price_new", "token = '" + supported_tokens[key] + "'"))
        c.execute(update_query("pricelog", "price_new", str(prices_data[key]["usd"]), "token = '" + supported_tokens[key] + "'" ))
        conn.commit()


while True:
    data = get_prices()
    logging.debug(data)
    update_price_log(data)

    c.execute(select_query("alerts", "target_price IS NOT NULL"))
    alerts = c.fetchall()

    for a in alerts:
        alert_id, chat_id, token = a[0], a[1], a[2]
        c.execute(select_query("pricelog", "token = '" + token + "'"))
        token_price_log = c.fetchall()
        price_old, price_new, price_target = token_price_log[0][1], token_price_log[0][2], a[3]
        

        if price_crossed(price_old, price_new, price_target):
            if price_increased(price_old, price_new):
                direction = "has increased to"
            else:
                direction = "has dropped to"

            bot.send_message(chat_id, token + " price " + direction + " " + str(price_new) + " $")
            logging.debug("Alert #" + str(alert_id) + " sent")
            c.execute(delete_query("alerts", "id = " + str(alert_id)))
            conn.commit()
            logging.debug("Alert #" + str(alert_id) + " removed")

    time.sleep(10)