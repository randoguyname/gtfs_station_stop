"""GTFS Static Dataset Base Class."""

import asyncio
import inspect
import os
from abc import abstractmethod
from io import BytesIO
from typing import IO, Any

import aiofiles
from aiohttp import ClientSession
from yarl import URL

from .helpers import gtfs_record_iter, is_url


class GtfsStaticDataset:
    """
    Base class for GTFS Datasets.
    https://gtfs.org/documentation/schedule/reference/#dataset-files
    """

    def _get_gtfs_record_iter(self, zip_filelike: os.PathLike | URL, target_txt: str):
        return gtfs_record_iter(zip_filelike, target_txt)  # type: ignore

    @abstractmethod
    async def async_add_gtfs_data(self, zip_filelike: os.PathLike | URL) -> None:
        """Add GTFS Data."""
        raise NotImplementedError

    @abstractmethod
    def __getitem__(self, key) -> Any:
        """Get Dataset Item."""
        raise NotImplementedError


async def async_factory(
    gtfs_ds_or_class: type[GtfsStaticDataset] | GtfsStaticDataset,
    *gtfs_resource: os.PathLike,
    session: ClientSession | None = None,
    **kwargs,
) -> GtfsStaticDataset:
    """Create an empty dataset if a type is given"""
    gtfsds = (
        gtfs_ds_or_class()
        if inspect.isclass(gtfs_ds_or_class)
        and issubclass(gtfs_ds_or_class, GtfsStaticDataset)
        else gtfs_ds_or_class
    )

    for resource in gtfs_resource:
        await gtfsds.async_add_gtfs_data(resource)

    return gtfsds
