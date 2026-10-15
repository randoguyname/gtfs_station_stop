from typing import Iterable, override

from ...enums import CarsAllowed, BikesAllowed, WheelchairBoarding, DirectionID
from .base import GtfsRowTuple


class Trips(GtfsRowTuple):
    _trip_id_idx: int
    _route_id_idx: int
    _service_id_idx: int
    _trip_headsign_idx: int | None = None
    _trip_short_name_idx: int | None = None
    _direction_id_idx: int | None = None
    _block_id_idx: int | None = None
    _shape_id_idx: int | None = None
    _wheelchair_accessible_idx: int | None = None
    _bikes_allowed_idx: int | None = None
    _cars_allowed_idx: int | None = None
    _safe_duration_factor_idx: int | None = None
    _safe_duration_offset_idx: int | None = None

    @staticmethod
    @override
    def make_named_tuple(name: str, headers: Iterable[str]) -> type[Trips]:
        header_dict = {}

        for index, header in enumerate(headers):
            match header:
                case "trip_id":
                    header_dict["_trip_id_idx"] = index
                case "route_id":
                    header_dict["_route_id_idx"] = index
                case "service_id":
                    header_dict["_service_id_idx"] = index
                case "trip_headsign":
                    header_dict["_trip_headsign_idx"] = index
                case "trip_short_name":
                    header_dict["_trip_short_name_idx"] = index
                case "direction_id":
                    header_dict["_direction_id_idx"] = index
                case "block_id":
                    header_dict["_block_id_idx"] = index
                case "shape_id":
                    header_dict["_shape_id_idx"] = index
                case "wheelchair_accessible":
                    header_dict["_wheelchair_accessible_idx"] = index
                case "bikes_allowed":
                    header_dict["_bikes_allowed_idx"] = index
                case "cars_allowed":
                    header_dict["_cars_allowed_idx"] = index
                case "safe_duration_factor":
                    header_dict["_safe_duration_factor_idx"] = index
                case "safe_duration_offset":
                    header_dict["_safe_duration_offset_idx"] = index

        return type(name, (Trips,), header_dict)

    @property
    def trip_id(self) -> str:
        return self[self._trip_id_idx].replace("_", "+")

    @property
    def route_id(self) -> str:
        return self[self._route_id_idx]

    @property
    def service_id(self) -> str:
        return self[self._service_id_idx]

    @property
    def trip_headsign(self) -> str | None:
        if self._trip_headsign_idx is None:
            return None

        return self[self._trip_headsign_idx]

    @property
    def trip_short_name(self) -> str | None:
        if self._trip_short_name_idx is None:
            return None

        return self[self._trip_short_name_idx]

    @property
    def direction_id(self) -> DirectionID | None:
        if self._direction_id_idx is None:
            return None

        return DirectionID.parse(self[self._direction_id_idx])

    @property
    def block_id(self) -> str | None:
        if self._block_id_idx is None:
            return None

        return self[self._block_id_idx]

    @property
    def shape_id(self) -> str | None:
        if self._shape_id_idx is None:
            return None

        return self[self._shape_id_idx]

    @property
    def wheelchair_accessible(self) -> WheelchairBoarding:
        if self._wheelchair_accessible_idx is None:
            return WheelchairBoarding(None)

        return WheelchairBoarding(self[self._wheelchair_accessible_idx])

    @property
    def bikes_allowed(self) -> BikesAllowed:
        if self._bikes_allowed_idx is None:
            return BikesAllowed(None)

        return BikesAllowed(self[self._bikes_allowed_idx])

    @property
    def cars_allowed(self) -> CarsAllowed:
        if self._cars_allowed_idx is None:
            return CarsAllowed(None)

        return CarsAllowed(self[self._cars_allowed_idx])

    @property
    def safe_duration_factor(self) -> float | None:
        if self._safe_duration_factor_idx is None:
            return None

        factor = self[self._safe_duration_factor_idx]

        if factor is None:
            return None

        return float(factor)

    @property
    def safe_duration_offset(self) -> float | None:
        if self._safe_duration_offset_idx is None:
            return None

        offset = self[self._safe_duration_offset_idx]

        if offset is None:
            return None

        return float(offset)
