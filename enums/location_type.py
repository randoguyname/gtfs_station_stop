from typing import Self
from enum import IntEnum


class LocationType(IntEnum):
    """
    Location Type.
    see https://gtfs.org/documentation/schedule/reference/#stopstxt
    """

    STOP = 0
    STATION = 1
    ENTRANCE = 2
    GENERIC_NODE = 3
    BOARDING_AREA = 4
    UNKNOWN = 5

    def __str__(self) -> str:
        if self == LocationType.STOP:
            return "stop"
        elif self == LocationType.STATION:
            return "station"
        elif self == LocationType.ENTRANCE:
            return "entrance"
        elif self == LocationType.GENERIC_NODE:
            return "generic_node"
        elif self == LocationType.BOARDING_AREA:
            return "boarding_area"
        else:
            return "unknown"

    @classmethod
    def _missing_(cls, value: object) -> LocationType:
        if isinstance(value, str):
            value = int(value)
            for member in cls:
                if member.value == value:
                    return member
        return cls.STOP
