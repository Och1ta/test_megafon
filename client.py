import asyncio
import logging
import random


logger = logging.getLogger(__name__)


async def run_client(client_id, message_count=5):
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)

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
