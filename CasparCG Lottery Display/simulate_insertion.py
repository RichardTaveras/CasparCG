import sqlite3
import time
import random

db_path = 'lottery.db'

lotteries = ['lottery1', 'lottery2', 'lottery3']

def insert_numbers(lottery_table):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    numbers = [str(random.randint(1, 99)) for _ in range(3)]
    numbers_str = ','.join(numbers)
    cursor.execute(f'''
        INSERT INTO {lottery_table} (numbers) VALUES (?)
    ''', (numbers_str,))
    conn.commit()
    conn.close()
    print(f"Insertados números en {lottery_table}: {numbers}")

while True:
    for lottery in lotteries:
        insert_numbers(lottery)
    time.sleep(60)  # Tiempo entre inserciones

