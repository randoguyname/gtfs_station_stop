from enum import Enum
from typing import Self


class ServiceExceptionType(Enum):
    ADDED = 1
    REMOVED = 2

    @classmethod
    def parse(cls, value: str | int | None) -> Self | None:
        if value is None:
            return None

        if isinstance(value, int):
            try:
                return cls(value)
            except ValueError:
                return None

        if isinstance(value, str):
            try:
                return cls(int(value))
            except ValueError:
                return None

        return None
