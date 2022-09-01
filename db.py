import sqlite3 as sl

conn = sl.connect('watchdog.db')
c = conn.cursor()

c.execute("""
        CREATE TABLE alerts (
            id INTEGER PRIMARY KEY,
            chat_id INTEGER,
            token TEXT NOT NULL,
            target_price INTEGER
        );
    """)

c.execute("""
        CREATE TABLE pricelog (
            token TEXT PRIMARY_KEY,
            price_old REAL,
            price_new REAL
        );
    """)


c.execute("""
        CREATE TABLE prealerts (
            id INTEGER PRIMARY KEY,
            chat_id INTEGER,
            token TEXT,
            state INTEGER
        );
    """)

# ============================
# Populating with test data:
c.execute('INSERT INTO pricelog values ("BTC", 0, 0)')
c.execute('INSERT INTO pricelog values ("ATOM", 0, 0)')
c.execute('INSERT INTO pricelog values ("DOT", 0, 0)')

c.execute('INSERT INTO alerts values (1, 914202, "BTC", 19999)')
c.execute('INSERT INTO alerts values (2, 914202, "ATOM", 12.1)')
c.execute('INSERT INTO alerts values (3, 914202, "DOT", 7.33)')
c.execute('INSERT INTO alerts values (4, 914202, "ATOM", 10.65)')
# ============================


conn.commit()
conn.close()
