import asyncio
import json
import logging
import socket
from json.decoder import JSONDecodeError

from data.classes import ClientCommands, CommandStatuses
from data.config import TARGET_DIR
from fortify.fortify_base import FortifyScan
from tools.files import clean_results_folder, clean_target_folder
from tools.randomiser import get_unique_id
from io import BytesIO
logger = logging.getLogger(__name__)


async def async_client(client: socket.socket, adr: tuple):
    receiving_file = False
    target_archive = None
    fortify_obj: FortifyScan
    scan_result_as_bytes = b''
    client_loop = asyncio.get_event_loop()
    logger.info('New Connection: ' + str(adr))

    async def send_to_client(data_for_sending: dict,
                             status: CommandStatuses = CommandStatuses.DONE.value):
        data_for_sending['status'] = status
        logger.info(f'Send to client: {data_for_sending}')
        await client_loop.sock_sendall(client, json.dumps(data_for_sending).encode('utf8'))

    async def get_data_from_client() -> dict:
        try:
            response = await client_loop.sock_recv(client, 1024)
            return json.loads(response.decode('utf8').replace("'", '"'))
        except JSONDecodeError as err:
            logger.error(err)
            return {}

    async def receive_file():  # sourcery skip: raise-specific-error
        logger.info("Receiving Target file")
        file_size_in_bytes = await client_loop.sock_recv(client, 8)
        file_size = int.from_bytes(file_size_in_bytes, 'big')
        await client_loop.sock_sendall(client, "File size received.".encode('utf8'))

        logger.info("[RECV] Receiving the file data...")
        packet = b""  # Use bytes, not str, to accumulate
        while len(packet) < file_size:
            if (file_size - len(packet)) > 1024:  # if remaining bytes are more than the defined chunk size
                buffer = await client_loop.sock_recv(client, 1024)  # read SIZE bytes
            else:
                buffer = await client_loop.sock_recv(client, file_size - len(packet))  # read remaining number of bytes
            if not buffer:
                raise Exception("Incomplete file received")
            packet += buffer
        file_name = TARGET_DIR.joinpath(f'{get_unique_id()}.zip')
        with open(file_name, 'wb') as f:
            f.write(packet)
            f.close()
        logger.info("[RECV] File data received.")
        await client_loop.sock_sendall(client, "File data received".encode('utf8'))
        return file_name

    while True:
        try:
            if receiving_file:
                try:
                    target_archive = await receive_file()
                except Exception as e:
                    logger.error(e)
                finally:
                    receiving_file = False
            else:
                received_data = await get_data_from_client()

                command = received_data.get('command')
                logger.info(f'Received data: {received_data}')

                if command == ClientCommands.GET_FILE.value:
                    receiving_file = True

                elif command == ClientCommands.RUN_SCAN.value:
                    clean_results = received_data.get('message', True)
                    if not target_archive:
                        result = {'result': 'Target undefined'}
                        status = CommandStatuses.ERROR.value
                    else:
                        fortify_obj = FortifyScan(target=target_archive, clean_results=clean_results)
                        scan_result = fortify_obj.run_scan()
                        scan_result_as_bytes = json.dumps(scan_result).encode('utf-8')
                        result = {'result': 'Forty scan status', 'length': len(scan_result_as_bytes)}
                        status = fortify_obj.status
                    await send_to_client(data_for_sending=result, status=status)
                    clean_results_folder()

                elif command == ClientCommands.GET_RESULT.value:
                    await client_loop.sock_sendfile(client, file=BytesIO(scan_result_as_bytes))

                elif command == ClientCommands.CLEAN_OLD_RESULTS.value:
                    result = {'result': 'Old scans removed'}
                    status = CommandStatuses.ERROR.value
                    if clean_results_folder():
                        status = CommandStatuses.DONE.value
                    await send_to_client(data_for_sending=result, status=status)

                elif command == ClientCommands.CLEAN_OLD_TARGETS.value:
                    result = {'result': 'Old targets removed'}
                    status = CommandStatuses.ERROR.value
                    if clean_target_folder():
                        status = CommandStatuses.DONE.value
                    await send_to_client(data_for_sending=result, status=status)

                else:
                    logger.warning(f"Unknown command: {command}\nMore data: {received_data}")
                    await send_to_client(data_for_sending={'result': 'Unknown command'},
                                         status=CommandStatuses.ERROR.value)
        except ConnectionResetError:
            logger.info(f'Disconnected: {str(adr)}')
            break
        except Exception as e:
            logging.error(f'DATA ERROR:{e}')
            break
    client.close()
