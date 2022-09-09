import sqlite3

CREATE_TABLE_USERS = """CREATE TABLE IF NOT EXISTS users
                        (  
                           chatid INTEGER PRIMARY KEY,
                           username TEXT,
                           state INTEGER
                        )"""


CREATE_TABLE_ALERTS = """CREATE TABLE IF NOT EXISTS alerts
                        (
                            id INTEGER PRIMARY KEY,
                            chatid INTEGER,
                            token TEXT,
                            pricetarget REAL,
                            sequence INTEGER,
                            state INTEGER,
                            FOREIGN KEY (chatid) REFERENCES users (chatid),
                            UNIQUE (chatid, token, pricetarget),
                            UNIQUE (chatid, sequence)
                        )"""


CREATE_TABLE_PRICE = """CREATE TABLE IF NOT EXISTS price
                        (
                            token TEXT PRIMARY_KEY,
                            old REAL, 
                            new REAL
                        )"""


CREATE_TABLE_ALERTSLOG = """CREATE TABLE IF NOT EXISTS alertslog
                            (
                                id INTEGER,
                                chatid INTEGER,
                                pricetarget REAL,
                                message TEXT,
                                time TEXT,
                                FOREIGN KEY(chatid) REFERENCES users(chatid)
                            )"""


ADD_EMPTY_TOKEN_ROW = "INSERT INTO price VALUES (?, 0, 0);"
ADD_USER = "INSERT INTO users VALUES (?, ?, ?)"
GET_USER_BY_CHATID = "SELECT * FROM users WHERE chatid = ?"
SET_STATE_FOR_USER = "UPDATE users SET state = ? WHERE chatid = ?"
#GET_PRICE = "SELECT IFNULL(new, -1) new FROM price WHERE token = ?"
GET_PRICE = "SELECT new FROM price WHERE token = ?"
GET_MAX_SEQUENCE_BY_CHATID = "SELECT IFNULL(MAX(sequence), 0) sequence FROM alerts WHERE chatid = ?"
ADD_ALERT = "INSERT INTO alerts (chatid, token, pricetarget, sequence, state) VALUES (?, ?, ?, ?, ?)"
GET_INACTIVE_ALERT_BY_CHATID = "SELECT * FROM alerts WHERE state = 0 AND chatid = ?"
GET_ACTIVE_ALERTS_BY_CHATID = "SELECT * FROM alerts WHERE state = 1 AND chatid = ? ORDER BY sequence"
DEL_ALERTS_BY_CHATID_AND_SEQUENCE = "DELETE FROM alerts WHERE chatid = ? AND sequence = ?"
SET_ALERT_DETAILS = "UPDATE alerts SET (token, pricetarget, sequence, state) = (?, ?, ?, ?)"
DEL_ALERT_BY_ID = "DELETE FROM alerts WHERE id = ?"
SET_ALERT_TOKEN = "UPDATE alerts SET token = ? WHERE id = ?"
SET_ALERT_PRICE = "UPDATE alerts SET pricetarget = ? WHERE id = ?"
SET_ALERT_SEQUENCE = "UPDATE alerts SET sequence = ? WHERE id = ?"
SET_ALERT_STATE = "UPDATE alerts SET state = ? WHERE id = ?"
SET_OLD_PRICE = "UPDATE price SET old = ? WHERE token = ?"
SET_PRICE = "UPDATE price SET new = ? WHERE token = ?"
GET_ACTIVE_ALERTS = "SELECT * FROM alerts WHERE state = 1"
GET_PRICELOG_BY_TOKEN = "SELECT * FROM price WHERE token = ?;"
ADD_ALERTLOG = "INSERT INTO alertslog VALUES (?, ?, ?, ?, ?)"
GET_ALERTS_SHIFT_SEQUENCE = "SELECT * FROM alerts WHERE chatid = ? AND sequence >= ?"
ALERT_SHIFT_SEQUENCE = "UPDATE alerts SET sequence = ? WHERE id = ?"


