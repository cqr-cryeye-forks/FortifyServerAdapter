from pathlib import Path

from fortify.core import run_command


def check_sources(source_path: Path) -> bool:
    if not source_path.is_file():
        return False
    result = run_command([source_path.as_posix(), '--help'])
    if result.lines_err:
        print(f'Error: {result.lines_err}\nUsed sources: {source_path}')
        return False
    return True
