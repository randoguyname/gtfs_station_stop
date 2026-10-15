from dataclasses import dataclass, field
from typing import override
import logging

from ..gtfs_arrival_departure_time import GtfsArrivalDepartureTime
from .static_dataset import GtfsStaticDataset
from ..stop_times import StopTime
from ...sorted_list import SortedList
from ..gtfs_row.stop_times import StopTimes as StopTimeRow


_LOGGER = logging.getLogger(__name__)


@dataclass
class StopTimesDataset(GtfsStaticDataset):
    """Dataset for Stop Times."""

    stop_times: dict[str, dict[int, StopTime]] = field(
        default_factory=dict, init=False)

    # only add stop_ids from here
    stops_filter: set[str] = field(default_factory=set, init=False)

    stop_times_ordered: SortedList[StopTime] = field(
        default_factory=SortedList, init=False)

    @override
    async def async_add_gtfs_data(self, resource):
        _LOGGER.debug("Adding gtfs data...")
        if len(self.stops_filter) == 0:
            _LOGGER.debug(
                "Aborting adding gtfs data as stops_filter is empty.")
            return

        prev_first_column: str | None = None

        async for line in self._get_gtfs_record_iter(resource.path, "stop_times.txt", StopTimeRow):
            if resource.sorted_asc_by_first_column is None:
                if prev_first_column is None:
                    prev_first_column = line[0]
                else:
                    if line[0] < prev_first_column:
                        resource.sorted_asc_by_first_column = False

            if not getattr(line, "stop_id", None) in self.stops_filter:
                continue

            stop_time = StopTime(line)
            self.stop_times.setdefault(stop_time.trip_id, {})[
                stop_time.stop_sequence
            ] = stop_time

            self.stop_times_ordered.add(stop_time)

        if resource.sorted_asc_by_first_column is None:
            resource.sorted_asc_by_first_column = True

    def get(self, trip_id: str, stop_sequence: int, *, default: StopTime | None = None):
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

    def clear(self) -> None:
        self.stop_times.clear()
        self.stop_times_ordered.clear()
