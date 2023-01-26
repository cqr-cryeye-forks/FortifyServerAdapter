import datetime

import ulid


def get_unique_id() -> str:
    return ulid.microsecond.new().uuid.hex


def get_unique_name() -> str:
    return f"whitebox_{datetime.date.today()}_{get_unique_id()}"
