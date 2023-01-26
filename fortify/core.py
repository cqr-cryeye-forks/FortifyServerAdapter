import logging
import subprocess

from data.classes import ResultForLaunchOneCommand

logger = logging.getLogger(__name__)


def run_command(command: list[str]) -> ResultForLaunchOneCommand:
    result_object = ResultForLaunchOneCommand()
    try:
        completed_proc = subprocess.run(command,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        universal_newlines=True)
    except FileNotFoundError as error:
        logger.error(error)
        result_object.lines_out = '',
        result_object.lines_err = str(error.strerror)
    except (FileNotFoundError, PermissionError, subprocess.CalledProcessError) as error:
        logger.error(error)
        result_object.lines_out = str(error.stdout),
        result_object.lines_err = str(error.stderr)
    else:
        result_object.lines_out = completed_proc.stdout
        result_object.lines_err = completed_proc.stderr
    return result_object
