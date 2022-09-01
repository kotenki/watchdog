import time
import logging
import telebot
from keys import TG_API_KEY
import sqlite3 as sl
from pycoingecko import CoinGeckoAPI
import help
import sql.update_query
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
        update_query("pricelog", "price_old", "price_new", "token = '" + supported_tokens[key] + "'")
        update_query("pricelog", "price_new", str(prices_data[key]["usd"]), "token = '" + supported_tokens[key] + "'" )
        conn.commit()


while True:
    data = get_prices()
    logging.debug(data)
    update_price_log(data)

    alerts = vki.select_query("alerts", "target_price IS NOT NULL")

    for a in alerts: 
        alert_id, chat_id, token = a[0], a[1], a[2]
        token_price_log = vki.select_query("pricelog", "token = '" + token + "'")
        price_old, price_new, price_target = token_price_log[0][1], token_price_log[0][2], a[3]
        

        if help.price_crossed(price_old, price_new, price_target):
            if help.price_increased(price_old, price_new):
                direction = "has increased to"
            else:
                direction = "has dropped to"

            bot.send_message(chat_id, token + " price " + direction + " " + str(price_new) + " USD")
            logging.debug("Alert #" + str(alert_id) + " sent")
            vki.delete_query("alerts", "id = " + str(alert_id))
            logging.debug("Alert #" + str(alert_id) + " removed")

    time.sleep(10)