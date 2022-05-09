import enum
from dataclasses import dataclass
from typing import Union


@enum.unique
class CommandStatuses(enum.Enum):
    ADDING_ERROR = 'Adding error'
    IN_PROGRESS = 'In Progress'
    QUEUE = 'Queue'
    ERROR = 'Error'
    DONE = 'Done'


@enum.unique
class ClientCommands(enum.Enum):
    CHECK_STATUS = 'CHECK_STATUS'
    GET_RESULT = 'GET_RESULT'
    RUN_SCAN = 'RUN_SCAN'
    GET_FILE = 'GET_FILE'
    CLEAN_OLD_TARGETS = 'CLEAN_OLD_TARGETS'
    CLEAN_OLD_RESULTS = 'CLEAN_OLD_RESULTS'


@dataclass
class ResultForLaunchOneCommand:
    content: Union[str, list[str], list[dict], dict] = None
    lines_out: str = ""
    lines_err: str = ""
