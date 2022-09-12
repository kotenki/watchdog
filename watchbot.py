from keys import TG_API_KEY
import telebot
import database as db
from help import *
from constants import *
#import logging
#logging.basicConfig(filename="bot.log", level=logging.DEBUG, format="%(asctime)s %(message)s", filemode="w")

bot = telebot.TeleBot(TG_API_KEY)
conn = db.connect()


def shift_sequence(conn, chat_id, sequence):
    shift_increment = 0
    alerts_shift_sequence = db.get_alerts_shift_sequence(conn, chat_id, sequence)

    for a in alerts_shift_sequence:
        db.alert_shift_sequence(conn, int(sequence) + shift_increment, a[0])
        shift_increment += 1


@bot.message_handler(commands=["add"])
def add(msg):
    chat_id = msg.chat.id
    if db.get_user_by_chatid(conn, msg.chat.id) == None:
        db.add_user(conn, chat_id, msg.from_user.username, user_states["add"])
    else:
        db.set_state_for_user(conn, chat_id, user_states["add"])
    
    inactive_alert_id = db.get_inactive_alert_by_chatid(conn, chat_id)
    
    if inactive_alert_id is not None:
        db.del_alert_by_id(conn, inactive_alert_id[0])

    sequence = db.get_max_sequence_by_chatid(conn, chat_id)[0] + 1
    db.add_alert(conn, chat_id, None, None, sequence, alert_states["inactive"])

    bot.send_message(chat_id, "Which token you would like to be alerted on, e.g. BTC, ATOM")

    return None
  

@bot.message_handler(commands=["delete"])
def delete(msg):

    chat_id = msg.chat.id
    alerts(msg)

    db.set_state_for_user(conn, chat_id, user_states["delete"])
    bot.send_message(msg.chat.id, "Which alert number do you want to delete?")

    return None


@bot.message_handler(commands=["alerts"])
def alerts(msg):
    chat_id = msg.chat.id

    alerts = db.get_active_alerts_by_chatid(conn, chat_id)

    alerts_string = "" 

    for a in alerts:
        alerts_string += str(a[4]) + ". " + a[2] + ": " + str(a[3]) + "$" + "\n"

    if len(alerts_string) == 0: 
       bot.send_message(chat_id, "No alerts yet created!")
    else:  
        bot.send_message(chat_id, alerts_string)    

    return None


@bot.message_handler(regexp = "[a-zA-Z]")
def input_text(msg):
    chat_id = msg.chat.id
    user_state = db.get_user_by_chatid(conn, chat_id)[2]

    if user_state != user_states["add"]:
        bot.send_message(chat_id, "Use /add command to add a new alert")
        return None

    # if token not supported -> reply "Token not supported"
    token = msg.text.upper()
    last_price = db.get_price(conn, token)

    # !!! Add exception handling:
    #    last_price = db.get_price(conn, token)[0]
    # TypeError: 'NoneType' object is not subscriptable
    
    # if last_price == -1:
    if last_price == None:
       bot.send_message(chat_id, "Token " + token + " is not supported")
       return None

    inactive_alert_id = db.get_inactive_alert_by_chatid(conn, chat_id)[0]

    db.set_alert_token(conn, token, inactive_alert_id)
    db.set_state_for_user(conn, chat_id, user_states["add-token"])

    bot.send_message(chat_id, "Current " + token + " price: " + str(last_price[0]) + "$")
    bot.send_message(chat_id, 'Which price would you like to be notified on?')

    return None

@bot.message_handler(regexp = "[0-9]")
def input_numbers(msg):
    chat_id = msg.chat.id
    user_state = db.get_user_by_chatid(conn, chat_id)[2]

    if float(msg.text) <= 0: 
        bot.send_message(chat_id, 'Please type a positive number')
        return None

    if user_state == user_states["delete"]:
        sequence = msg.text
        db.del_alerts_by_chatid_and_sequence(conn, chat_id, sequence)
        db.set_state_for_user(conn, chat_id, user_states["default"])
        bot.send_message(chat_id, 'Alert removed!')
        shift_sequence(conn, chat_id, sequence)

    elif user_state == user_states["add-token"]:
        price = msg.text
        inactive_alert_id = db.get_inactive_alert_by_chatid(conn, chat_id)[0]
        try: 
            db.set_alert_price(conn, price, inactive_alert_id)
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                bot.send_message(chat_id, 'You already have an alert with these parameters!')
                return None

        db.set_alert_state(conn, alert_states["active"], inactive_alert_id)
        db.set_state_for_user(conn, chat_id, user_states["default"])

        bot.send_message(msg.chat.id, 'Alert created!')

    else:
        bot.send_message(msg.chat.id, "Use /add command to add a new alert")
    
    return None
   
# bot.polling()
# requests.exceptions.ReadTimeout: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=25)

bot.infinity_polling(timeout=25, long_polling_timeout = 5)