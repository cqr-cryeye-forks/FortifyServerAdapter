import ulid


def get_unique_id() -> str:
    return ulid.microsecond.new().uuid.hex
