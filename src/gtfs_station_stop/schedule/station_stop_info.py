"""Station Stop Info"""

from typing import Self

from ..enums import LocationType, WheelchairBoarding
from .gtfs_row.stops import Stops


def try_parse_float(value: str | None) -> float | None:
    if value is None:
        return None

    try:
        return float(value)
    except ValueError:
        return None


class StationStopInfo:
    """Class for a Station/Stop Dataset Record"""

    def __init__(self, station_data: Stops, parent: Self | None = None) -> None:
        self.parent_station: str | None = station_data.parent_station
        self.location_type = station_data.location_type
        self.id: str = station_data.stop_id

        self.code: str | None = station_data.stop_code
        self.name: str | None = station_data.stop_name
        self.desc: str | None = station_data.stop_desc
        self.lat: float | None = station_data.stop_lat
        self.lon: float | None = station_data.stop_lon
        self.url: str | None = station_data.stop_url
        self.wheelchair_boarding: WheelchairBoarding = station_data.wheelchair_boarding
        self.platform_code: str | None = station_data.platform_code
        self.level_id: str | None = station_data.level_id
        self.parent = parent

    @staticmethod
    def _get_location_type(raw: str) -> LocationType:
        if raw == "":
            return LocationType.STOP
        return LocationType(int(raw))

    def __repr__(self):
        return f"{self.id}: {self.name}, lat: {self.lat}, long: {self.lon}{f', parent: {self.parent.id}' if self.parent else ''}"  # noqa E501
