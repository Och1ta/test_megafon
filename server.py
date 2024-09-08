import asyncio
import logging

from db import save_request_to_db


logger = logging.getLogger(__name__)


async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    addr_str = f"{addr[0]}:{addr[1]}"

    logger.info(f'Новое соединение от {addr_str}')

    try:
        while True:
            data = await reader.read(100)
            if not data:
                break
            message = data.decode()
            logger.info(f'Получено: {message} от {addr_str}')
            writer.write(data)
            await writer.drain()

            # Сохранение в базу данных
            save_request_to_db(addr_str, message)
    except asyncio.CancelledError:
        logger.info(f'Сеанс с {addr_str} завершён')
    finally:
        writer.close()
        await writer.wait_closed()
        logger.info(f'Соединение с {addr_str} закрыто')


async def run_server():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 8888)
    addr = server.sockets[0].getsockname()
    logger.info(f'Server запущен на {addr}')

    async with server:
        try:
            await server.serve_forever()
        except asyncio.CancelledError:
            logger.info('Сервер завершает работу...')