def connect():
    return sqlite3.connect("data.db", check_same_thread=False)


def create_tables(connection):
    with connection:
        connection.execute(CREATE_TABLE_ALERTS)
        connection.execute(CREATE_TABLE_USERS)
        connection.execute(CREATE_TABLE_PRICE)
        connection.execute(CREATE_TABLE_ALERTSLOG)


def add_empty_token_row(connection, token):
    with connection:
        connection.execute(ADD_EMPTY_TOKEN_ROW, (token,))


def get_user_by_chatid(connection, chatid):
    with connection:
        return connection.execute(GET_USER_BY_CHATID, (chatid,)).fetchone()

def add_user(connection, chatid, username, state):
    with connection:
        connection.execute(ADD_USER, (chatid, username, state))
        connection.commit()

def set_state_for_user(connection, chatid, state):
    with connection:
       connection.execute(SET_STATE_FOR_USER, (state, chatid))
       connection.commit()

def get_price(connection, token):
    with connection:
        return connection.execute(GET_PRICE, (token,)).fetchone()


def get_max_sequence_by_chatid(connection, chatid):
    with connection:
        return connection.execute(GET_MAX_SEQUENCE_BY_CHATID, (chatid,)).fetchone()


def add_alert(connection, chatid, token, price, sequence, state):
    with connection:
        connection.execute(ADD_ALERT, (chatid, token, price, sequence, state))
        connection.commit()


def get_inactive_alert_by_chatid(connection, chatid):
    with connection:
        return connection.execute(GET_INACTIVE_ALERT_BY_CHATID, (chatid,)).fetchone()


def set_alert_token(connection, token, id):
    with connection:
        return connection.execute(SET_ALERT_TOKEN, (token, id))
        connection.commit()

def set_alert_price(connection, pricetarget, id):
    with connection:
        return connection.execute(SET_ALERT_PRICE, (pricetarget, id))
        connection.commit()
        
def set_alert_sequence(connection, sequence, id):
    with connection:
        return connection.execute(SET_ALERT_SEQUENCE, (sequence, id))
        connection.commit()

def set_alert_state(connection, state, id):
    with connection:
        return connection.execute(SET_ALERT_STATE, (state, id))
        connection.commit()


def del_alert_by_id(connection, id):
    with connection:
        connection.execute(DEL_ALERT_BY_ID, (id,))
        connection.commit()

def set_old_price(connection, price, token):
    with connection:
        connection.execute(SET_OLD_PRICE, (price, token))
        connection.commit()


def set_price(connection, price, token):
    with connection:
        connection.execute(SET_PRICE, (price, token))
        connection.commit()


def get_active_alerts(connection):
    with connection:
        return connection.execute(GET_ACTIVE_ALERTS).fetchall()


def get_pricelog_by_token(connection, token):
    with connection:
        return connection.execute(GET_PRICELOG_BY_TOKEN, (token,)).fetchall()


def add_alertlog(connection, id, chatid, pricetarget, message, time):
    with connection:
        connection.execute(ADD_ALERTLOG, (id, chatid, pricetarget, message, time))
        connection.commit()


def get_active_alerts_by_chatid(connection, chatid):
    with connection:
        return connection.execute(GET_ACTIVE_ALERTS_BY_CHATID, (chatid,)).fetchall()


def del_alerts_by_chatid_and_sequence(connection, chatid, sequence):
    with connection:
        connection.execute(DEL_ALERTS_BY_CHATID_AND_SEQUENCE, (chatid, sequence))
        connection.commit()


def get_alerts_shift_sequence(connection, chatid, sequence):
    with connection:
        return connection.execute(GET_ALERTS_SHIFT_SEQUENCE, (chatid, sequence)).fetchall()


def alert_shift_sequence(connection, new_sequence, id):
    with connection:
        return connection.execute(ALERT_SHIFT_SEQUENCE, (new_sequence, id))
        connection.commit()