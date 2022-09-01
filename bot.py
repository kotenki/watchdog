import sqlite3 as sl
from keys import TG_API_KEY
import telebot

#import logging
#logging.basicConfig(filename="bot.log", level=logging.DEBUG, format="%(asctime)s %(message)s", filemode="w")

bot = telebot.TeleBot(TG_API_KEY)
conn = sl.connect('watchdog.db', check_same_thread=False)
c = conn.cursor()

prealerts = {}


@bot.message_handler(commands=["start"])
def start(msg):
    bot.send_message(msg.chat.id, 'Send me the token which you would like to be alerted on, e.g. BTC or ATOM')
    #prealerts[1 = dict["chat_id" = msg.chat.id, "token" = "" ]]


@bot.message_handler(regexp = "[a-zA-Z]")
def parse_token(msg):
    #if token exist in the dict
    token = msg.text
    bot.send_message(msg.chat.id, 'Which price would you like to be notified on?')
    state = 2


@bot.message_handler(regexp = "[0-9]")
def parse_price(msg):
    # if token not null and state = 2
    global token
    bot.send_message(msg.chat.id, 'Got it')
    c.execute("INSERT INTO alerts (chat_id, token, target_price) values (" + str(msg.chat.id) + ", " + token + ", " + msg.text) + ")" 
    state = 3

#@bot.message_handler(func=lambda msg: True)
#def parse_price(msg):
#    #regexp to accept only digits 
#    #check if the same alert exists
#    #add alert to the database 
#    message = msg
#    

bot.polling()
