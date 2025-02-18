from enum import IntEnum
from sys import stderr
_exit = exit


def exit(code: int, reason: str):
    if reason:
        print(reason, file=stderr)
    _exit(code)


class EXIT_CODES(IntEnum):
    BAD_AUTH = 3
    NO_SERVICES = 4
