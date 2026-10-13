from dataclasses import dataclass
from typing import Self
from datetime import datetime

from google.transit.gtfs_realtime_pb2 import TripUpdate

from .schedule.gtfs_arrival_departure_time import GtfsArrivalDepartureTime
from .enums import TripDescriptorScheduleRelationship, DirectionID


@dataclass(frozen=True, kw_only=True)
class TripIdentifier:  # TODO: technically, stop id is not required in Schedule; fix this
    trip_id: str | None = None
    start_time: GtfsArrivalDepartureTime | None = None
    stop_id_1: str | None = None
    stop_id_2: str | None = None
    route_id: str | None = None
    direction_id: DirectionID | None = None

    @classmethod
    def from_trip_update(cls, trip_update: TripUpdate) -> Self:
        stop_times = trip_update.stop_time_update

        schedule_relationship = TripDescriptorScheduleRelationship(
            trip_update.trip.schedule_relationship)

        if schedule_relationship in {
            TripDescriptorScheduleRelationship.NEW,
            TripDescriptorScheduleRelationship.REPLACEMENT
        }:
            if trip_update.trip.HasField("start_time"):
                start_time = GtfsArrivalDepartureTime.strptime(
                    trip_update.trip.start_time)
            else:
                if stop_times[0].arrival.HasField("time"):
                    start_time = GtfsArrivalDepartureTime.from_time(
                        datetime.fromtimestamp(stop_times[0].arrival.time).time())
                elif stop_times[0].arrival.HasField("scheduled_time"):
                    start_time = GtfsArrivalDepartureTime.from_time(
                        datetime.fromtimestamp(stop_times[0].arrival.scheduled_time + stop_times[0].arrival.delay).time())
                else:
                    start_time = None

            # stop id is required
            return cls(
                start_time=start_time,
                stop_id_1=stop_times[0].stop_id,
                stop_id_2=stop_times[1].stop_id,
            )

        if schedule_relationship == TripDescriptorScheduleRelationship.UNSCHEDULED:
            # trip id and start time *will* be defined

            return cls(
                trip_id=trip_update.trip.trip_id,
                start_time=GtfsArrivalDepartureTime.strptime(
                    trip_update.trip.start_time),
            )

        if trip_update.trip.HasField("start_time"):
            start_time = GtfsArrivalDepartureTime.strptime(
                trip_update.trip.start_time)
        elif stop_times[0].HasField("arrival"):
            if stop_times[0].arrival.HasField("time"):
                start_time = GtfsArrivalDepartureTime.from_time(
                    datetime.fromtimestamp(stop_times[0].arrival.time).time())
            else:
                start_time = None
        else:  # has field "departure"
            if stop_times[0].departure.HasField("time"):
                start_time = GtfsArrivalDepartureTime.from_time(
                    datetime.fromtimestamp(stop_times[0].departure.time).time())
            else:
                start_time = None

        return cls(
            start_time=start_time,
            trip_id=trip_update.trip.trip_id if trip_update.trip.HasField(
                "trip_id") and schedule_relationship != TripDescriptorScheduleRelationship.ADDED else None,
            route_id=trip_update.trip.route_id if trip_update.trip.HasField(
                "route_id") else None,
            direction_id=DirectionID(trip_update.trip.direction_id) if trip_update.trip.HasField(
                "direction_id") else None,
            stop_id_1=stop_times[0].stop_id if stop_times[0].HasField(
                "stop_id") else None,
            stop_id_2=stop_times[1].stop_id if len(
                stop_times) >= 2 and stop_times[1].HasField("stop_id") else None,
        )

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, TripIdentifier):
            return False

        if self.trip_id is not None and value.trip_id is not None:
            if self.trip_id == value.trip_id:
                # probably same, but check start_time
                if self.start_time is None or value.start_time is None:
                    return True

                return self.start_time == value.start_time

            return False

        # now, one of the trip ids is None

        if self.stop_id_1 is not None and value.stop_id_1 is not None and \
                self.stop_id_1 != value.stop_id_1:
            return False

        if self.stop_id_2 is not None and value.stop_id_2 is not None and \
                self.stop_id_2 != value.stop_id_2:
            return False

        if self.route_id is not None and value.route_id is not None and \
                self.route_id != value.route_id:
            return False

        if self.direction_id is not None and value.direction_id is not None and \
                self.direction_id != value.direction_id:
            return False

        if self.start_time is not None and value.start_time is not None and \
                self.start_time != value.start_time:
            return False

        return True
