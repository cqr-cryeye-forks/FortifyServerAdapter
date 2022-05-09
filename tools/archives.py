import logging
from pathlib import Path

import patoolib

logger = logging.getLogger(__name__)


def extract_archive_target(target_path: Path, output_path: Path) -> Path:
    try:
        logger.info(f'Archive detected. Extracting to {output_path.resolve()}')
        patoolib.extract_archive(str(target_path.resolve()), outdir=str(output_path.resolve()))
        logger.info(f'Archive extracted to {output_path.resolve()}')
        return output_path.resolve()
    except FileNotFoundError as e:
        raise f"Can't extract {target_path.resolve()} - archive not found" from e
