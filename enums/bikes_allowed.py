from enum import Enum


class BikesAllowed(Enum):
    NO_INFORMATION = 0
    ALLOWED = 1
    NOT_ALLOWED = 2

    @classmethod
    def _missing_(cls, value: object) -> BikesAllowed:
        if isinstance(value, str):
            value = int(value)
            for member in cls:
                if member.value == value:
                    return member
        return cls.NO_INFORMATION
