import logging
import shutil
from abc import ABC
from pathlib import Path

from data.classes import CommandStatuses
from data.cli_arguments import cli_arguments
from data.config import RESULTS_DIR, TARGET_DIR, DEFAULT_OUTPUT_FILE, FORTIFY_APP_NAME
from fortify.core import run_command
from tools.archives import extract_archive_target
from tools.files import read_data_from_xml
from tools.randomiser import get_unique_id

logger = logging.getLogger(__name__)


class FortifyScan(ABC):
    status: CommandStatuses = CommandStatuses.QUEUE.value
    output_format: str = cli_arguments.output_format
    output_path: Path = RESULTS_DIR
    output: Path = DEFAULT_OUTPUT_FILE
    sources: Path = cli_arguments.sources
    _result: dict = None
    target: Path
    clean_results: bool = False

    def __init__(self, target: Path,
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
        self.target = self.init_target(target)
        self.output_format = output_format
        self.clean_results = clean_results

    def get_result(self):
        return self._result

    @staticmethod
    def init_target(target: Path):
        if target.is_file() and target.suffix == '.zip':
            return extract_archive_target(target_path=target, output_path=TARGET_DIR.joinpath(get_unique_id()))
        return target

    def run_scan(self):
        command = [self.sources.as_posix(), '-f', self.output.as_posix(), '-scan', self.target.as_posix()]
        logger.info(f'Start scanning {self.target.as_posix()}')
        result = run_command(command=command)
        if result.lines_err:
            logger.error(result.lines_err)
            self.status = CommandStatuses.ERROR.value
        logger.info(f'Scan finished and saved to {self.output}')
        self.status = CommandStatuses.DONE.value
        self.parce_result()
        if self.clean_results:
            self.remove_output_file()
        return self._result

    def parce_result(self):
        self._result = read_data_from_xml(self.output)

    def generate_output_path(self) -> Path:
        return self.output_path.joinpath(f'{get_unique_id()}.{self.output_format}')

    def remove_output_file(self):
        shutil.rmtree(self.output, ignore_errors=True)
        logger.info(f'File {self.output} removed')
