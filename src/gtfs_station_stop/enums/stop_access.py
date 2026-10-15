
from enum import Enum


class StopAccess(Enum):
    NOT_ACCESSIBLE_FROM_STREET = 0
    ACCESSIBLE_FROM_STREET = 1
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, value: object) -> StopAccess:
        try:
            if isinstance(value, str):
                value = int(value)
                for member in cls:
                    if member.value == value:
                        return member
        except ValueError:
            pass

        return cls.UNKNOWN
