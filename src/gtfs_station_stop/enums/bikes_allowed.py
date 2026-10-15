from enum import Enum


class BikesAllowed(Enum):
    NO_INFORMATION = 0
    ALLOWED = 1
    NOT_ALLOWED = 2

    @classmethod
    def _missing_(cls, value: object) -> BikesAllowed:
        try:
            if isinstance(value, str):
                value = int(value)
                for member in cls:
                    if member.value == value:
                        return member
        except ValueError:
            pass

        return cls.NO_INFORMATION
