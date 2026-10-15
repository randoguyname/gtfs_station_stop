from typing import Self
from enum import Enum


class CEMVSupport(Enum):
    NO_INFORMATION = 0
    SUPPORTED = 1
    NOT_SUPPORTED = 2

    @classmethod
    def _missing_(cls, value: object) -> CEMVSupport:
        try:
            if isinstance(value, str):
                value = int(value)
                for member in cls:
                    if member.value == value:
                        return member
        except ValueError:
            pass

        return cls.NO_INFORMATION
