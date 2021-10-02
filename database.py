import sqlite3

conn = sqlite3.connect("newauct.db", check_same_thread=False)
cursor = conn.cursor()

def inser_book_in_db(book_link):
    sql = 'insert into product_links(product_link)values(\'{0}\');'.format(book_link)
    cursor.execute(sql)
    conn.commit()

def check_new_book(book_link):
    sql = 'select product_link from product_links where product_link = \'{0}\';'.format(book_link)
    cursor.execute(sql)
    result = cursor.fetchone()
    conn.commit()
    if result:
        return result
    else:
        return None