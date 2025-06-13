# import sqlite3
# import pandas as pd
# from support_objects import main_database
#
# conn = sqlite3.connect('baza')
# cursor =conn.cursor()
#
# k = main_database.iloc[:3,:]
# k.to_sql('test', con=conn)
# pd.read_sql('test', conn=conn)

import sqlite3

# Connect to SQLite database (creates the database if it doesn't exist)
conn = sqlite3.connect('example.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Create a table
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    age INTEGER
                  )''')

# Insert some data
cursor.execute("INSERT INTO users (name, age) VALUES (?, ?)", ('Alice', 30))
cursor.execute("INSERT INTO users (name, age) VALUES (?, ?)", ('Bob', 25))
cursor.execute("INSERT INTO users (name, age) VALUES (?, ?)", ('Charlie', 35))

# Save (commit) the changes
conn.commit()

# Fetch and print all data from the table
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()
for row in rows:
    print(row)

# Close the connection
conn.close()
