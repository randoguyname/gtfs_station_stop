from enum import Enum


class Timepoint(Enum):
    """
    Timepoint
    see https://gtfs.org/documentation/schedule/reference/#stop_timestxt
    """

    APPROXIMATE = 0
    EXACT = 1
