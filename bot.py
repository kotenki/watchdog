import sqlite3 as sl
from keys import TG_API_KEY
import telebot

#import logging
#logging.basicConfig(filename="bot.log", level=logging.DEBUG, format="%(asctime)s %(message)s", filemode="w")

bot = telebot.TeleBot(TG_API_KEY)
conn = sl.connect('watchdog.db', check_same_thread=False)
c = conn.cursor()

sql_insert = 'INSERT INTO SUBSCRIPTIONS (chat_id, active) values(?, ?)'
sql_update_activate = 'UPDATE SUBSCRIPTIONS SET active = 1 WHERE chat_id = '
sql_update_deactivate = 'UPDATE SUBSCRIPTIONS SET active = 0 WHERE chat_id = '
sql_select = 'SELECT * FROM SUBSCRIPTIONS WHERE chat_id = '

# Scenario:
step_one = "1"
step_two = "2"



@bot.message_handler(commands=["start"])
def start(msg):
    bot.send_message(msg.chat.id, 'Send me the token which you would like to be alerted on, e.g. BTC or ATOM')


@bot.message_handler(regexp = "[a-zA-Z]")
def parse_token(msg):
    token = msg.text
    print(token)
    #if token exist in the dict
    #send message to type target price 

@bot.message_handler(func=lambda msg: True)
def parse_price(msg):
    #regexp to accept only digits 
    #check if the same alert exists
    #add alert to the database 
    message = msg
    

bot.polling()
