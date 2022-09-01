def delete_query(table, condition):
    return ("DELETE FROM " + table + " WHERE " + condition)


def select_query(table, condition): 
    return ("SELECT * FROM " + table + " WHERE " + condition)


def update_query(table, column, value, condition):
    return ("UPDATE " + table + " SET " + column + " = " + value + " WHERE " + condition)


def test():
    print("test successful")