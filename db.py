import sqlite3
from datetime import datetime

# Создание базы данных и таблицы
conn = sqlite3.connect('requests.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS requests
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, client TEXT, message TEXT, timestamp TEXT)''')
conn.commit()


# Функция для записи данных в базу данных
def save_request_to_db(client_id, message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("INSERT INTO requests (client, message, timestamp) VALUES (?, ?, ?)",
                   (client_id, message, timestamp))
    conn.commit()


# Закрытие базы данных
def close_db():
    conn.close()
