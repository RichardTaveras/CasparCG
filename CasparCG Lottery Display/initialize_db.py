import sqlite3

conn = sqlite3.connect('lottery.db')
cursor = conn.cursor()

lotteries = ['lottery1', 'lottery2', 'lottery3']

for lottery in lotteries:
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {lottery} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numbers TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

conn.commit()
conn.close()
