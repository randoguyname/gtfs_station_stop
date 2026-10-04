"""Helpers"""

import csv
import io
import os
from pathlib import Path
import tempfile
from collections.abc import Generator
from collections import namedtuple
from datetime import datetime as dt, date, timedelta
from typing import IO, Any, AsyncGenerator, Callable, Literal, TypeVar, TypeVarTuple, overload, override, Generator
from urllib.parse import urlparse
from zipfile import ZipFile
from logging import getLogger

import aiofiles
import aiohttp
from google.transit import gtfs_realtime_pb2
from yarl import URL

_LOGGER = getLogger(__name__)


class GtfsDialect(csv.excel):
    """Dialect for GTFS files."""

    skipinitialspace = True

def is_none_or_ends_at(
    alert: gtfs_realtime_pb2.Alert, at_time: float | dt | None = None
):
    """Returns the 'ends at' time, else returns None if not active."""
    at_time_: dt = dt.fromtimestamp(at_time) \
        if isinstance(at_time, float) \
        else dt.now() if at_time is None \
        else at_time  # type: ignore

    for time_range in alert.active_period:
        start: dt = (
            dt.fromtimestamp(time_range.start)
            if time_range.HasField("start")
            else dt.min
        )
        end: dt = (
            dt.fromtimestamp(time_range.end) if time_range.HasField(
                "end") else dt.max
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


@overload
async def gtfs_record_iter(zip_file: URL, target_txt: str, session: aiohttp.ClientSession) -> AsyncGenerator[Any]:
    yield tuple()


@overload
async def gtfs_record_iter(zip_file: os.PathLike, target_txt: str) -> AsyncGenerator[Any]:
    yield tuple()


async def gtfs_record_iter(
    zip_file: os.PathLike | URL | IO[bytes],
    target_txt: str,
    session: aiohttp.ClientSession | None = None,
    headers: dict[str, str] | None = None
) -> AsyncGenerator[Any]:
    """Generates a line from a given GTFS table. Can handle local files or URLs."""

    zip_file_path_or_bytes: os.PathLike | IO[bytes]

    # If the data is a url, make the request for the file resource.
    if is_url(zip_file):
        _LOGGER.debug("gtfs_record_iter: url detected; downloading file...")
        assert session is not None
        # Make the request, check for good return code, and convert to IO object.
        # As GTFS Static Data updates rarely, (most providers recommend pulling this
        # once per day), we will use a cache to minimize unnecessary checks.
        
        async with session.get(zip_file, headers=headers) as resp: # type: ignore
            if 200 <= resp.status < 400:
                _LOGGER.debug(
                    "gtfs_record_iter: file response received. Writing output...")
                # good req
                zip_file_path_or_bytes = Path(tempfile.gettempdir(
                ), "/gtfs_station_stop", f"{hex(hash(zip_file))[2:]}.zip")

                async with aiofiles.open(zip_file_path_or_bytes, "wb") as outfile:
                    async for chunk in resp.content.iter_chunked(1024):
                        await outfile.write(chunk)

                _LOGGER.debug("gtfs_record_iter: Output file written.")
            else:
                raise ConnectionRefusedError
    else:
        zip_file_path_or_bytes = zip_file  # type: ignore

    with ZipFile(zip_file_path_or_bytes, "r") as z:
        _LOGGER.debug("gtfs_record_iter: Zip file opened")

        # Find the *.txt file
        first_or_none: str | None = next(
            (name for name in z.namelist() if name == target_txt), None
        )
        if first_or_none is None:
            return

        # Create the dictionary of IDs, parents should precede the children
        with (
            z.open(first_or_none, "r") as f,
            io.TextIOWrapper(f, encoding="utf-8-sig") as buf,
        ):
            _LOGGER.debug("gtfs_record_iter: opened file %s of %s, reading rows...",
                          first_or_none, zip_file_path_or_bytes.__repr__())
            reader = csv.reader(buf, delimiter=",", dialect=GtfsDialect)

            csv_headers: list[str] = [header.strip() for header in next(reader)]

            GTFSRowTuple = namedtuple("GTFSRow", csv_headers)

            for row in reader:
                yield GTFSRowTuple(*[item.strip() for item in row])


def date_range(start: date, end: date) -> Generator[date]:
    days = int((end - start).days) + 1

    for i in range(days):
        yield start + timedelta(i)
