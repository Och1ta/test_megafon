import asyncio
import logging
import random
import sqlite3
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Инициализация базы данных
db = sqlite3.connect('requests.db')
cursor = db.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS requests
                  (client_ip TEXT, message TEXT, timestamp TEXT)''')
db.commit()


# TCP-сервер
async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    logger.info(f'Новое соединение от {addr}')

    try:
        while True:
            data = await reader.read(100)
            if not data:
                break
            message = data.decode()
            logger.info(f'Получено: {message} от {addr}')

            # Запись в базу данных
            cursor.execute("INSERT INTO requests (client_ip, message, timestamp) VALUES (?, ?, ?)",
                           (str(addr), message, datetime.now().isoformat()))
            db.commit()

            writer.write(data)
            await writer.drain()
    except asyncio.CancelledError:
        logger.info(f'Сеанс с {addr} завершён')
    finally:
        writer.close()
        await writer.wait_closed()
        logger.info(f'Соединение с {addr} закрыто')


async def run_server():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 8888)
    addr = server.sockets[0].getsockname()
    logger.info(f'Server запущен на {addr}')

    async with server:
        try:
            await server.serve_forever()
        except asyncio.CancelledError:
            logger.info('Сервер завершает работу...')


# TCP-клиент
async def run_client(client_id, message_count=5):
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    addr = writer.get_extra_info('sockname')

    for i in range(message_count):
        message = f'Клиент {client_id}: сообщение {i + 1}'
        logger.info(f'Клиент {client_id} отправляет: {message}')
        writer.write(message.encode())
        await writer.drain()

        data = await reader.read(100)
        logger.info(f'Клиент {client_id} получил: {data.decode()}')

        # Задержка перед следующей отправкой сообщения
        await asyncio.sleep(random.uniform(5, 10))

    logger.info(f'Клиент {client_id} завершает соединение')
    writer.close()
    await writer.wait_closed()


# Главная функция
async def main():
    # Запуск сервера
    server_task = asyncio.create_task(run_server())

    # Запуск 10 клиентов
    client_tasks = [
        asyncio.create_task(run_client(client_id))
        for client_id in range(1, 11)
    ]

    # Ожидание завершения всех клиентов
    await asyncio.gather(*client_tasks)

    # Завершение сервера после того, как все клиенты завершат работу
    server_task.cancel()
    try:
        await server_task
    except asyncio.CancelledError:
        logger.info('Сервер был корректно завершён.')


# Запуск программы
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Программа прервана пользователем')
    finally:
        db.close()  # Закрытие соединения с базой данных
