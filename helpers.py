"""Helpers"""

import csv
import io
import os
from pathlib import Path
import tempfile
from collections.abc import Generator
from collections import namedtuple
from datetime import datetime, date, timedelta
from typing import IO, Any, AsyncGenerator, Callable, Literal, TypeVar, TypeVarTuple, overload, override, Generator
from urllib.parse import urlparse
from zipfile import ZipFile, ZipInfo
from logging import getLogger
import time

import aiofiles
import aiohttp
from google.transit import gtfs_realtime_pb2
from google.transit.gtfs_realtime_pb2 import TripUpdate
from yarl import URL
from .schedule.gtfs_row.base import GtfsRowTuple

_LOGGER = getLogger(__name__)


class GtfsDialect(csv.excel):
    """Dialect for GTFS files."""

    skipinitialspace = True


@overload
def as_datetime(time: float | datetime | None,
                now_if_none: Literal[True] = True) -> datetime: ...


@overload
def as_datetime(time: float | datetime | None,
                now_if_none: Literal[False] = False) -> datetime | None: ...


def as_datetime(time: float | datetime | None, now_if_none: bool = True) -> datetime | None:
    if isinstance(time, float) or isinstance(time, int):
        return datetime.fromtimestamp(time)

    if time is None:
        return datetime.now() if now_if_none else None

    return time


@overload
def as_timedelta(time: float | timedelta | None,
                 zero_if_none: Literal[True] = True) -> timedelta: ...


@overload
def as_timedelta(time: float | timedelta | None,
                 zero_if_none: Literal[False] = False) -> timedelta | None: ...


def as_timedelta(time: float | timedelta | None, zero_if_none: bool = True) -> timedelta | None:
    if isinstance(time, float) or isinstance(time, int):
        return timedelta(seconds=time)

    if time is None:
        return timedelta() if zero_if_none else None

    return time


def is_none_or_ends_at(
    alert: gtfs_realtime_pb2.Alert, at_time: float | datetime | None = None
):
    """Returns the 'ends at' time, else returns None if not active."""

    at_time_ = as_datetime(at_time)

    for time_range in alert.active_period:
        start: datetime = (
            datetime.fromtimestamp(time_range.start)
            if time_range.HasField("start")
            else datetime.min
        )
        end: datetime = (
            datetime.fromtimestamp(time_range.end) if time_range.HasField(
                "end") else datetime.max
        )
        if start <= at_time_ <= end:
            return end

    return None


def get_as_number[T](
    # type: ignore
    d: dict[Any, Any] | tuple, key: Any, to_type: Callable[[Any], T], default: T = 0
) -> T:
    """Get a key from a dictionary or named tuple, or return a Number type default."""
    if isinstance(d, tuple):
        value = getattr(d, key, default)
        try:
            return to_type(value)
        except ValueError:
            return default

    try:
        tmp = d.get(key)
        if not bool(tmp):
            tmp = default
        return to_type(tmp)
    except ValueError:
        return default


@overload
def is_url(url: IO) -> Literal[False]: ...


@overload
def is_url(url: str) -> bool: ...


@overload
def is_url(url: URL) -> Literal[True]: ...


@overload
def is_url(url: os.PathLike) -> Literal[False]: ...


def is_url(url: Any) -> bool:
    """Check if a str is a URL."""
    try:
        result = urlparse(str(url))
        return all([result.scheme, result.netloc])
    except (ValueError, AttributeError):
        return False


async def open_gtfs_record(
    zip_file: os.PathLike | URL | IO[bytes],
    target_txt: str,
    session: aiohttp.ClientSession | None = None,
    headers: dict[str, str] | None = None
) -> tuple[IO[bytes], ZipInfo]:
    zip_file_path_or_bytes: os.PathLike | IO[bytes]

    # If the data is a url, make the request for the file resource.
    if is_url(zip_file):
        _LOGGER.debug(
            "open_gtfs_record: url detected; downloading file...")
        assert session is not None
        # Make the request, check for good return code, and convert to IO object.
        # As GTFS Static Data updates rarely, (most providers recommend pulling this
        # once per day), we will use a cache to minimize unnecessary checks.

        async with session.get(zip_file, headers=headers) as resp:  # type: ignore
            if 200 <= resp.status < 400:
                _LOGGER.debug(
                    "open_gtfs_record: file response received. Writing output...")
                # good req
                zip_file_path_or_bytes = Path(tempfile.gettempdir(
                ), "/gtfs_station_stop", f"{hex(hash(zip_file))[2:]}.zip")

                async with aiofiles.open(zip_file_path_or_bytes, "wb") as outfile:
                    async for chunk in resp.content.iter_chunked(1024):
                        await outfile.write(chunk)

                _LOGGER.debug("open_gtfs_record: Output file written.")
            else:
                raise ConnectionRefusedError
    else:
        zip_file_path_or_bytes = zip_file  # type: ignore

    with ZipFile(zip_file_path_or_bytes, "r") as z:
        _LOGGER.debug("open_gtfs_record: Zip file opened")

        # Find the *.txt file
        first_or_none: ZipInfo | None = next(
            (name for name in z.infolist() if name.filename == target_txt), None
        )

        assert first_or_none is not None

        return z.open(first_or_none, "r"), first_or_none


