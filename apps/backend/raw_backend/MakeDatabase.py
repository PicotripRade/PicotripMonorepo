import sqlite3

import pandas as pd
from support.support_objects import main_database
k = main_database.iloc[0, :]
m = main_database.iloc[500:700, :]




# Assuming 'main_database' is your DataFrame and 'k' is the first row
# If 'main_database' is a DataFrame and 'k' is a Series representing the first row:

# Connect to an SQLite database
conn = sqlite3.connect('../my_database.db')

# Write the Series to the SQLite database
k.to_frame().T.to_sql('my_table', conn, index=False, if_exists='replace')
m.to_sql('my_table', conn, if_exists='append', index=False)


# Write your SQL query to select data from your database
sql_query = "SELECT * FROM my_table;"

# Read the data into a Pandas DataFrame
df = pd.read_sql_query(sql_query, conn)

# Close the database connection
conn.close()
print(df)