"""Calendar Data."""

import os
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import NamedTuple, Self, override

from .static_dataset import GtfsStaticDataset

SERVICE_EXCEPTION_TYPE_ADDED = "1"
SERVICE_EXCEPTION_TYPE_REMOVED = "2"


class ServiceDays(NamedTuple):
    """Class for storing the days available with names."""

    monday: bool
    tuesday: bool
    wednesday: bool
    thursday: bool
    friday: bool
    saturday: bool
    sunday: bool

    @classmethod
    def no_service(cls) -> Self:
        """Create a No-Service Service Days Set"""
        return cls(*[False] * len(ServiceDays._fields))


@dataclass
class Service:
    """Class for keeping calendar service data."""

    service_id: str
    service_days: ServiceDays = field(repr=False)
    start: date = field(repr=False)
    end: date = field(repr=False)
    added_exceptions: set[date] = field(
        default_factory=set, init=False, repr=False)
    removed_exceptions: set[date] = field(
        default_factory=set, init=False, repr=False)

    def is_active_on(self, the_date: date | None = None) -> bool:
        """Check if service is active on a given datetime, defaults to now."""
        if the_date is None:
            the_date = date.today()
        if isinstance(the_date, datetime):
            the_date = the_date.date()
        normally_active = (self.start <= the_date <= self.end) and self.service_days[
            the_date.weekday()
        ]
        return (normally_active and the_date not in self.removed_exceptions) or (
            not normally_active and the_date in self.added_exceptions
        )

    @classmethod
    def no_regular_service(cls, service_id: str) -> Self:
        """Provides a service with no regular service days."""
        return cls(service_id, ServiceDays.no_service(), date.min, date.min)


@dataclass
class Calendar(GtfsStaticDataset):
    """Provides the Calendar data."""

    services: dict[str, Service] = field(default_factory=dict, init=False)

    @override
    async def async_add_gtfs_data(self, zip_filelike) -> None:
        """Adds data from a GTFS Dataset to the Calendar."""
        async for line in self._get_gtfs_record_iter(zip_filelike, "calendar.txt"):
            if line is None:
                continue

            self.services[line.service_id] = Service(
                line.service_id,
                ServiceDays(
                    line.monday == "1",
                    line.tuesday == "1",
                    line.wednesday == "1",
                    line.thursday == "1",
                    line.friday == "1",
                    line.saturday == "1",
                    line.sunday == "1",
                ),
                datetime.strptime(line.start_date, "%Y%m%d").date(),
                datetime.strptime(line.end_date, "%Y%m%d").date(),
            )
        # Add in special services
        async for line in self._get_gtfs_record_iter(zip_filelike, "calendar_dates.txt"):
            if line is None:
                continue

            service_id = line.service_id
            if self.services.get(service_id) is None:
                # Create a blank calendar if it is missing
                self.services[service_id] = Service.no_regular_service(
                    service_id)

            if line.exception_type == SERVICE_EXCEPTION_TYPE_ADDED:
                self.services[service_id].added_exceptions.add(
                    datetime.strptime(line.date, "%Y%m%d").date()
                )
            elif line.exception_type == SERVICE_EXCEPTION_TYPE_REMOVED:
                self.services[service_id].removed_exceptions.add(
                    datetime.strptime(line.date, "%Y%m%d").date()
                )
            else:
                raise RuntimeError("Unsupported GTFS service exception type.")

    @override
    def __getitem__(self, key) -> Service:
        return self.services[key]

    def get_active_services(self, the_date: date | None = None) -> list[Service]:
        """Filtered list of all active services."""
        if the_date is None:
            the_date = date.today()
        return [s for s in self.services.values() if s.is_active_on(the_date)]

    def get_inactive_services(self, the_date: date | None = None) -> list[Service]:
        """Filtered list of all inactive services."""
        if the_date is None:
            the_date = date.today()
        return [s for s in self.services.values() if not s.is_active_on(the_date)]