@overload
def gtfs_record_iter[T: GtfsRowTuple](zip_file: URL, target_txt: str, tuple_type: type[T], session: aiohttp.ClientSession) -> AsyncGenerator[T]:
    ...


@overload
def gtfs_record_iter[T: GtfsRowTuple](zip_file: os.PathLike[str], target_txt: str, tuple_type: type[T]) -> AsyncGenerator[T]:
    ...


async def gtfs_record_iter[T: GtfsRowTuple](
    zip_file: os.PathLike[str] | URL | IO[bytes],
    target_txt: str,
    tuple_type: type[T],
    session: aiohttp.ClientSession | None = None,
    headers: dict[str, str] | None = None,
) -> AsyncGenerator[T]:
    """Generates a line from a given GTFS table. Can handle local files or URLs."""

    with ((await open_gtfs_record(zip_file, target_txt, session, headers))[0] as f,
          io.TextIOWrapper(f, encoding="utf-8-sig") as buf):
        reader = csv.reader(buf, delimiter=",", dialect=GtfsDialect)

        csv_headers: list[str] = [header.strip()
                                  for header in next(reader)]

        tuple_t = tuple_type.make_named_tuple(
            "GTFSRow", csv_headers)

        for row in reader:
            yield tuple_t([item.strip() for item in row])


def date_range(start: date, end: date) -> Generator[date]:
    days = int((end - start).days) + 1

    for i in range(days):
        yield start + timedelta(i)


def realtime_get_current_trip_position(
    trip_update: TripUpdate,
    *,
    current_time: float | None = None,
    max_allowed_seconds: float = 180,
) -> str | None:
    current_pos: TripUpdate.StopTimeUpdate | None = None

    if current_time is None:
        current_time = time.time()

    for stu in trip_update.stop_time_update:
        delta = abs(current_time - stu.arrival.time)
        if delta < max_allowed_seconds and (
            current_pos is None
            or delta < abs(current_time - current_pos.arrival.time)
        ):
            current_pos = stu

    if current_pos is not None:
        return current_pos.stop_id

    return None


def read_gtfs_line(line: str | bytes) -> tuple[str, ...]:
    if isinstance(line, bytes):
        line = line.decode("utf-8-sig")

    reader = csv.reader([line], dialect=GtfsDialect)

    return tuple(next(reader))


def gtfs_binary_search[T: tuple](file: IO[bytes], start_offset: int, end_offset: int, search_term: str, headers: type[T]) -> Generator[T]:
    # start and end offsets must always be at a file or line boundary
    # never check a line that begins before start offset, or one that starts after or at end_offset

    if start_offset == end_offset:  # search must be over
        return

    middle = (start_offset + end_offset) // 2

    file.seek(middle)

    file.readline()  # purge the end of the previous line; should never fail unless middle == end_offset

    # now, offset > start_offset, but offset could be ge end_offset

    offset_before = file.tell()

    if offset_before >= end_offset:
        # there is at least one line starting at start_offset
        # very unlikely that there are many lines, so linear search is easiest here
        file.seek(start_offset)
        while file.tell() < end_offset:
            line_bytes = file.readline()
            line = headers(*read_gtfs_line(line_bytes))

            if line[0] == search_term:  # TODO: comparison
                yield line

        # has reached end offset, search is complete
        return

    # now, offset must be at a newline that is neither start nor end offset

    # t.f., there is a line beginning at start_offset and a line beginning at the cur offset. There are at least 2 lines

    line_bytes = file.readline()  # get a full line

    line = headers(*read_gtfs_line(line_bytes))

    offset_after = file.tell()

    # now, we have a full line

    # case 1: equality
    if line[0] == search_term:
        # if the line is equal, we must yield it and yield from either side
        yield line

        # yield from before is easy, because there is necessarily at least one line before
        yield from gtfs_binary_search(file, start_offset, end_offset=offset_before, search_term=search_term, headers=headers)

        if offset_after == offset_before:
            # then there are no more; all have been yielded and the search is complete
            return

        yield from gtfs_binary_search(file, start_offset=offset_after, end_offset=end_offset, search_term=search_term, headers=headers)
    # case 2: search term later
    elif line[0] < search_term:
        # must start at offset_after, end at end_offset
        # if offset_after == end_offset, then the line is not present
        if offset_after == end_offset:
            return

        # otherwise, there is at least one line between offset_after and end_offset
        yield from gtfs_binary_search(file, start_offset=offset_after, end_offset=end_offset, search_term=search_term, headers=headers)
    # case 3: search term earlier
    else:
        # must start before offset_before
        # there is at least one line starting at start_offset
        yield from gtfs_binary_search(file, start_offset, end_offset=offset_before, search_term=search_term, headers=headers)
