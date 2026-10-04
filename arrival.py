"""Dataclass for Arrivals"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Self

from .vehicle import Vehicle
from .stop_times import StopTimesDataset


@dataclass(kw_only=True, order=True)
class Arrival:
    """Class for keeping arrival data."""

    time: datetime | None = None
    delay: timedelta | None = None
    departure_time: datetime | None = None
    departure_delay: timedelta | None = None
    trip: str
    route: str
    stop_sequence: int | None = None
    destination: str | None = None
    vehicle: Vehicle | None = None
    current_station: str | None = None
    time_until: timedelta | None = None

    def make_relative_arrival(self, current_time: datetime | None = None, stop_times_dataset: StopTimesDataset | None = None) -> Self:
        current_time_ = (current_time or datetime.now())

        if self.time is not None:
            self.time_until = self.time - current_time_

            return self

        if self.departure_time is not None:
            self.time_until = self.departure_time - current_time_

            return self

        assert stop_times_dataset is not None
        assert self.trip is not None
        assert self.stop_sequence is not None

        stop_time = stop_times_dataset.get(self.trip, self.stop_sequence)

        assert stop_time is not None

        current_date = current_time_.date()

        if self.delay is not None:
            assert stop_time.arrival_time is not None

            stop_time_datetime = datetime(
                year=current_date.year,
                month=current_date.month,
                day=current_date.day,
                hour=stop_time.arrival_time.hour,
                minute=stop_time.arrival_time.minute,
                second=stop_time.arrival_time.second,
            )

            self.time_until = current_time_ - (stop_time_datetime + self.delay)

            return self

        if self.departure_delay is not None:
            assert stop_time.departure_time is not None

            stop_time_datetime = datetime(
                year=current_date.year,
                month=current_date.month,
                day=current_date.day,
                hour=stop_time.departure_time.hour,
                minute=stop_time.departure_time.minute,
                second=stop_time.departure_time.second,
            )

            self.time_until = current_time_ - \
                (stop_time_datetime + self.departure_delay)

            return self

        raise ValueError("Arrival has no time data")
