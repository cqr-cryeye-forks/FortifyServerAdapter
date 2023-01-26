import datetime
from pathlib import Path
import shutil
from data.config import RESULTS_DIR, TARGET_DIR


def clean_old_results_and_targets(delete_age: int = 30):
    print('Cleaning old junk projects...')
    for folder in [RESULTS_DIR, TARGET_DIR]:
        for file_ in folder.iterdir():
            if file_.name != '.gitkeep':
                if 'whitebox' not in file_.name:
                    delete_path(path=file_)
                    continue
                creating_date: str = file_.name.split('_', 2)[-2]
                if creating_date == 'whitebox':
                    delete_path(path=file_)
                    continue
                else:
                    try:
                        parsed_date = datetime.datetime.strptime(creating_date, '%Y-%m-%d').date()
                        project_age = datetime.date.today() - parsed_date
                        if project_age.days > delete_age:
                            delete_path(path=file_)
                            continue
                    except Exception as e:
                        print(f'Parse error: {e}')
            print(f"Project {file_} skipped")
    print('Cleaning old junk files finished')


def delete_path(path: Path):
    if path.is_file():
        path.unlink(missing_ok=True)
    else:
        shutil.rmtree(path)
    print(f"Path removed: {path}")
    return
