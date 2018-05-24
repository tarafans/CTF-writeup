a = open('mydb.db', 'rb').read()
b = open('db.db', 'wb')

a = a[a.find('<pre>') + len('<pre>'):]
a = a[:a.find('</pre>')]
b.write(a)
b.close()
