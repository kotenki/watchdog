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