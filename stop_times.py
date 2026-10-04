"""Stop Times Dataset."""

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Self, override
from functools import total_ordering

from datetime import time

import logging

from .helpers import get_as_number
from .static_dataset import GtfsStaticDataset
from .sorted_list import SortedList

_LOGGER = logging.getLogger(__name__)


class PickupType(Enum):
    """
    Pickup Type.
    see https://gtfs.org/documentation/schedule/reference/#stop_timestxt
    """

    REGULARLY_SCHEDULED = 0
    NO_PICKUP_AVAILABLE = 1
    PHONE_AGENCY_FOR_PICKUP = 2
    COORDINATE_WITH_DRIVER_FOR_PICKUP = 3


class DropOffType(Enum):
    """
    Drop-Off Type.
    see https://gtfs.org/documentation/schedule/reference/#stop_timestxt
    """

    REGULARLY_SCHEDULED = 0
    NO_DROP_OFF_AVAILABLE = 1
    PHONE_AGENCY_FOR_DROP_OFF = 2
    COORDINATE_WITH_DRIVER_FOR_DROP_OFF = 3


class TimePoint(Enum):
    """
    Timepoint
    see https://gtfs.org/documentation/schedule/reference/#stop_timestxt
    """

    APPROXIMATE = 0
    EXACT = 1


@dataclass(order=True)
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


@total_ordering
@dataclass
class StopTime:
    """Stop Time."""
    trip_id: str
    arrival_time: GtfsArrivalDepartureTime | None
    departure_time: GtfsArrivalDepartureTime | None

    stop_id: str | None
    location_group_id: str | None
    location_id: str | None
    stop_sequence: int
    stop_headsign: str | None
    start_pickup_drop_off_window: str | None
    end_pickup_drop_off_window: str | None

    pickup_type: PickupType
    drop_off_type: DropOffType
    continuous_pickup: PickupType
    continuous_drop_off: DropOffType

    shape_dist_traveled: float
    timepoint: TimePoint

    def __init__(self, stop_times_data) -> None:
        self.trip_id = stop_times_data.trip_id

        self.arrival_time = None

        if (arrival_time_str := getattr(stop_times_data, "arrival_time", None)) not in {
            None,
            "",
        }:
            self.arrival_time = GtfsArrivalDepartureTime.strptime(
                arrival_time_str)  # pyright: ignore[reportArgumentType]

        self.departure_time = None
        if (departure_time_str := getattr(stop_times_data, "departure_time", None)) not in {
            None,
            "",
        }:
            self.departure_time = GtfsArrivalDepartureTime.strptime(
                departure_time_str)  # pyright: ignore[reportArgumentType]

        self.stop_id = getattr(stop_times_data, "stop_id", None)
        self.location_group_id = getattr(
            stop_times_data, "location_group_id", None)
        self.location_id = getattr(stop_times_data, "location_id", None)

        self.stop_sequence = int(stop_times_data.stop_sequence)
        self.stop_headsign = getattr(stop_times_data, "stop_headsign", "")
        self.start_pickup_drop_off_window = getattr(stop_times_data,
                                                    "start_pickup_drop_off_window", None
                                                    )
        self.end_pickup_drop_off_window = getattr(stop_times_data,
                                                  "end_pickup_drop_off_window", None
                                                  )
        self.pickup_type = PickupType(
            get_as_number(stop_times_data, "pickup_type", int)
        )
        self.drop_off_type = DropOffType(
            get_as_number(stop_times_data, "drop_off_type", int)
        )

        self.continuous_pickup = PickupType(
            get_as_number(stop_times_data, "continuous_pickup", int)
        )

        self.continuous_drop_off = DropOffType(
            get_as_number(stop_times_data, "continuous_drop_off", int)
        )

        self.shape_dist_traveled = float(
            # pyright: ignore[reportArgumentType]
            get_as_number(stop_times_data, "shape_dist_traveled", float)
        )
        self.timepoint = TimePoint(
            get_as_number(stop_times_data, "timepoint", int, 1)
        )

    @classmethod
    def create_dummy_time(
        cls,
        stop_id: str | None = None,
        arrival_time: GtfsArrivalDepartureTime | None = None,
        departure_time: GtfsArrivalDepartureTime | None = None,
        location_group_id: str | None = None,
        location_id: str | None = None,
        trip_id: str = "",
        stop_sequence: int = 0,
        stop_headsign: str | None = None,
        pickup_type: PickupType = PickupType.REGULARLY_SCHEDULED,
        drop_off_type: DropOffType = DropOffType.REGULARLY_SCHEDULED,
        continuous_pickup: PickupType = PickupType.REGULARLY_SCHEDULED,
        continuous_drop_off: DropOffType = DropOffType.REGULARLY_SCHEDULED,
        shape_dist_traveled: float = 0,
        timepoint: TimePoint = TimePoint.EXACT,
    ) -> Self:
        output = cls.__new__(cls)
        output.stop_id = stop_id
        output.arrival_time = arrival_time
        output.departure_time = departure_time
        output.location_group_id = location_group_id
        output.location_id = location_id
        output.trip_id = trip_id
        output.stop_sequence = stop_sequence
        output.stop_headsign = stop_headsign
        output.pickup_type = pickup_type
        output.drop_off_type = drop_off_type
        output.continuous_pickup = continuous_pickup
        output.continuous_drop_off = continuous_drop_off
        output.shape_dist_traveled = shape_dist_traveled
        output.timepoint = timepoint
        return output

    def __lt__(self, other: StopTime) -> bool:
        if self.stop_id is None:
            return True

        if other.stop_id is None:
            return False

        if self.stop_id != other.stop_id:
            return self.stop_id < other.stop_id

        if self.arrival_time is None:
            return True

        if other.arrival_time is None:
            return False

        return self.arrival_time < other.arrival_time

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, StopTime):
            return False

        if self.stop_id != other.stop_id:
            return False

        return self.arrival_time == other.arrival_time


