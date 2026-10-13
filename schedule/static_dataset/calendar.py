from ...enums.service_exception_type import ServiceExceptionType

from ..service import Service, ServiceDays
from .static_dataset import GtfsStaticDataset
from ..gtfs_row.calendar import Calendar as CalendarRow
from ..gtfs_row.calendar_dates import CalendarDates as CalendarDatesRow


from dataclasses import dataclass, field
from datetime import date, datetime
from typing import override


@dataclass
class Calendar(GtfsStaticDataset):
    """Provides the Calendar data."""

    services: dict[str, Service] = field(default_factory=dict, init=False)

    @override
    async def async_add_gtfs_data(self, resource) -> None:
        """Adds data from a GTFS Dataset to the Calendar."""
        async for line in self._get_gtfs_record_iter(resource.path, "calendar.txt", CalendarRow):
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
                line.start_date,
                line.end_date,
            )
        # Add in special services
        async for line in self._get_gtfs_record_iter(resource.path, "calendar_dates.txt", CalendarDatesRow):
            service_id = line.service_id
            if self.services.get(service_id) is None:
                # Create a blank calendar if it is missing
                self.services[service_id] = Service.no_regular_service(
                    service_id)

            exception_type = line.exception_type

            if exception_type == ServiceExceptionType.ADDED:
                self.services[service_id].added_exceptions.add(line.date)
            elif exception_type == ServiceExceptionType.REMOVED:
                self.services[service_id].removed_exceptions.add(line.date)
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
