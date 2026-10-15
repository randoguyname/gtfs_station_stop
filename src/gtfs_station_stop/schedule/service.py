"""Calendar Data."""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import NamedTuple, Self


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
