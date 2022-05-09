import logging
import subprocess

from data.classes import ResultForLaunchOneCommand

logger = logging.getLogger(__name__)


def run_command(command: list[str]) -> ResultForLaunchOneCommand:
    result_object = ResultForLaunchOneCommand()
    try:
        completed_proc = wrapper_for_subprocess(command)
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

    # result_object.lines_out = "".join(one_line + "\n" for one_line in washing(str(result_object.lines_out)))
    # result_object.lines_err = "".join(one_line + "\n" for one_line in washing(str(result_object.lines_err)))
    return result_object


def wrapper_for_subprocess(command: list[str]):
    return subprocess.run(command,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          universal_newlines=True)
