"""Schedule"""

import os
import tempfile
from asyncio import TaskGroup, Lock
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from os import PathLike
from pathlib import Path
from re import Pattern, search
from typing import Any
from functools import cache
import random

from aiohttp import ClientSession
from yarl import URL
import logging

from zipwire import AsyncRemoteZip
from zipwire.backends import AiohttpReader

from ..arrival import Arrival
from .static_dataset.station_stop_info import StationStopInfoDataset
from .static_dataset.stop_times import StopTimesDataset
from .static_dataset.calendar import Calendar
from ..helpers import is_url, date_range
from .static_dataset.route_info import RouteInfoDataset
from .static_dataset.static_dataset import (
    GtfsStaticDataset,
    async_factory,
)
from .station_stop_info import StationStopInfo
from ..realtime.station_stop import StationStop
from ..realtime.subscriber_identifier import RouteIdentifier, StationStopIdentifier
from .gtfs_arrival_departure_time import GtfsArrivalDepartureTime
from .static_dataset.trip_info import TripInfoDataset
from .gtfs_schedule_resource import GtfsScheduleResource
from ..trip_identifier import TripIdentifier
from .gtfs_row.stop_times import StopTimes

DEFAULT_CHUNK_SIZE = 65536

_LOGGER = logging.getLogger(__name__)


