from dataclasses import dataclass
from datetime import time
from typing import Self


@dataclass(order=True, frozen=True)
class GtfsArrivalDepartureTime:
    """GTFS Specific Arrival or Departure Times from stoptimes.txt"""

    hour: int
    minute: int
    second: int

    @classmethod
    def strptime(cls, time_str: str) -> Self:
        """
        Generate the dataclass from a string in a dataset row.
        Times are permitted to exceed 24 hours for datasets after midnight, so the
        built-in method datetime.strptime cannot be used.
        see https://gtfs.org/documentation/schedule/reference/#stop_timestxt
        arrival_time and departure_time
        """
        return cls(*[int(x) for x in time_str.split(":")])

    @classmethod
    def from_time(cls, time_: time) -> Self:
        return cls(time_.hour, time_.minute, time_.second)
