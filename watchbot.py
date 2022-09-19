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
    if db.get_user_by_chatid(conn, msg.chat.id) is None:
        db.add_user(conn, chat_id, msg.from_user.username, user_states["add"])
    else:
        db.set_state_for_user(conn, chat_id, user_states["add"])
    
    inactive_alert_id = db.get_inactive_alert_by_chatid(conn, chat_id)
    
    if inactive_alert_id is not None:
        db.del_alert_by_id(conn, inactive_alert_id[0])

    sequence = db.get_max_sequence_by_chatid(conn, chat_id)[0] + 1
    db.add_alert(conn, chat_id, None, None, sequence, alert_states["inactive"])

    bot.send_message(chat_id, "О цене какого токена добавить уведомление? Например, BTC, ATOM или другие.")

    return None
  

@bot.message_handler(commands=["delete"])
def delete(msg):

    chat_id = msg.chat.id
    alerts_string = alerts(msg)

    if len(alerts_string) != 0: 
        db.set_state_for_user(conn, chat_id, user_states["delete"])
        bot.send_message(msg.chat.id, "Какое по счету уведомление удалить? Например, 1. ")

    return None


@bot.message_handler(commands=["alerts"])
def alerts(msg):
    chat_id = msg.chat.id

    alerts = db.get_active_alerts_by_chatid(conn, chat_id)

    alerts_string = "" 

    for a in alerts:
        alerts_string += str(a[4]) + ". " + a[2] + ": " + str(a[3]) + "$" + "\n"

    if len(alerts_string) == 0: 
        bot.send_message(chat_id, "У вас пока нет активных уведомлений.")
        bot.send_message(chat_id, "Используйте команду /add чтобы создать новое уведомление.")
        bot.send_message(chat_id, "Либо, пришлите название токена и цену в одном сообщении. Например, btc 25500")
    else:  
        bot.send_message(chat_id, alerts_string)    

    return alerts_string

# Input: btc 20000
@bot.message_handler(regexp = "[a-zA-Z]+\s+[0-9]+")
def quick_command_token_price(msg):
    chat_id = msg.chat.id
    input_list = msg.text.upper().split()

    token, target = input_list[0], input_list[1]

    if db.get_price(conn, token) is None: 
        bot.send_message(chat_id, "Токен " + token + " еще не поддержан.")
        return None 

    if float(target) <= 0:
        bot.send_message(chat_id, 'Цена должна быть положительной. Попробуйте еще раз.')
        return None

    db.del_inactive_alerts_by_chatid(conn, chat_id)
    sequence = db.get_max_sequence_by_chatid(conn, chat_id)[0] + 1
    try: 
        db.add_alert(conn, chat_id, token, target, sequence, alert_states["active"])
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            bot.send_message(chat_id, 'У вас уже есть уведомление с такими параметрами!')
            return None
    
    db.set_state_for_user(conn, chat_id, user_states["default"])
    bot.send_message(msg.chat.id, 'Уведомление добавлено!')


@bot.message_handler(regexp = "[a-zA-Zа-яА-Я]")
def input_text(msg):
    chat_id = msg.chat.id
    user_state = db.get_user_by_chatid(conn, chat_id)[2]

    token = msg.text.upper()

    last_price = db.get_price(conn, token)

    #if last_price is None:
    #    last_price = db.get_price(conn, supported_tokens[token])

    if user_state == user_states["default"]:
        if last_price is not None:
            bot.send_message(chat_id, "Текущая цена " + token + ": " + str(last_price[0]) + "$")
            bot.send_message(chat_id, "Используйте команду /add чтобы создать новое уведомление.")
            bot.send_message(chat_id, "Либо, пришлите название токена и цену в одном сообщении. Например, btc 25500")
        else: 
            bot.send_message(chat_id, "Токен " + token + " еще не поддержан.")

    elif user_state == user_states["add-token"]:
        bot.send_message(chat_id, "Цена должна быть положительной. Попробуй еще раз.")
        db.set_state_for_user(conn, chat_id, user_states["default"])

    elif user_state == user_states["delete"]:
        bot.send_message(chat_id, "Некорректный номер. Попробуйте еще раз.")
        db.set_state_for_user(conn, chat_id, user_states["default"])

    elif user_state == user_states["add"]:
        if last_price is not None:
            inactive_alert_id = db.get_inactive_alert_by_chatid(conn, chat_id)[0]

            db.set_alert_token(conn, token, inactive_alert_id)
            db.set_state_for_user(conn, chat_id, user_states["add-token"])

            bot.send_message(chat_id, "Текущая цена " + token + ": " + str(last_price[0]) + "$")
            bot.send_message(chat_id, 'О какой цене (в $) вас уведомить?')

        else:
            bot.send_message(chat_id, "Токен " + token + " не поддерживается.")

    else:    
        bot.send_message(chat_id, "Используйте команду /add чтобы создать новое уведомление.")
        bot.send_message(chat_id, "Либо, пришлите название токена и цену в одном сообщении. Например, btc 25500")

    return None

@bot.message_handler(regexp = "[0-9]")
def input_numbers(msg):
    chat_id = msg.chat.id
    user_state = db.get_user_by_chatid(conn, chat_id)[2]

    if float(msg.text) <= 0: 
        bot.send_message(chat_id, 'Введено некорректное число. Попробуйте еще раз.')
        return None

    if user_state == user_states["delete"]:
        sequence = msg.text

        if db.get_active_alert_by_chatid_sequence(conn, chat_id, sequence) is None: 
            bot.send_message(chat_id, 'Введите порядковый номер уведомления из списка выше. Например, 1.')
            return None 

        db.del_alerts_by_chatid_and_sequence(conn, chat_id, sequence)
        db.set_state_for_user(conn, chat_id, user_states["default"])
        shift_sequence(conn, chat_id, sequence)
        bot.send_message(chat_id, 'Уведомление удалено.')

    elif user_state == user_states["add-token"]:
        price = msg.text
        inactive_alert_id = db.get_inactive_alert_by_chatid(conn, chat_id)[0]
        try: 
            db.set_alert_price(conn, price, inactive_alert_id)
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                bot.send_message(chat_id, 'У вас уже есть уведомление с такими параметрами!')
                return None

        db.set_alert_state(conn, alert_states["active"], inactive_alert_id)
        db.set_state_for_user(conn, chat_id, user_states["default"])

        bot.send_message(msg.chat.id, 'Уведомление добавлено!')

    else:
        bot.send_message(msg.chat.id, "Используйте команду /add чтобы создать новое уведомление.")
        bot.send_message(chat_id, "Либо, пришлите название токена и цену в одном сообщении. Например, btc 25500")
    
    return None
   
# bot.polling()
# requests.exceptions.ReadTimeout: HTTPSConnectionPool(host='api.telegram.org', port=443): Read timed out. (read timeout=25)

bot.infinity_polling(timeout=25, long_polling_timeout = 5)