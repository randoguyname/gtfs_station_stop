from typing import Iterable, override

from ..gtfs_arrival_departure_time import GtfsArrivalDepartureTime
from ...enums import PickupType, ContinuousPickupType, DropOffType, ContinuousDropOffType, Timepoint
from .base import GtfsRowTuple


class StopTimes(GtfsRowTuple):
    _trip_id_idx: int
    _arrival_time_idx: int | None = None
    _departure_time_idx: int | None = None
    _stop_id_idx: int | None = None
    _location_group_id_idx: int | None = None
    _location_id_idx: int | None = None
    _stop_sequence_idx: int
    _stop_headsign_idx: int | None = None
    _start_pickup_drop_off_window_idx: int | None = None
    _end_pickup_drop_off_window_idx: int | None = None
    _pickup_type_idx: int | None = None
    _drop_off_type_idx: int | None = None
    _continuous_pickup_idx: int | None = None
    _continuous_drop_off_idx: int | None = None
    _shape_dist_traveled_idx: int | None = None
    _timepoint_idx: int | None = None
    _pickup_booking_rule_id_idx: int | None = None
    _drop_off_booking_rule_id_idx: int | None = None

    @staticmethod
    @override
    def make_named_tuple(name: str, headers: Iterable[str]) -> type[StopTimes]:
        header_dict = {}

        for index, header in enumerate(headers):
            match header:
                case "trip_id":
                    header_dict["_trip_id_idx"] = index
                case "arrival_time":
                    header_dict["_arrival_time_idx"] = index
                case "departure_time":
                    header_dict["_departure_time_idx"] = index
                case "stop_id":
                    header_dict["_stop_id_idx"] = index
                case "location_group_id":
                    header_dict["_location_group_id_idx"] = index
                case "location_id":
                    header_dict["_location_id_idx"] = index
                case "stop_sequence":
                    header_dict["_stop_sequence_idx"] = index
                case "stop_headsign":
                    header_dict["_stop_headsign_idx"] = index
                case "start_pickup_drop_off_window":
                    header_dict["_start_pickup_drop_off_window_idx"] = index
                case "end_pickup_drop_off_window":
                    header_dict["_end_pickup_drop_off_window_idx"] = index
                case "pickup_type":
                    header_dict["_pickup_type_idx"] = index
                case "drop_off_type":
                    header_dict["_drop_off_type_idx"] = index
                case "continuous_pickup":
                    header_dict["_continuous_pickup_idx"] = index
                case "continuous_drop_off":
                    header_dict["_continuous_drop_off_idx"] = index
                case "shape_dist_traveled":
                    header_dict["_shape_dist_traveled_idx"] = index
                case "timepoint":
                    header_dict["_timepoint_idx"] = index
                case "pickup_boarding_rule_id":
                    header_dict["_pickup_boarding_rule_id_idx"] = index
                case "drop_off_boarding_rule_id":
                    header_dict["_drop_off_boarding_rule_id_idx"] = index

        return type(name, (StopTimes,), header_dict)

    @property
    def trip_id(self) -> str:
        return self[self._trip_id_idx]

    @property
    def arrival_time(self) -> GtfsArrivalDepartureTime | None:
        if self._arrival_time_idx is None:
            return None

        return GtfsArrivalDepartureTime.strptime(self[self._arrival_time_idx])

    @property
    def departure_time(self) -> GtfsArrivalDepartureTime | None:
        if self._departure_time_idx is None:
            return None

        return GtfsArrivalDepartureTime.strptime(self[self._departure_time_idx])

    @property
    def stop_id(self) -> str | None:
        if self._stop_id_idx is None:
            return None

        return self[self._stop_id_idx]

    @property
    def location_group_id(self) -> str | None:
        if self._location_group_id_idx is None:
            return None

        return self[self._location_group_id_idx]

    @property
    def location_id(self) -> str | None:
        if self._location_id_idx is None:
            return None

        return self[self._location_id_idx]

    @property
    def stop_sequence(self) -> int:
        return int(self[self._stop_sequence_idx])

    @property
    def stop_headsign(self) -> str | None:
        if self._stop_headsign_idx is None:
            return None

        return self[self._stop_headsign_idx]

    @property
    def start_pickup_drop_off_window(self) -> GtfsArrivalDepartureTime | None:
        if self._start_pickup_drop_off_window_idx is None:
            return None

        return GtfsArrivalDepartureTime.strptime(self[self._start_pickup_drop_off_window_idx])

    @property
    def end_pickup_drop_off_window(self) -> GtfsArrivalDepartureTime | None:
        if self._end_pickup_drop_off_window_idx is None:
            return None

        return GtfsArrivalDepartureTime.strptime(self[self._end_pickup_drop_off_window_idx])

    @property
    def pickup_type(self) -> PickupType:
        if self._pickup_type_idx is None:
            return PickupType(None)

        return PickupType(self[self._pickup_type_idx])

    @property
    def drop_off_type(self) -> DropOffType:
        if self._drop_off_type_idx is None:
            return DropOffType(None)

        return DropOffType(self[self._drop_off_type_idx])

    @property
    def continuous_drop_off(self) -> ContinuousDropOffType:
        if self._continuous_drop_off_idx is None:
            return ContinuousDropOffType(None)

        return ContinuousDropOffType(self[self._continuous_drop_off_idx])

    @property
    def continuous_pickup(self) -> ContinuousPickupType:
        if self._continuous_pickup_idx is None:
            return ContinuousPickupType(None)

        return ContinuousPickupType(self[self._continuous_pickup_idx])

    @property
    def shape_dist_traveled(self) -> float | None:
        if self._shape_dist_traveled_idx is None:
            return None

        return float(self[self._shape_dist_traveled_idx])

    @property
    def timepoint(self) -> Timepoint | None:
        if self._timepoint_idx is None:
            return None

        return Timepoint(self[self._timepoint_idx])

    @property
    def pickup_booking_rule_id(self) -> str | None:
        if self._pickup_booking_rule_id_idx is None:
            return None

        return self[self._pickup_booking_rule_id_idx]

    @property
    def drop_off_booking_rule_id(self) -> str | None:
        if self._drop_off_booking_rule_id_idx is None:
            return None

        return self[self._drop_off_booking_rule_id_idx]
