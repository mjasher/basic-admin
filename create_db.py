
import sqlite3 
import json


def make_clients():
	conn = sqlite3.connect('example.db')
	c = conn.cursor()

	# Create table
	c.execute('''CREATE TABLE clients (name text, dob text, email text)''')

	# Insert a row of data
	# a.date().isoformat()
	c.execute("INSERT INTO clients VALUES (?, ?, ?)", ("mikey", "1890-11-05", "michael@gmail.com"))
	c.execute("INSERT INTO clients VALUES (?, ?, ?)", ("johnny", "1388-07-28", "john@gmail.com"))

	# Save (commit) the changes
	conn.commit()

	# We can also close the connection if we are done with it.
	# Just be sure any changes have been committed or they will be lost.
	c.close()
	conn.close()

def demo():
	conn = sqlite3.connect('example.db')
	c = conn.cursor()
	c.execute("SELECT rowid, * FROM clients")
	rows = c.fetchall()
	print json.dumps(rows)

if __name__ == '__main__':
	make_clients()
	demo()