@dataclass(kw_only=True)
class GtfsSchedule:
    """GTFS Schedule."""

    calendar: Calendar = field(default_factory=Calendar)
    station_stop_info_ds: StationStopInfoDataset = field(
        default_factory=StationStopInfoDataset
    )
    trip_info_ds: TripInfoDataset = field(default_factory=TripInfoDataset)
    route_info_ds: RouteInfoDataset = field(default_factory=RouteInfoDataset)
    stop_times_ds: StopTimesDataset = field(default_factory=StopTimesDataset)
    download_dir_path: PathLike = Path(
        f"{tempfile.gettempdir()}/gtfs_station_stop")
    resources: set[GtfsScheduleResource] = field(default_factory=set)
    zip_subfile_filter: Pattern[str] | str | None = field(default=None)

    download_locks: dict[URL | PathLike, Lock] = field(default_factory=dict)
    _hash: int = field(init=False, repr=False,
                       default_factory=lambda: random.randint(0, 2_000_000))

    _trip_id_cache: dict[str, TripIdentifier] = field(init=False, repr=False,
                                                      default_factory=dict)

    def __hash__(self) -> int:
        return hash(self._hash)

    async def async_build_schedule(
        self,
        *gtfs_urls_or_paths: URL | PathLike,
        session: ClientSession | None = None,
        **kwargs,
    ) -> None:
        """Update the schedule given a set of URLs"""

        _LOGGER.debug("async_build_schedule: beginning..")
        close_session = False
        if session is None:
            session = ClientSession()
            close_session = True
        _LOGGER.debug("async_build_schedule: Building schedule...")

        try:
            os.makedirs(self.download_dir_path, exist_ok=True)
            async with TaskGroup() as tg:
                for url_or_path in gtfs_urls_or_paths:
                    # hash and stringify the URL
                    if is_url(url_or_path):
                        hash_str = hex(hash(str(url_or_path)) & 0xFFFFFFFF)[2:]
                        path = Path(self.download_dir_path) / f"{hash_str}.zip"
                        tg.create_task(
                            self._async_download_to_file_and_add_data(
                                tg,
                                url_or_path,  # type: ignore
                                path,
                                session=session,
                                **kwargs,
                            )
                        )
                    else:
                        tg.create_task(
                            self._async_download_to_file_and_add_data(
                                tg,
                                None,
                                url_or_path,  # type: ignore
                                session=session,
                                **kwargs,
                            )
                        )
        finally:
            if close_session:
                await session.close()

    async def async_load_stop_times(self, stops_filter: set[str] | None = None) -> None:
        """
        Async load stop times in stop_times.txt
        This operation should be delayed from schedule building as it can
        be time consuming and is not needed for many datasets.
        """
        self.stop_times_ds.stops_filter = stops_filter or set()

        self.stop_times_ds.clear()

        for resource in self.resources:
            _LOGGER.debug("Loading stop times %s", resource)
            await self.stop_times_ds.async_add_gtfs_data(resource)

    def get_stop_info(self, stop_id: str | StationStopIdentifier) -> StationStopInfo | None:
        """Get stop info by ID."""
        if isinstance(stop_id, StationStopIdentifier):
            return self.get_stop_info(stop_id.stop_id)

        return self.station_stop_info_ds.station_stop_infos.get(stop_id)

    def get_trip_headsign(self, trip_id: str) -> str:
        """Get Trip's Headsign."""
        trip_info = self.trip_info_ds.get_close_match(trip_id)
        if trip_info is not None and trip_info.trip_headsign is not None:
            return trip_info.trip_headsign
        return ""

    def get_route_color(self, route_id: str) -> str:
        """Get Trip's Route Color."""
        route_info = self.route_info_ds.get(route_id)
        if route_info is not None:
            return route_info.color or ""
        return ""

    def get_route_text_color(self, route_id: str) -> str:
        """Get Trip's Route Text Color."""
        route_info = self.route_info_ds.get(route_id)
        if route_info is not None:
            return route_info.text_color or ""
        return ""

    def get_route_type(self, route_id: str) -> str:
        """Get Trip's Route Type."""
        route_info = self.route_info_ds.get(route_id)
        if route_info is not None:
            return route_info.type.pretty_name()
        return ""

    def get_upcoming_arrivals(self, stop_id: str, delta: timedelta) -> list[Arrival]:
        """Get a list of scheduled arrivals from now until a time in the future."""
        return self.get_arrivals_between_times(
            stop_id, datetime.now(), datetime.now() + delta
        )

    def get_arrivals_between_times(
        self, stop_id: str, start: datetime, end: datetime
    ) -> list[Arrival]:
        """Get a list of scheduled arrivals."""
        arrivals: list[Arrival] = []
        _LOGGER.debug("Getting arrivals...")
        for stop_time in self.stop_times_ds.search_by_stop_id(
                stop_id,
                start_time=GtfsArrivalDepartureTime.from_time(start.time()),
                end_time=GtfsArrivalDepartureTime.from_time(end.time())):
            if (trip_info := self.trip_info_ds.get(stop_time.trip_id)) is None:
                continue

            for day in date_range(start.date(), end.date()):
                active_services = self.calendar.get_active_services(day)

                if not trip_info.service_id in [s.service_id for s in active_services]:
                    continue

                at = datetime(
                    year=day.year,
                    month=day.month,
                    day=day.day,
                    hour=getattr(stop_time.arrival_time, "hour"),
                    minute=getattr(stop_time.arrival_time, "minute"),
                    second=getattr(stop_time.arrival_time, "second"),
                )

                if start <= at <= end:
                    arrivals.append(
                        Arrival(
                            route_id=trip_info.route_id,
                            trip_id=trip_info.trip_id,
                            time=at,
                            stop_sequence=stop_time.stop_sequence,
                        )
                    )

        return arrivals

    def _get_required_datasets(self) -> list[GtfsStaticDataset]:
        return [
            self.calendar,
            self.station_stop_info_ds,
            self.trip_info_ds,
            self.route_info_ds,
        ]

    async def _async_download_to_file_and_add_data(
        self,
        task_group: TaskGroup,
        url: URL | None,
        target: Path,
        *,
        session: ClientSession | None = None,
    ) -> None:
        if url is not None:

            self.download_locks.setdefault(url, Lock())

            if self.download_locks[url].locked():
                _LOGGER.debug(
                    "_async_download_to_file_and_add_data: Waiting for another execution to complete...")
                await self.download_locks[url].acquire()
                _LOGGER.debug(
                    "_async_download_to_file_and_add_data: Download completed by another execution, returning early")
                self.download_locks[url].release()

                return

            close_session = False

            if session is None:
                session = ClientSession()
                close_session = True

            reader = AiohttpReader(str(url), session=session)

            async with (
                AsyncRemoteZip(reader) as r,
                self.download_locks[url],
            ):

                nested_dest = target.parent
                os.makedirs(nested_dest, exist_ok=True)

                for fileinfo in r.infolist():
                    if fileinfo.is_dir():
                        continue

                    filename = fileinfo.filename
                    if self.zip_subfile_filter is not None \
                            and not search(self.zip_subfile_filter, filename):

                        continue

                    os.makedirs((nested_dest / filename).parent, exist_ok=True)

                    _LOGGER.debug(
                        "_async_download_to_file_and_add_data: Downloading file `%s` from url `%s`", filename, url)

                    path = nested_dest / filename

                    resource = GtfsScheduleResource(path)

                    # TODO: make this async
                    with open(nested_dest / filename, "wb") as outfile:
                        await r.read_into(filename, outfile)

                    self.resources.add(resource)

                    _LOGGER.debug(
                        "_async_download_to_file_and_add_data: File successfully downloaded")

            if close_session:
                await session.close()
        else:
            _LOGGER.debug(
                "_async_download_to_file_and_add_data: File already exists, loading data...")

        for resource in self.resources:
            for ds in self._get_required_datasets():
                task_group.create_task(async_factory(ds, resource))

    def __del__(self) -> None:
        _LOGGER.debug("Deleting temporary resource files...")
        for resource in self.resources:
            if not os.path.exists(resource.path):
                _LOGGER.debug("Resource %s already deleted", resource)
                continue

            try:
                os.remove(resource.path)
                _LOGGER.debug("Successfully deleted resource: %s", resource)
            except Exception as e:
                _LOGGER.error(
                    "Failed to delete resource %s due to exception %s", resource, e)
        _LOGGER.debug("Temporary GTFS files deleted")

    async def merge_with_realtime_data(self, arrivals: list[Arrival], station_stop: StationStop) -> list[Arrival]:
        # First, apply cancelations
        filtered_arrivals: list[Arrival] = []

        for arrival in arrivals:
            passed = True
            for details in station_stop.canceled_arrivals:
                if details.route_id is not None and details.route_id == arrival.route_id:
                    passed = False
                    break

                if details.trip_id is not None and details.trip_id == arrival.trip_id:
                    passed = False
                    break

            if passed:
                filtered_arrivals.append(arrival)

        # Then, handle updates

        for updated_arrival in station_stop.updated_arrivals:
            for arrival in filtered_arrivals:
                # must correspond to a list element
                if arrival.trip_id == updated_arrival.trip_id:
                    arrival.update_from(updated_arrival)
                    break

        # Finally, add new arrivals

        trip_identifiers = [await self.get_trip_identifier(
            arrival.trip_id) for arrival in filtered_arrivals]

        trip_identifiers = [
            trip_identifier for trip_identifier in trip_identifiers if trip_identifier is not None]

        for added_trip_id, added_arrival in station_stop.added_arrivals.items():
            # First, check to make sure the trip is not incorrect data (i.e. a duplicate of an existing static trip)

            added_trip_id = self.get_trip_id_missing_data(added_trip_id)

            if added_trip_id in trip_identifiers:
                idx = trip_identifiers.index(added_trip_id)
                filtered_arrivals[idx].update_from(added_arrival)
            else:
                filtered_arrivals.append(added_arrival)

        return filtered_arrivals

    async def get_trip_identifier(self, trip_id: str) -> TripIdentifier | None:
        if trip_id in self._trip_id_cache:
            return self._trip_id_cache[trip_id]

        lowest_stop_seq: StopTimes | None = None
        second_lowest_stop_seq: StopTimes | None = None
        for resource in self.resources:
            async for stop_time in self.stop_times_ds._gtfs_record_search_by_first_column(resource, "stop_times.txt", trip_id, StopTimes):
                if lowest_stop_seq is None:
                    lowest_stop_seq = stop_time
                    continue

                if second_lowest_stop_seq is None:
                    second_lowest_stop_seq = stop_time
                    continue

                if lowest_stop_seq.stop_sequence > stop_time.stop_sequence:
                    second_lowest_stop_seq = lowest_stop_seq
                    lowest_stop_seq = stop_time
                    continue

                if second_lowest_stop_seq.stop_sequence > stop_time.stop_sequence:
                    second_lowest_stop_seq = stop_time
                    continue

        if lowest_stop_seq is None or second_lowest_stop_seq is None:
            _LOGGER.warning(
                "get_trip_identifier: Failed to get trip identifier for trip_id: %s", trip_id)
            return None

        start_time = lowest_stop_seq.arrival_time

        if start_time is None:
            _LOGGER.warning(
                "get_trip_identifier: Failed to get trip identifier for trip_id: %s", trip_id)
            return None

        trip_info = self.trip_info_ds.get_close_match(trip_id)

        trip_identifier = TripIdentifier(
            trip_id=trip_id,
            start_time=start_time,
            route_id=RouteIdentifier(
                trip_info.route_id) if trip_info is not None else None,
            direction_id=trip_info.direction_id if trip_info is not None else None,
            stop_id_1=self.get_station_stop_identifier(
                lowest_stop_seq.stop_id) if lowest_stop_seq and lowest_stop_seq.stop_id is not None else None,
            stop_id_2=self.get_station_stop_identifier(
                second_lowest_stop_seq.stop_id) if second_lowest_stop_seq and second_lowest_stop_seq.stop_id is not None else None,
        )

        self._trip_id_cache[trip_id] = trip_identifier

        return trip_identifier

    def get_station_stop_identifier(self, stop_id: str) -> StationStopIdentifier:
        stop_info = self.get_stop_info(stop_id)
        if stop_info is None:
            return StationStopIdentifier(stop_id)

        return StationStopIdentifier(
            stop_id,
            stop_info.location_type,
            stop_info.parent_station
        )

    def get_trip_id_missing_data(self, trip_id: TripIdentifier) -> TripIdentifier:
        return TripIdentifier(
            trip_id=trip_id.trip_id,
            start_time=trip_id.start_time,
            stop_id_1=self.get_station_stop_identifier(
                trip_id.stop_id_1.stop_id) if trip_id.stop_id_1 is not None else None,
            stop_id_2=self.get_station_stop_identifier(
                trip_id.stop_id_2.stop_id) if trip_id.stop_id_2 is not None else None,
            route_id=trip_id.route_id,
            direction_id=trip_id.direction_id,
        )


async def async_build_schedule(
    *gtfs_urls: os.PathLike,
    session: ClientSession | None = None,
    **kwargs,
) -> GtfsSchedule:
    """Build a schedule dataclass."""

    close_session: bool = False
    if session is None:
        session = ClientSession()
        close_session = True

    try:
        schedule = GtfsSchedule()
        await schedule.async_build_schedule(*gtfs_urls, session=session, **kwargs)
    finally:
        if close_session:
            await session.close()
    return schedule
