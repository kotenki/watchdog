import time
import logging
import sqlite3 as sl
import telebot
from pycoingecko import CoinGeckoAPI
from keys import TG_API_KEY

bot = telebot.TeleBot(TG_API_KEY)
logging.basicConfig(filename="debug.log", level=logging.DEBUG, format="%(asctime)s %(message)s", filemode="w")
conn = sl.connect("watchdog.db")
c = conn.cursor()
tokens_dict = {"bitcoin": "BTC", "cosmos": "ATOM", "polkadot": "DOT"}
cg = CoinGeckoAPI()

def get_prices():
    tokens = "bitcoin, cosmos, polkadot"
    return cg.get_price(ids=tokens, vs_currencies="usd")


def update_price_log(prices_data): 
    for key in prices_data:
        update_query("pricelog", "price_old", "price_new", "token = '" + tokens_dict[key] + "'")
        update_query("pricelog", "price_new", str(prices_data[key]["usd"]), "token = '" + tokens_dict[key] + "'" )
        conn.commit()

def delete_query(table, condition):
    c.execute("DELETE FROM " + table + " WHERE " + condition)
    conn.commit() 


def select_query(table, condition): 
    c.execute("SELECT * FROM " + table + " WHERE " + condition)
    return c.fetchall()


def update_query(table, column, value, condition):
    c.execute("UPDATE " + table + " SET " + column + " = " + value + " WHERE " + condition)


def price_crossed(old, new, target):
    if (old <= target <= new) or (new <= target < old):
        return True
    else:
        return False


def price_increased(old, new):
    if new > old: 
        return True
    else:
        return False


while True:
    data = get_prices()
    logging.debug(data)
    update_price_log(data)

    alerts = select_query("alerts", "target_price IS NOT NULL")

    for a in alerts: 
        alert_id, chat_id, token = a[0], a[1], a[2]
        token_price_log = select_query("pricelog", "token = '" + token + "'")
        price_old, price_new, price_target = token_price_log[0][1], token_price_log[0][2], a[3]
        

        if price_crossed(price_old, price_new, price_target):
            if price_increased(price_old, price_new):
                direction = "has increased to"
            else:
                direction = "has dropped to"

            bot.send_message(chat_id, token + " price " + direction + " " + str(price_new) + " USD")
            logging.debug("Alert #" + str(alert_id) + " sent")
            delete_query("alerts", "id = " + str(alert_id))
            logging.debug("1Alert #" + str(alert_id) + " removed")

    time.sleep(10)