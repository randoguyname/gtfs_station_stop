from enum import Enum
from typing import Self


class PickupType(Enum):
    """
    Pickup Type.
    see https://gtfs.org/documentation/schedule/reference/#stop_timestxt
    """

    REGULARLY_SCHEDULED = 0
    NO_PICKUP_AVAILABLE = 1
    PHONE_AGENCY_FOR_PICKUP = 2
    COORDINATE_WITH_DRIVER_FOR_PICKUP = 3

    @classmethod
    def _missing_(cls, value: object) -> PickupType:
        if isinstance(value, str):
            value = int(value)
            for member in cls:
                if member.value == value:
                    return member
        return cls.REGULARLY_SCHEDULED


class ContinuousPickupType(Enum):
    """
    Pickup Type.
    see https://gtfs.org/documentation/schedule/reference/#stop_timestxt
    """

    REGULARLY_SCHEDULED = 0
    NO_PICKUP_AVAILABLE = 1
    PHONE_AGENCY_FOR_PICKUP = 2
    COORDINATE_WITH_DRIVER_FOR_PICKUP = 3

    @classmethod
    def _missing_(cls, value: object) -> ContinuousPickupType:
        if isinstance(value, str):
            value = int(value)
            for member in cls:
                if member.value == value:
                    return member
        return cls.NO_PICKUP_AVAILABLE
