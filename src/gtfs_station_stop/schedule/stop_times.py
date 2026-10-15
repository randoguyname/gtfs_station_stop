"""Stop Times Dataset."""

from dataclasses import dataclass
from typing import Self, override
from functools import total_ordering

from .gtfs_arrival_departure_time import GtfsArrivalDepartureTime

from ..enums import DropOffType, PickupType, Timepoint, ContinuousDropOffType, ContinuousPickupType
from .gtfs_row.stop_times import StopTimes


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
    start_pickup_drop_off_window: GtfsArrivalDepartureTime | None
    end_pickup_drop_off_window: GtfsArrivalDepartureTime | None

    pickup_type: PickupType
    drop_off_type: DropOffType
    continuous_pickup: ContinuousPickupType
    continuous_drop_off: ContinuousDropOffType

    shape_dist_traveled: float
    timepoint: Timepoint

    def __init__(self, stop_times_data: StopTimes) -> None:
        self.trip_id = stop_times_data.trip_id

        self.arrival_time = stop_times_data.arrival_time

        self.departure_time = stop_times_data.departure_time

        self.stop_id = stop_times_data.stop_id
        self.location_group_id = stop_times_data.location_group_id
        self.location_id = stop_times_data.location_id

        self.stop_sequence = stop_times_data.stop_sequence
        self.stop_headsign = stop_times_data.stop_headsign
        self.start_pickup_drop_off_window = stop_times_data.start_pickup_drop_off_window
        self.end_pickup_drop_off_window = stop_times_data.end_pickup_drop_off_window

        self.pickup_type = stop_times_data.pickup_type
        self.drop_off_type = stop_times_data.drop_off_type
        self.continuous_pickup = stop_times_data.continuous_pickup
        self.continuous_drop_off = stop_times_data.continuous_drop_off

        self.shape_dist_traveled = stop_times_data.shape_dist_traveled or 0.0
        self.timepoint = stop_times_data.timepoint or Timepoint.EXACT

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
        continuous_pickup: ContinuousPickupType = ContinuousPickupType.NO_PICKUP_AVAILABLE,
        continuous_drop_off: ContinuousDropOffType = ContinuousDropOffType.NO_DROP_OFF_AVAILABLE,
        shape_dist_traveled: float = 0,
        timepoint: Timepoint = Timepoint.EXACT,
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
