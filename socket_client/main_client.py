import asyncio
import logging
import socket
from socket_client.client_base import Client

logger = logging.getLogger(__name__)


async def async_client(client_socket: socket.socket, adr: tuple):
    client_loop = asyncio.get_event_loop()
    logger.info(f'New Connection: {adr}')

    client = Client(client_socket=client_socket, client_loop=client_loop)
    try:
        await client.listen_socket()
    except (ConnectionResetError, ConnectionAbortedError):
        logger.info(f'Disconnected: {adr}')
    logger.info(f'Disconnected: {adr}')
    client_socket.close()
