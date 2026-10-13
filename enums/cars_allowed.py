from enum import Enum


class CarsAllowed(Enum):
    NO_INFORMATION = 0
    ALLOWED = 1
    NOT_ALLOWED = 2

    @classmethod
    def _missing_(cls, value: object) -> CarsAllowed:
        if isinstance(value, str):
            value = int(value)
            for member in cls:
                if member.value == value:
                    return member
        return cls.NO_INFORMATION
