import logging
from pathlib import Path

LOG_FORMAT = '%(levelname) -10s %(asctime)s %(name) -20s %(funcName) -20s %(lineno) -5d: %(message)s'
logger = logging.getLogger(__name__)
logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)

# Fortify sources
BASE_DIR = Path(__file__).parents[1]
PARENT_BASE = BASE_DIR.parent
FORTIFY_APP_NAME = 'sourceanalyzer.exe'
FORTIFY_APP = PARENT_BASE.joinpath('bin', FORTIFY_APP_NAME)

TEMP_DIR = BASE_DIR.joinpath('temp_data')
RESULTS_DIR = TEMP_DIR.joinpath('results')
TARGET_DIR = TEMP_DIR.joinpath('target')
DEFAULT_OUTPUT_NAME = 'output'
DEFAULT_OUTPUT_FORMAT = 'fvdl'  # same as xml
# DEFAULT_OUTPUT_FORMAT = 'fpr'
DEFAULT_OUTPUT_FILE = RESULTS_DIR.joinpath(f'{DEFAULT_OUTPUT_NAME}.{DEFAULT_OUTPUT_FORMAT}')
