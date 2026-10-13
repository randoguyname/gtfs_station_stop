from .static_dataset import GtfsStaticDataset
from ..station_stop_info import StationStopInfo
from ..gtfs_row.stops import Stops as StopRow


from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, override


@dataclass
class StationStopInfoDataset(GtfsStaticDataset):
    """Dataset class for Station/Stop Info."""

    station_stop_infos: dict[str, StationStopInfo] = field(
        init=False, default_factory=dict)

    @override
    async def async_add_gtfs_data(self, resource):
        async for line in self._get_gtfs_record_iter(resource.path, "stops.txt", StopRow):
            stop_id = line.stop_id
            parent = None
            if line.parent_station is not None:
                parent = self.station_stop_infos.get(line.parent_station)

            self.station_stop_infos[stop_id] = StationStopInfo(line, parent)

    @override
    def __getitem__(self, key) -> StationStopInfo:
        return self.station_stop_infos[key]

    def get_stop_ids(self) -> Iterable[str]:
        """Get all stop IDs."""
        return self.station_stop_infos.keys()

    def get(self, key: Any, default: Any | None = None):
        """Get a stop by ID or a default."""
        return self.station_stop_infos.get(key, default)
