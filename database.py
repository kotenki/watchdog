import sqlite3


CREATE_TABLE_ALERTS = "CREATE TABLE IF NOT EXISTS alerts (id INTEGER PRIMARY KEY, chat_id INTEGER, username TEXT, token TEXT NOT NULL, target_price INTEGER, sequence_id INTEGER, UNIQUE (chat_id, token, target_price));"
CREATE_TABLE_PREALERTS = "CREATE TABLE IF NOT EXISTS prealerts (id INTEGER PRIMARY KEY, chat_id INTEGER, token TEXT, state INTEGER);"
CREATE_TABLE_PRICELOG = "CREATE TABLE IF NOT EXISTS pricelog (token TEXT PRIMARY_KEY, price_old REAL, price_new REAL);"
CREATE_TABLE_ALERTSLOG = "CREATE TABLE IF NOT EXISTS alertslog (id INTEGER, chat_id INTEGER, username TEXT, token TEXT NOT NULL, target_price INTEGER, msg TEXT, time TEXT);"

GET_PREALERT_TOKEN_BY_CHAT_ID_AND_STATE = "SELECT token FROM prealerts WHERE chat_id = ? AND state = ?;"
GET_PRICE_NEW_BY_TOKEN = "SELECT price_new FROM pricelog WHERE token = ?;"
GET_ALERTS_BY_TARGET_PRICE_NOT_NULL = "SELECT * FROM alerts WHERE target_price IS NOT NULL;"
GET_PRICELOG_BY_TOKEN = "SELECT * FROM pricelog WHERE token = ?;"
GET_ALERTS_BY_CHAT_ID = "SELECT * FROM alerts WHERE chat_id = ? ORDER BY sequence_id;"
GET_PREALERT_WITH_STATE_1 = "SELECT * FROM prealerts where chat_id = ? and state = 1;"
GET_ALL_CHATS = "SELECT DISTINCT chat_id FROM alertslog;"
GET_MAX_SEQUENCE_ID_BY_CHAT_ID = "SELECT IFNULL(MAX(sequence_id), 0) sequence_id FROM alerts WHERE chat_id = ?;"


SET_PRICE_OLD_TO_PRICE_NEW_BY_TOKEN = "UPDATE pricelog SET price_old = price_new WHERE token = ?;"
SET_PRICE_NEW_BY_TOKEN = "UPDATE pricelog SET price_new = ? WHERE token = ?;"
SET_PREALERT_STATE_2 = "UPDATE prealerts SET token = ?, state = 2 WHERE chat_id = ? AND state = 1;"

DEL_ALERT_BY_ID = "DELETE FROM alerts WHERE id = ?;"
DEL_PREALERT_BY_CHAT_ID_STATE = "DELETE FROM prealerts WHERE chat_id = ? AND state = ?;"
DEL_PREALERTS_BY_CHAT_ID = "DELETE FROM prealerts WHERE chat_id = ? AND state in (1, 2);"

ADD_ALERT = "INSERT INTO alerts (chat_id, username, token, target_price, sequence_id) VALUES (?, ?, ?, ?, ?);"
ADD_PREALERT = "INSERT INTO prealerts (chat_id, state) VALUES (?, ?);"
ADD_EMPTY_TOKEN_ROW = "INSERT INTO pricelog VALUES (?, 0, 0);"
ADD_ALERTLOG = "INSERT INTO alertslog VALUES (?, ?, ?, ?, ?, ?, ?)"

def connect():
    return sqlite3.connect("data.db", check_same_thread=False)


def create_tables(connection):
    with connection:
        connection.execute(CREATE_TABLE_ALERTS)
        connection.execute(CREATE_TABLE_PREALERTS)
        connection.execute(CREATE_TABLE_PRICELOG)
        connection.execute(CREATE_TABLE_ALERTSLOG)


def add_empty_token_row(connection, token):
    with connection:
        connection.execute(ADD_EMPTY_TOKEN_ROW, (token,))


def get_prealert_token_by_chat_id_and_state(connection, chat_id, state):
    with connection:
        return connection.execute(GET_PREALERT_TOKEN_BY_CHAT_ID_AND_STATE, (chat_id, state)).fetchall()


# change to get_pricelog_by_token
def get_price_new_by_token(connection, token):
    with connection:
        return connection.execute(GET_PRICE_NEW_BY_TOKEN, (token,)).fetchall()


def get_alerts_by_target_price_not_null(connection):
    with connection:
        return connection.execute(GET_ALERTS_BY_TARGET_PRICE_NOT_NULL).fetchall()


def get_pricelog_by_token(connection, token):
    with connection:
        return connection.execute(GET_PRICELOG_BY_TOKEN, (token,)).fetchall()


def set_price_old_to_price_new_by_token(connection, token):
    with connection:
        connection.execute(SET_PRICE_OLD_TO_PRICE_NEW_BY_TOKEN, (token,))
 

def set_price_new_by_token(connection, price_new, token):
    with connection:
        connection.execute(SET_PRICE_NEW_BY_TOKEN, (price_new, token))
 

def add_prealert(connection, chat_id, state):
    with connection:
        connection.execute(ADD_PREALERT, (chat_id, state))


def del_alert_by_id(connection, id):
    with connection:
        connection.execute(DEL_ALERT_BY_ID, (id,))


def del_prealert_by_chat_id_state(connection, chat_id, state):
    with connection:
        connection.execute(DEL_PREALERT_BY_CHAT_ID_STATE, (chat_id, state))


def set_prealert_state_2(connection, token, chat_id):
    with connection:
        connection.execute(SET_PREALERT_STATE_2, (token, chat_id))

def add_alert(connection, chat_id, username, token, target_price, sequence_id):
    with connection:
        connection.execute(ADD_ALERT, (chat_id, username, token, target_price, sequence_id))

def add_alertlog(connection, id, chat_id, username, token, target_price, msg, time):
    with connection:
        connection.execute(ADD_ALERTLOG, (id, chat_id, username, token, target_price, msg, time))


def del_prealerts_by_chat_id(connection, chat_id):
    with connection:
        connection.execute(DEL_PREALERTS_BY_CHAT_ID, (chat_id,))


def get_alerts_by_chat_id(connection, chat_id):
    with connection:
        return connection.execute(GET_ALERTS_BY_CHAT_ID, (chat_id,)).fetchall()


def get_prealert_with_state_1(connection, chat_id):
    with connection:
        return connection.execute(GET_PREALERT_WITH_STATE_1, (chat_id,)).fetchall()


def get_all_chats(connection):
    with connection:
        return connection.execute(GET_ALL_CHATS).fetchall()


def get_max_sequence_id_by_chat_id(connection, chat_id):
    with connection:
        return connection.execute(GET_MAX_SEQUENCE_ID_BY_CHAT_ID, (chat_id,)).fetchall()

