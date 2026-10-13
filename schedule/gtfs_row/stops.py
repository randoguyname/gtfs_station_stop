from typing import Iterable, override
from ...enums import LocationType, WheelchairBoarding, StopAccess
from .base import GtfsRowTuple


class Stops(GtfsRowTuple):
    _stop_id_idx: int
    _stop_code_idx: int | None = None
    _stop_name_idx: int | None = None
    _tts_stop_name_idx: int | None = None
    _stop_desc_idx: int | None = None
    _stop_lat_idx: int | None = None
    _stop_lon_idx: int | None = None
    _zone_id_idx: int | None = None
    _stop_url_idx: int | None = None
    _location_type_idx: int | None = None
    _parent_station_idx: int | None = None
    _stop_timezone_idx: int | None = None
    _wheelchair_boarding_idx: int | None = None
    _level_id_idx: int | None = None
    _platform_code_idx: int | None = None
    _stop_access_idx: int | None = None

    @staticmethod
    @override
    def make_named_tuple(name: str, headers: Iterable[str]) -> type[Stops]:
        header_dict = {}

        for index, header in enumerate(headers):
            match header:
                case "stop_id":
                    header_dict["_stop_id_idx"] = index
                case "stop_code":
                    header_dict["_stop_code_idx"] = index
                case "stop_name":
                    header_dict["_stop_name_idx"] = index
                case "tts_stop_name":
                    header_dict["_tts_stop_name_idx"] = index
                case "stop_desc":
                    header_dict["_stop_desc_idx"] = index
                case "stop_lat":
                    header_dict["_stop_lat_idx"] = index
                case "stop_lon":
                    header_dict["_stop_lon_idx"] = index
                case "zone_id":
                    header_dict["_zone_id_idx"] = index
                case "stop_url":
                    header_dict["_stop_url_idx"] = index
                case "location_type":
                    header_dict["_location_type_idx"] = index
                case "parent_station":
                    header_dict["_parent_station_idx"] = index
                case "stop_timezone":
                    header_dict["_stop_timezone_idx"] = index
                case "wheelchair_boarding":
                    header_dict["_wheelchair_boarding_idx"] = index
                case "level_id":
                    header_dict["_level_id_idx"] = index
                case "platform_code":
                    header_dict["_platform_code_idx"] = index
                case "stop_access":
                    header_dict["_stop_access_idx"] = index

        return type(name, (Stops,), header_dict)

    @property
    def stop_id(self) -> str:
        return self[self._stop_id_idx]

    @property
    def stop_code(self) -> str | None:
        if self._stop_code_idx is None:
            return None

        return self[self._stop_code_idx]

    @property
    def stop_name(self) -> str | None:
        if self._stop_name_idx is None:
            return None

        return self[self._stop_name_idx]

    @property
    def tts_stop_name(self) -> str | None:
        if self._tts_stop_name_idx is None:
            return None

        return self[self._tts_stop_name_idx]

    @property
    def stop_desc(self) -> str | None:
        if self._stop_desc_idx is None:
            return None

        return self[self._stop_desc_idx]

    @property
    def stop_lat(self) -> float | None:
        if self._stop_lat_idx is None:
            return None

        lat = self[self._stop_lat_idx]

        if lat is None:
            return None

        return float(lat)

    @property
    def stop_lon(self) -> float | None:
        if self._stop_lon_idx is None:
            return None

        lon = self[self._stop_lon_idx]

        if lon is None:
            return None

        return float(lon)

    @property
    def zone_id(self) -> str | None:
        if self._zone_id_idx is None:
            return None

        return self[self._zone_id_idx]

    @property
    def stop_url(self) -> str | None:
        if self._stop_url_idx is None:
            return None

        return self[self._stop_url_idx]

    @property
    def location_type(self) -> LocationType:
        if self._location_type_idx is None:
            return LocationType(None)

        return LocationType(self[self._location_type_idx])

    @property
    def parent_station(self) -> str | None:
        if self._parent_station_idx is None:
            return None

        return self[self._parent_station_idx]

    @property
    def stop_timezone(self) -> str | None:
        if self._stop_timezone_idx is None:
            return None

        return self[self._stop_timezone_idx]

    @property
    def wheelchair_boarding(self) -> WheelchairBoarding:
        if self._wheelchair_boarding_idx is None:
            return WheelchairBoarding(None)

        return WheelchairBoarding(self[self._wheelchair_boarding_idx])

    @property
    def level_id(self) -> str | None:
        if self._level_id_idx is None:
            return None

        return self[self._level_id_idx]

    @property
    def platform_code(self) -> str | None:
        if self._platform_code_idx is None:
            return None

        return self[self._platform_code_idx]

    @property
    def stop_access(self) -> StopAccess:
        if self._stop_access_idx is None:
            return StopAccess(None)

        return StopAccess(self[self._stop_access_idx])
