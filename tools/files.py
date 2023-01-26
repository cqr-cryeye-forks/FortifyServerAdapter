import json
import logging
from pathlib import Path

import xmltodict as xmltodict

logger = logging.getLogger(__file__)


def read_data_from_xml(path_to_file: Path) -> dict:
    """ Generated json if not empty, else "[]" """

    try:
        parsed_xml = xmltodict.parse(path_to_file.read_text(), encoding='utf-8')
        return json.loads(json.dumps(parsed_xml))
    except FileNotFoundError:
        logger.warning(f"Way unreachable {path_to_file} - file not found, return empty list")
        return {}
    except (json.JSONDecodeError, json.JSONEncoder) as err:
        logger.warning(f"{err}\n{path_to_file} - file unreadable, return empty list")
        return {}
    except UnicodeDecodeError as e:
        logger.warning(f"{path_to_file} - unicode error: {e}")
        return {}
