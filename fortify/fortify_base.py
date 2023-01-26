import logging
import shutil
import subprocess
from abc import ABC
from pathlib import Path

from data.classes import CommandStatuses
from data.cli_arguments import cli_arguments
from data.config import RESULTS_DIR, TARGET_DIR, DEFAULT_OUTPUT_FILE, FORTIFY_APP_NAME
from tools.archives import extract_archive_target
from tools.files import read_data_from_xml
from tools.randomiser import get_unique_name

logger = logging.getLogger(__name__)


class FortifyScan(ABC):
    status: "CommandStatuses.value" = CommandStatuses.QUEUE.value
    output_format: str = cli_arguments.output_format
    output_path: Path = RESULTS_DIR
    output: Path = DEFAULT_OUTPUT_FILE
    sources: Path = cli_arguments.sources
    _result: dict = None
    _is_scan_started: bool = False
    target: Path = None
    clean_results: bool = False

    def __init__(self, target: Path = None,
                 output: Path = None,
                 output_format: str = cli_arguments.output_format,
                 sources: Path = cli_arguments.sources,
                 clean_results: bool = False):
        if sources.is_dir():
            sources = sources.joinpath(FORTIFY_APP_NAME)
        self.sources = sources
        if not output:
            output = self.generate_output_path()
        self.output = output
        if target:
            self.target = self.init_target(target)
        self.output_format = output_format
        self.clean_results = clean_results

    def get_result(self):
        return self._result

    def init_target(self, target: Path):
        target_path = target
        if target.is_file() and target.suffix == '.zip':
            target_path = extract_archive_target(target_path=target, output_path=TARGET_DIR.joinpath(get_unique_name()))
        self.target = target_path
        return target_path

    def run_scan(self):
        if self._is_scan_started:
            return self._is_scan_started
        self._is_scan_started = True
        if not self.target:
            self._is_scan_started = False
            raise FileNotFoundError('No target in scan')
        command = [str(self.sources), '-f', str(self.output), '-scan', str(self.target)]
        logger.info(f'Start scanning {self.target.as_posix}')
        logger.info(f'Command {command}')
        # result = run_command(command=command)
        final_result = None
        while not final_result:
            result = subprocess.run(command,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    universal_newlines=True)
            self.status = CommandStatuses.IN_PROGRESS.value
            if type(result.returncode) is int:
                final_result = result
        # noinspection PyUnboundLocalVariable
        if result.stderr:
            logger.error(result.stderr)
            self.status = CommandStatuses.ERROR.value
        logger.info(f'Scan finished and saved to {self.output}')
        self.status = CommandStatuses.DONE.value
        self._result = read_data_from_xml(self.output)
        self._result['errors'] = [result.stderr]
        if self.clean_results:
            self.remove_output_file()
            # self.remove_target_folder()
        self._is_scan_started = False
        return self._result

    def generate_output_path(self) -> Path:
        return self.output_path.joinpath(f'{get_unique_name()}.{self.output_format}')

    def remove_output_file(self):
        shutil.rmtree(self.output, ignore_errors=True)
        logger.info(f'File {self.output} removed')

    def remove_target_folder(self):
        shutil.rmtree(self.sources.as_posix(), ignore_errors=True)
        logger.info(f'Folder {self.sources} removed')
