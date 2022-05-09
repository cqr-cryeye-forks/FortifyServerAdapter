import asyncio
import logging
import socket

from data.cli_arguments import cli_arguments
from socket_client import main_client

logger = logging.getLogger(__name__)


async def socket_listener():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # init server socket
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # TCP socket
    server.bind((cli_arguments.host, cli_arguments.port))  # bind host and port
    server.listen()  # start listen
    server.setblocking(False)  # not blocking (not sure for what)
    logger.info(f"Socket is listening on {cli_arguments.host}:{cli_arguments.port}")
    loop = asyncio.get_event_loop()  # get or create loop for clients
    while True:
        client, _ = await loop.sock_accept(server)  # accept client
        loop.create_task(main_client.async_client(client, _))  # create task ro each connected client
        logger.info(f'Client task created: {client}')
