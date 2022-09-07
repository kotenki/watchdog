from keys import TG_API_KEY
import telebot
import logging
import database
from help import token_supported


user_states = {
    "default": 0,
    "add": 1,
    "add-token": 2,
    "add-token-price": 3,
    "delete": 4,
    "delete-id": 5
}


logging.basicConfig(filename="bot.log", level=logging.DEBUG, format="%(asctime)s %(message)s", filemode="w")

bot = telebot.TeleBot(TG_API_KEY)

connection = database.connect()
#database.create_tables(connection)

@bot.message_handler(commands=["add"])
def add(msg):
    bot.send_message(msg.chat.id, 'Send me the token which you would like to be alerted on, e.g. BTC or ATOM')

    database.del_prealerts_by_chat_id(connection, str(msg.chat.id))
    database.add_prealert(connection, str(msg.chat.id), 1)

    connection.commit()


@bot.message_handler(commands=["delete"])
def delete(msg):


    my_alerts(msg)
    bot.send_message(msg.chat.id, "Which alert number do you want to delete?")

    bot.send_message(msg.chat.id, "This command is still under construction...")
    #database.del_prealerts_by_chat_id(connection, str(msg.chat.id))
    #database.add_prealert(connection, str(msg.chat.id), 1)
    return None
    #connection.commit()


#@bot.message_handler(commands=["price"])
#ef add(msg):
#    bot.send_message(msg.chat.id, 'Which token?')

#    database.del_prealerts_by_chat_id(connection, str(msg.chat.id))
#    database.add_prealert(connection, str(msg.chat.id), 1)



@bot.message_handler(commands=["alerts"])
def my_alerts(msg):
    alerts = database.get_alerts_by_chat_id(connection, msg.chat.id)

    alerts_string = "" 

    #index = 0;
    for a in alerts:
    #    index += 1
        alerts_string += str(a[5]) + ". " + a[3] + ": " + str(a[4]) + " $" + "\n"

    if len(alerts_string) == 0: 
       bot.send_message(msg.chat.id, "No alerts yet created!")
    else:  
        bot.send_message(msg.chat.id, alerts_string)    


@bot.message_handler(regexp = "[a-zA-Z]")
def parse_token(msg):

    token = token_supported(msg.text)

    if len(database.get_prealert_with_state_1(connection, msg.chat.id)) == 0:
        bot.send_message(msg.chat.id, 'Oops! You should use /add command to add an alert')
        return None

    try: 
        current_price = database.get_price_new_by_token(connection, token)[0][0]
    except Exception as e:
        bot.send_message(msg.chat.id, "Token " + msg.text + " is not supported. Try again with /add command!")
        return None 
    
    database.set_prealert_state_2(connection, token, str(msg.chat.id))

    bot.send_message(msg.chat.id, "Current " + token + " price: " + str(current_price) + "$")
    bot.send_message(msg.chat.id, 'Which price would you like to be notified on?')


@bot.message_handler(regexp = "[0-9]")
def parse_price(msg):
    # if token not null and state = 2
    # Exception Handling:
    # token = database.get_prealert_token_by_chat_id_and_state(connection, str(msg.chat.id), 2)[0][0]
    # IndexError: list index out of range
    # if out of range exception -> msg "Please use add command if you want yo add a new alert" 
    
    try: 
        token = database.get_prealert_token_by_chat_id_and_state(connection, str(msg.chat.id), 2)[0][0]
    except Exception as e:
        if "list index out of range" in str(e):
            bot.send_message(msg.chat.id, 'Oops! You should use /add command to add an alert')
            return None


    if float(msg.text) <= 0: 
         bot.send_message(msg.chat.id, 'Please type a valid price')
         return None

    try: 
        sequence_id = database.get_max_sequence_id_by_chat_id(connection, msg.chat.id)[0][0] + 1
        database.add_alert(connection, str(msg.chat.id), msg.from_user.username, token, msg.text, sequence_id)
    except Exception as e: 
        if "UNIQUE constraint failed" in str(e):
            bot.send_message(msg.chat.id, 'You already have an alert with these parameters!')
            return None
        
    bot.send_message(msg.chat.id, 'Got it')

    database.del_prealerts_by_chat_id(connection, str(msg.chat.id))

    connection.commit()


bot.polling()
#bot.infinity_polling(timeout=10, long_polling_timeout = 5)