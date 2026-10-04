"""Schedule"""

import os
import tempfile
from asyncio import TaskGroup, Lock
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from os import PathLike
from pathlib import Path
from re import Pattern, search

import aiofiles
from aiohttp import ClientSession
from yarl import URL
import logging

from zipwire import AsyncRemoteZip
from zipwire.backends import AiohttpReader

from .arrival import Arrival
from .calendar import Calendar
from .helpers import is_url, date_range
from .route_info import RouteInfoDataset
from .static_dataset import (
    GtfsStaticDataset,
    async_factory,
)
from .station_stop_info import StationStopInfo, StationStopInfoDataset
from .stop_times import StopTimesDataset, GtfsArrivalDepartureTime
from .trip_info import TripInfoDataset

DEFAULT_CHUNK_SIZE = 65536

_LOGGER = logging.getLogger(__name__)


class ScheduleRelationship(Enum):
    """
    Schedule Relationship.
    see https://gtfs.org/documentation/realtime/reference/#enum-schedulerelationship
    """

    SCHEDULED = 0
    SKIPPED = 1
    NO_DATA = 2
    UNSCHEDULED = 3

    @classmethod
    def _missing_(cls, value) -> ScheduleRelationship | None:
        if value is None:
            return cls.SCHEDULED
        return super()._missing_(value)

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
    resources: set[Path] = field(default_factory=set)
    zip_subfile_filter: Pattern[str] | str | None = field(default=None)

    download_locks: dict[URL | PathLike, Lock] = field(default_factory=dict)

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
                                url_or_path, # type: ignore
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
                                url_or_path, # type: ignore
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
        for resource in self.resources:
            _LOGGER.debug("Loading stop times %s", resource)
            await self.stop_times_ds.async_add_gtfs_data(resource)

    def get_stop_info(self, stop_id: str) -> StationStopInfo | None:
        """Get stop info by ID."""
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
                            route=trip_info.route_id,
                            trip=trip_info.trip_id,
                            time=at.timestamp(),
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
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        **kwargs,
    ) -> None:
        if url is not None:

            self.download_locks.setdefault(url, Lock())

            if self.download_locks[url].locked():
                _LOGGER.debug("_async_download_to_file_and_add_data: Waiting for another execution to complete...")
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

                    _LOGGER.debug("_async_download_to_file_and_add_data: Downloading file `%s` from url `%s`", filename, url)
                    with open(nested_dest / filename, "wb") as outfile:
                        await r.read_into(filename, outfile)

                    self.resources.add(nested_dest / filename)

                    _LOGGER.debug("_async_download_to_file_and_add_data: File successfully downloaded")

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
            if not os.path.exists(resource):
                _LOGGER.debug("Resource %s already deleted", resource)
                continue

            try:
                os.remove(resource)
                _LOGGER.debug("Successfully deleted resource: %s", resource)
            except Exception as e:
                _LOGGER.error(
                    "Failed to delete resource %s due to exception %s", resource, e)
        _LOGGER.debug("Temporary GTFS files deleted")


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
