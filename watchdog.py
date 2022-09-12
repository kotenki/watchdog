import time
import logging
#logging.basicConfig(filename="watchdog.log", level=logging.DEBUG, format="%(asctime)s %(message)s", filemode="w")
import telebot
from keys import TG_API_KEY
#import sqlite3 as sl
from pycoingecko import CoinGeckoAPI
from help import *
from constants import *
import database as db
from datetime import datetime
#from watchbot import shift_sequence

bot = telebot.TeleBot(TG_API_KEY)


conn = db.connect()
db.create_tables(conn)

# TO BE REFACTORED: 
def shift_sequence(conn, chat_id, sequence):
    shift_increment = 0
    alerts_shift_sequence = db.get_alerts_shift_sequence(conn, chat_id, sequence)

    for a in alerts_shift_sequence:
        db.alert_shift_sequence(conn, int(sequence) + shift_increment, a[0])
        shift_increment += 1

for item in supported_tokens.items():
    db.add_empty_token_row(conn, item[1])

cg = CoinGeckoAPI()

def get_prices():
    tokens_string = ", ".join(supported_tokens.keys())
    return cg.get_price(ids=tokens_string.lower(), vs_currencies="usd")

def set_prices(prices_data):
    for key in prices_data:
        token = supported_tokens[key.upper()]
        price = db.get_price(conn, token)[0]

        db.set_old_price(conn, price, token)

        db.set_price(conn, str(prices_data[key]["usd"]), token)


while True:
    set_prices(get_prices())

    alerts = db.get_active_alerts(conn)

    for a in alerts:
        alert_id, chat_id, token, target, sequence = a[0], a[1], a[2], a[3], a[4]

        token_price_log = db.get_pricelog_by_token(conn, token)
        price_old, price_new = token_price_log[0][1], token_price_log[0][2]
        

        if price_crossed(price_old, price_new, target):
            if price_increased(price_old, price_new):
                direction = "has increased to"
                circle_emoji = "\U0001F7E2"
            else:
                direction = "has dropped to"
                circle_emoji = "\U0001F534"

            msg = token + " price " + direction + " " + str(price_new) + "$"
            bot.send_message(chat_id, circle_emoji + " " + msg)

            db.add_alertlog(conn, alert_id, chat_id, target, msg, datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            db.del_alert_by_id(conn, str(alert_id))
            shift_sequence(conn, chat_id, sequence)

    time.sleep(10)