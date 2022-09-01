import sqlite3 as sl
from keys import TG_API_KEY
import telebot
import sql

#import logging
#logging.basicConfig(filename="bot.log", level=logging.DEBUG, format="%(asctime)s %(message)s", filemode="w")

bot = telebot.TeleBot(TG_API_KEY)
conn = sl.connect('watchdog.db', check_same_thread=False)
c = conn.cursor()




@bot.message_handler(commands=["start"])
def start(msg):
    bot.send_message(msg.chat.id, 'Send me the token which you would like to be alerted on, e.g. BTC or ATOM')
    c.execute("DELETE FROM prealerts WHERE chat_id = " + str(msg.chat.id) + " AND state in (1, 2)")
    c.execute("INSERT INTO prealerts (chat_id, state) values (" + str(msg.chat.id) + ", " + "1" + ")")
    conn.commit()


@bot.message_handler(regexp = "[a-zA-Z]")
def parse_token(msg):
    #if token exist in the dict
    c.execute("UPDATE prealerts SET token = '" + msg.text + "'" + ", state = 2 WHERE chat_id = " + str(msg.chat.id) + " AND state = 1")
    c.execute("SELECT price_new FROM pricelog WHERE token = '" + msg.text + "'")
    current_price = c.fetchall()[0][0]
    bot.send_message(msg.chat.id, "Current " + msg.text + " price: " + str(current_price) + "$")
    bot.send_message(msg.chat.id, 'Which price would you like to be notified on?')


@bot.message_handler(regexp = "[0-9]")
def parse_price(msg):
    # if token not null and state = 2
    bot.send_message(msg.chat.id, 'Got it')
    data = c.execute("SELECT token FROM prealerts WHERE chat_id = " + str(msg.chat.id) + " AND state = 2") 
    token = data.fetchall()[0][0]
    c.execute("INSERT INTO alerts (chat_id, token, target_price) values (" + str(msg.chat.id) + ", '" + token + "', " + msg.text + ")")
    c.execute("DELETE FROM prealerts WHERE chat_id = " + str(msg.chat.id) + " AND state in (1, 2)")
    conn.commit()

#@bot.message_handler(func=lambda msg: True)
#def parse_price(msg):
#    #regexp to accept only digits 
#    #check if the same alert exists
#    #add alert to the database 
#    message = msg
#    

bot.polling()
