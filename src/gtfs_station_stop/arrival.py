"""Dataclass for Arrivals"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Self
from functools import total_ordering

from .realtime.vehicle import Vehicle
from .schedule.static_dataset.stop_times import StopTimesDataset
from .helpers import as_datetime, as_timedelta, realtime_get_current_trip_position

from google.transit.gtfs_realtime_pb2 import TripUpdate


@total_ordering
@dataclass(kw_only=True)
class Arrival:
    """Class for keeping arrival data."""

    trip_id: str
    route_id: str
    realtime_trip_id: str | None = None
    time: datetime | None = None
    delay: timedelta | None = None
    departure_time: datetime | None = None
    departure_delay: timedelta | None = None
    stop_sequence: int | None = None
    destination: str | None = None
    vehicle: Vehicle | None = None
    current_station: str | None = None
    time_until: timedelta | None = None

    @classmethod
    def from_realtime_data(
        cls,
        trip_update: TripUpdate,
        stop_time_update: TripUpdate.StopTimeUpdate,
        vehicle: Vehicle | None = None,
    ) -> Self:

        current_station = realtime_get_current_trip_position(trip_update)

        destination: str | None = None

        if len(trip_update.stop_time_update) > 0:
            destination = trip_update.stop_time_update[-1].stop_id

        return cls(
            route_id=trip_update.trip.route_id,
            trip_id=trip_update.trip.trip_id,
            time=as_datetime(
                getattr(stop_time_update.arrival, "time", None), False),
            delay=as_timedelta(
                getattr(stop_time_update.arrival, "delay", None), False),
            departure_time=as_datetime(
                getattr(stop_time_update.departure, "time", None), False),
            departure_delay=as_timedelta(
                getattr(stop_time_update.departure, "delay", None), False),
            stop_sequence=getattr(
                stop_time_update, "stop_sequence", None),
            current_station=current_station,
            destination=destination,
            vehicle=vehicle,
        )

    def make_relative_arrival(self, current_time: datetime | None = None, stop_times_dataset: StopTimesDataset | None = None) -> Self:
        current_time_ = (current_time or datetime.now())

        if self.time is not None:
            self.time_until = self.time - current_time_

            return self

        if self.departure_time is not None:
            self.time_until = self.departure_time - current_time_

            return self

        assert stop_times_dataset is not None
        assert self.trip_id is not None
        assert self.stop_sequence is not None

        stop_time = stop_times_dataset.get(self.trip_id, self.stop_sequence)

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

    def update_from(self, other: Arrival) -> None:
        """Updates the data of this Arrival treating the other Arrival as a more authoritative source"""

        if other.time is not None:
            self.time = other.time
            self.delay = other.delay
        elif other.delay is not None:
            self.delay = other.delay
        elif other.departure_time is not None:
            self.departure_time = other.departure_time
            self.departure_delay = other.departure_delay
        elif other.departure_delay is not None:
            self.departure_delay = other.departure_delay

        if other.trip_id != self.trip_id:
            self.realtime_trip_id = other.trip_id

        self.route_id = other.route_id

        if other.stop_sequence is not None:
            self.stop_sequence = other.stop_sequence

        if other.destination is not None:
            self.destination = other.destination

        if other.vehicle is not None:
            self.vehicle = other.vehicle

        if other.current_station is not None:
            self.current_station = other.current_station

        if other.time_until is not None:
            self.time_until = other.time_until

    def __lt__(self, value: object) -> bool:
        if not isinstance(value, Arrival):
            raise TypeError(
                f"Cannot compare {self.__class__} with {value.__class__}")

        if self.time is not None and value.time is not None and self.time != value.time:
            return self.time < value.time

        if self.departure_time is not None and value.departure_time is not None and self.departure_time != value.departure_time:
            return self.departure_time < value.departure_time

        if self.trip_id != value.trip_id:
            return self.trip_id < value.trip_id

        return self.route_id < value.route_id

    def __str__(self) -> str:
        return f"Arrival(time={self.time.strftime("%H:%M:%S") if self.time else None}, \
delay={str(self.delay)}, \
departure_time={self.departure_time.strftime("%H:%M:%S") if self.departure_time else None}, \
delay={str(self.departure_delay)}, \
trip_id={self.trip_id}, \
route_id={self.route_id}, \
realtime_trip_id={self.realtime_trip_id})"