@dataclass
class StopTimesDataset(GtfsStaticDataset):
    """Dataset for Stop Times."""

    stop_times: dict[str, dict[int, StopTime]]
    # only add stop_ids from here
    stops_filter: set[str] = field(default_factory=set)

    stop_times_ordered: SortedList = field(default_factory=SortedList)

    def __init__(self):
        self.stop_times = {}
        self.stops_filter = set()
        self.stop_times_ordered = SortedList()

    @override
    async def async_add_gtfs_data(self, zip_filelike):
        _LOGGER.debug("Adding gtfs data...")
        if len(self.stops_filter) == 0:
            _LOGGER.debug(
                "Aborting adding gtfs data as stops_filter is empty.")
            return

        async for line in self._get_gtfs_record_iter(zip_filelike, "stop_times.txt"):
            if getattr(line, "stop_id", None) in (self.stops_filter or set()):
                stop_time = StopTime(line)
                self.stop_times.setdefault(stop_time.trip_id, {})[
                    stop_time.stop_sequence
                ] = stop_time

                self.stop_times_ordered.add(stop_time)

    def get(self, trip_id, stop_sequence, *, default: StopTime | None = None):
        """Get Stop Time from Dataset."""
        by_trip_id = self.stop_times.get(trip_id)
        if by_trip_id is not None:
            return by_trip_id.get(stop_sequence, default)
        return default

    def search_by_stop_id(self, stop_id: str, start_time: GtfsArrivalDepartureTime | None = None, end_time: GtfsArrivalDepartureTime | None = None) -> list[StopTime]:
        search_time_start = StopTime.create_dummy_time(
            stop_id=stop_id, arrival_time=start_time) if start_time is not None else None
        search_time_end = StopTime.create_dummy_time(
            stop_id=stop_id, arrival_time=end_time) if end_time is not None else None

        output_slice = self.stop_times_ordered.search_range(
            search_time_start, search_time_end)

        return self.stop_times_ordered[output_slice]
