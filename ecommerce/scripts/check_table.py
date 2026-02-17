import sqlite3
conn = sqlite3.connect('db.sqlite3')
print('tables:', conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall())
print('product columns:', conn.execute("PRAGMA table_info('ecommerceapp_product')").fetchall())
