import asyncio
import json
import logging
import socket
import subprocess
from asyncio import AbstractEventLoop, sleep
from io import BytesIO
from json import JSONDecodeError
from pathlib import Path

from data.classes import CommandStatuses, ClientCommands
from data.config import TARGET_DIR
from fortify.fortify_base import FortifyScan
from tools.files import read_data_from_xml
from tools.randomiser import get_unique_name

logger = logging.getLogger(__name__)


class Client:
    """
    Socket Client base functions and logic
    """
    _scan_result: dict = {}

    def __init__(self,
                 client_socket: socket.socket,
                 target: Path = None,
                 fortify_obj: "FortifyScan" = None,
                 client_loop: AbstractEventLoop = None,
                 is_receiving_files=False,
                 scan_result_as_bytes=b'',
                 ):
        self.target = target
        self.fortify_obj = fortify_obj or FortifyScan(target=target)
        self._socket = client_socket
        self.client_loop = client_loop or asyncio.get_event_loop()

        # internal variables
        self._is_receiving_files = is_receiving_files
        self._scan_result_as_bytes = scan_result_as_bytes

    def is_receiving_file(self) -> bool:
        return self._is_receiving_files

    def change_receiving_file_mode(self, mode: bool):
        self._is_receiving_files = mode

    def create_target(self, target: Path):
        self.target = target
        self.fortify_obj.init_target(target=target)

    async def send_to_client(self, data_for_sending: dict,
                             status: "CommandStatuses.value" = CommandStatuses.DONE.value):
        data_for_sending['status'] = status
        logger.info(f'Send to client: {data_for_sending}')
        data = json.dumps(data_for_sending).encode('utf8')
        await self.client_loop.sock_sendall(self._socket, data)

    async def get_data_from_client(self) -> dict:
        try:
            response = await self.client_loop.sock_recv(self._socket, 1024)
            if response == b'':
                return {}
            return json.loads(response.decode('utf8').replace("'", '"'))
        except JSONDecodeError as err:
            logger.error(err)
            return {}

    async def receive_file(self) -> Path:
        logger.info("Receiving Target file")
        self.change_receiving_file_mode(mode=True)
        file_size_in_bytes = await self.client_loop.sock_recv(self._socket, 8)
        file_size = int.from_bytes(file_size_in_bytes, 'big')
        await self.client_loop.sock_sendall(self._socket, "File size received.".encode('utf8'))

        logger.info("[RECV] Receiving the file data...")
        packet = b""  # Use bytes, not str, to accumulate
        while len(packet) < file_size:
            if (file_size - len(packet)) > 1024:  # if remaining bytes are more than the defined chunk size
                buffer = await self.client_loop.sock_recv(self._socket, 1024)  # read SIZE bytes
            else:  # read remaining number of bytes
                buffer = await self.client_loop.sock_recv(self._socket, file_size - len(packet))
            if not buffer:
                self.change_receiving_file_mode(mode=False)
                raise ValueError("Incomplete file received")
            packet += buffer
        file_name = TARGET_DIR.joinpath(f'{get_unique_name()}.zip')
        with open(file_name, 'wb') as f:
            f.write(packet)
            f.close()
        logger.info("[RECV] File data received.")
        await self.client_loop.sock_sendall(self._socket, "File data received".encode('utf8'))
        self.change_receiving_file_mode(mode=False)
        return file_name

    async def run_target_scan(self, received_data: dict):
        clean_results = received_data.get('message', True)
        if not self.target:
            result = {'result': 'Target undefined'}
            status = CommandStatuses.ERROR.value
        else:
            is_finished = False
            self.fortify_obj.clean_results = clean_results

            command = [str(self.fortify_obj.sources),
                       '-f', str(self.fortify_obj.output),
                       '-scan', str(self.fortify_obj.target)]
            logger.info(f'Start scanning {self.fortify_obj.target.as_posix()}')
            result = subprocess.Popen(command,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      universal_newlines=True,
                                      )
            while not is_finished:
                print(f"return code: {result.poll()}")
                if type(result.returncode) is int:
                    print(f"return code: {result.returncode}")
                    is_finished = True

                await self.send_to_client(
                    data_for_sending={'result': 'Fortify scan status'},
                    status=CommandStatuses.DONE.value if is_finished else CommandStatuses.IN_PROGRESS.value
                )
                await sleep(10)
            print(f"return code: {result.returncode}")
            if result.stderr:
                logger.error(result.stderr)
            self._scan_result = read_data_from_xml(self.fortify_obj.output)
            self._scan_result_as_bytes = json.dumps(self._scan_result).encode()
            result = {
                'result': 'Forty scan status',
                'length': len(self._scan_result_as_bytes),
                'is_finished': is_finished
            }
            status = CommandStatuses.DONE.value
        await self.send_to_client(data_for_sending=result, status=status)

    async def listen_socket(self):
        while True:
            if self.is_receiving_file():
                try:
                    self.target = await self.receive_file()
                    self.create_target(self.target)
                except Exception as e:
                    logger.error(e)
                finally:
                    self.change_receiving_file_mode(mode=False)
            else:
                received_data = await self.get_data_from_client()

                command = received_data.get('command')
                logger.info(f'Received data: {received_data}')
                match command:

                    case ClientCommands.GET_FILE.value:
                        self.change_receiving_file_mode(mode=True)

                    case ClientCommands.RUN_SCAN.value:
                        await self.run_target_scan(received_data=received_data)

                    case ClientCommands.GET_RESULT.value:
                        await self.client_loop.sock_sendfile(self._socket, file=BytesIO(self._scan_result_as_bytes))

                    case ClientCommands.CLEAN_OLD_RESULTS.value | ClientCommands.CLEAN_OLD_TARGETS.value:
                        await self.send_to_client(data_for_sending={'result': 'Feature disabled'},
                                                  status=CommandStatuses.ERROR.value)

                    case _:
                        logger.warning(f"Unknown command: {command}\nMore data: {received_data}")
                        await self.send_to_client(data_for_sending={'result': 'Unknown command'},
                                                  status=CommandStatuses.ERROR.value)
