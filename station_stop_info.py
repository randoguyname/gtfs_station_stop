"""Station Stop Info"""

import os
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from typing import Any, Self, override

from .static_dataset import GtfsStaticDataset


class LocationType(Enum):
    """
    Location Type.
    see https://gtfs.org/documentation/schedule/reference/#stopstxt
    """

    STOP = 0
    STATION = 1
    ENTRANCE = 2
    GENERIC_NODE = 3
    BOARDING_AREA = 4

    def __str__(self) -> str:
        if self == LocationType.STOP:
            return "stop"
        elif self == LocationType.STATION:
            return "station"
        elif self == LocationType.ENTRANCE:
            return "entrance"
        elif self == LocationType.GENERIC_NODE:
            return "generic_node"
        else: # self == LocationType.BOARDING_AREA:
            return "boarding_area"


class WheelchairBoarding(Enum):
    NO_INFORMATION = 0
    ACCESSIBLE = 1
    INACCESSIBLE = 2

    def __str__(self) -> str:
        if self == WheelchairBoarding.NO_INFORMATION:
            return "no_information"
        elif self == WheelchairBoarding.ACCESSIBLE:
            return "accessible"
        else: # self == WheelchairBoarding.INACCESSIBLE:
            return "inaccessible"

    @classmethod
    def from_data(cls, data: str | int | None) -> WheelchairBoarding:
        if data is None or (type(data) == str and len(data) == 0) or data == 0:
            return WheelchairBoarding.NO_INFORMATION
        try:
            val = int(data)
        except ValueError:
            return WheelchairBoarding.NO_INFORMATION

        if val == 1:
            return WheelchairBoarding.ACCESSIBLE
        elif val == 2:
            return WheelchairBoarding.INACCESSIBLE
        else:
            return WheelchairBoarding.NO_INFORMATION


def try_parse_float(value: str | None) -> float | None:
    if value is None:
        return None

    try:
        return float(value)
    except ValueError:
        return None


class StationStopInfo:
    """Class for a Station/Stop Dataset Record"""

    def __init__(self, station_data, parent: Self | None = None) -> None:
        self.parent_station: str | None = getattr(
            station_data, "parent_station", None)
        self.location_type = StationStopInfo._get_location_type(
            getattr(station_data, "location_type", "")
        )
        self.id: str = station_data.stop_id
        self.code: str | None = getattr(station_data, "stop_code", None)
        self.name: str | None = getattr(station_data, "stop_name", None)
        self.desc: str | None = getattr(station_data, "stop_desc", None)
        self.lat: float | None = try_parse_float(
            getattr(station_data, "stop_lat", None))
        self.lon: float | None = try_parse_float(
            getattr(station_data, "stop_lon", None))
        self.url: str | None = getattr(station_data, "stop_url", None)
        self.wheelchair_boarding: WheelchairBoarding = WheelchairBoarding.from_data(
            getattr(station_data, "wheelchair_boarding", None))
        self.platform_code: str | None = getattr(
            station_data, "platform_code", None)
        self.level_id: str | None = getattr(station_data, "level_id", None)
        self.parent = parent

    @staticmethod
    def _get_location_type(raw: str) -> LocationType:
        if raw == "":
            return LocationType.STOP
        return LocationType(int(raw))

    def __repr__(self):
        return f"{self.id}: {self.name}, lat: {self.lat}, long: {self.lon}{f', parent: {self.parent.id}' if self.parent else ''}"  # noqa E501


@dataclass
class StationStopInfoDataset(GtfsStaticDataset):
    """Dataset class for Station/Stop Info."""

    station_stop_infos: dict[str, StationStopInfo]

    def __init__(self):
        self.station_stop_infos = {}

    @override
    async def async_add_gtfs_data(self, zip_filelike):
        async for line in self._get_gtfs_record_iter(zip_filelike, "stops.txt"):
            stop_id = line.stop_id
            parent = None
            if hasattr(line, "parent_station"):
                parent = self.station_stop_infos.get(line.parent_station)
            self.station_stop_infos[stop_id] = StationStopInfo(line, parent)

    def get_stop_ids(self) -> Iterable[str]:
        """Get all stop IDs."""
        return self.station_stop_infos.keys()

    def __getitem__(self, key) -> StationStopInfo:
        return self.station_stop_infos[key]

    def get(self, key: Any, default: Any | None = None):
        """Get a stop by ID or a default."""
        return self.station_stop_infos.get(key, default)
