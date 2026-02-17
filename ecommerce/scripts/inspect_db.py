import sqlite3
conn=sqlite3.connect('db.sqlite3')
c=conn.cursor()
c.execute("PRAGMA table_info('ecommerceapp_product')")
rows=c.fetchall()
print('columns:')
for r in rows:
    print(r)
conn.close()
