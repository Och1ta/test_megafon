import asyncio
import logging

from server import run_server
from client import run_client
from db import close_db


# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


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
        close_db()  # Закрытие базы данных
