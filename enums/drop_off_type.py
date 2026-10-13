from enum import Enum


class DropOffType(Enum):
    """
    Drop-Off Type.
    see https://gtfs.org/documentation/schedule/reference/#stop_timestxt
    """

    REGULARLY_SCHEDULED = 0
    NO_DROP_OFF_AVAILABLE = 1
    PHONE_AGENCY_FOR_DROP_OFF = 2
    COORDINATE_WITH_DRIVER_FOR_DROP_OFF = 3

    @classmethod
    def _missing_(cls, value: object) -> DropOffType:
        if isinstance(value, str):
            value = int(value)
            for member in cls:
                if member.value == value:
                    return member
        return cls.REGULARLY_SCHEDULED


class ContinuousDropOffType(Enum):
    """
    Drop-Off Type.
    see https://gtfs.org/documentation/schedule/reference/#stop_timestxt
    """

    REGULARLY_SCHEDULED = 0
    NO_DROP_OFF_AVAILABLE = 1
    PHONE_AGENCY_FOR_DROP_OFF = 2
    COORDINATE_WITH_DRIVER_FOR_DROP_OFF = 3

    @classmethod
    def _missing_(cls, value: object) -> ContinuousDropOffType:
        if isinstance(value, str):
            value = int(value)
            for member in cls:
                if member.value == value:
                    return member
        return cls.NO_DROP_OFF_AVAILABLE
