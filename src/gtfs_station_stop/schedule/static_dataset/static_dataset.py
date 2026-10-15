"""GTFS Static Dataset Base Class."""

import inspect
import os
from abc import abstractmethod
from typing import Any, AsyncGenerator, overload
from collections import namedtuple

from aiohttp import ClientSession
from yarl import URL

from ...helpers import gtfs_record_iter, open_gtfs_record, gtfs_binary_search, read_gtfs_line
from ..gtfs_schedule_resource import GtfsScheduleResource
from ..gtfs_row.base import GtfsRowTuple


class GtfsStaticDataset:
    """
    Base class for GTFS Datasets.
    https://gtfs.org/documentation/schedule/reference/#dataset-files
    """

    def _get_gtfs_record_iter[T: GtfsRowTuple](
            self,
            zip_filelike: os.PathLike[str] | URL,
            target_txt: str,
            tuple_type: type[T],
            session: ClientSession | None = None
    ):
        return gtfs_record_iter(
            zip_filelike,  # type: ignore
            target_txt,
            tuple_type=tuple_type,
            session=session,  # type: ignore
        )

    async def _gtfs_record_search_by_first_column[T: GtfsRowTuple](self, resource: GtfsScheduleResource, target_txt: str, search_term: str, tuple_type: type[T]) -> AsyncGenerator[T]:
        if not resource.sorted_asc_by_first_column:
            # perform a linear search if the dataset is not sorted
            async for line in self._get_gtfs_record_iter(resource.path, target_txt, tuple_type):
                if line[0] == search_term:
                    yield line

            return

        # the dataset is sorted; perform a binary search

        file, zip_info = await open_gtfs_record(resource.path, target_txt)

        with file:
            headers = read_gtfs_line(file.readline())
            tuple_t = tuple_type.make_named_tuple("GTFSRow", headers)

            for line in gtfs_binary_search(file, file.tell(), zip_info.file_size -
                                           1, search_term, tuple_t):
                yield line

    @abstractmethod
    async def async_add_gtfs_data(self, resource: GtfsScheduleResource) -> None:
        """Add GTFS Data."""
        raise NotImplementedError

    @abstractmethod
    def __getitem__(self, key) -> Any:
        """Get Dataset Item."""
        raise NotImplementedError


async def async_factory(
    gtfs_ds_or_class: type[GtfsStaticDataset] | GtfsStaticDataset,
    *gtfs_resource: GtfsScheduleResource,
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
