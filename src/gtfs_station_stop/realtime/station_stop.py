"""Station Stop."""

from datetime import datetime
import time
from typing import NamedTuple, override

from .subscriber_identifier import StationStopIdentifier

from .subscriber import (BaseSubscriberUpdate, SubscriberUpdateContext,
                         ArrivalSubscriberUpdate, StopTimeUpdateSubscriberUpdateContext)
from ..arrival import Arrival
from .feed_subject import FeedSubject
from ..schedule.static_dataset.stop_times import StopTimesDataset
from .subscriber import AlertSubscriber, BaseArrivalSubscriber
from ..trip_identifier import TripIdentifier
from ..enums import StopTimeScheduleRelationship, TripDescriptorScheduleRelationship


class ArrivalIdentifier(NamedTuple):
    trip_id: str | None
    route_id: str | None


class StationStop(AlertSubscriber, BaseArrivalSubscriber):
    """Station Stop."""

    added_arrivals: dict[TripIdentifier, Arrival]
    updated_arrivals: list[Arrival]
    canceled_arrivals: list[ArrivalIdentifier]

    def __init__(self, id: StationStopIdentifier, updater: FeedSubject) -> None:
        super().__init__()
        self.id = id
        self.updater = updater
        self.updater.subscribe(self.id, self)
        self.added_arrivals = {}
        self.updated_arrivals = []
        self.canceled_arrivals = []
        self.alerts = []

    def add_arrival(self, arrival: Arrival, trip_identifier: TripIdentifier) -> None:
        self.added_arrivals[trip_identifier] = arrival

    def update_arrival(self, arrival: Arrival) -> None:
        self.updated_arrivals.append(arrival)

    def cancel_arrival(self, trip_id: str | None = None, route_id: str | None = None) -> None:
        self.canceled_arrivals.append(ArrivalIdentifier(trip_id, route_id))

    @override
    def apply_update(self, update: BaseSubscriberUpdate, context: SubscriberUpdateContext) -> None:
        super().apply_update(update, context)

        if not isinstance(update, ArrivalSubscriberUpdate):
            return

        # handle arrivals
        assert isinstance(context, StopTimeUpdateSubscriberUpdateContext)

        assert isinstance(context.id, StationStopIdentifier)

        if context.id.stop_id != self.id.stop_id:
            return  # TODO: do something special here

        if context.trip_schedule_relationship == TripDescriptorScheduleRelationship.SCHEDULED \
                and context.stop_time_schedule_relationship == StopTimeScheduleRelationship.SCHEDULED:

            self.update_arrival(update.arrival)
            return

        if context.trip_schedule_relationship == TripDescriptorScheduleRelationship.CANCELED \
                or context.stop_time_schedule_relationship == StopTimeScheduleRelationship.SKIPPED:
            self.cancel_arrival(update.arrival.trip_id,
                                update.arrival.route_id)
            return

        self.add_arrival(update.arrival, context.trip_identifier)

    @override
    def begin_update(self, timestamp: float | None = None) -> None:
        if timestamp is None:
            timestamp = time.time()
        self.alerts.clear()

        self.canceled_arrivals.clear()
        self.added_arrivals.clear()
        self.updated_arrivals.clear()

        self._last_updated = timestamp

    @property
    def arrivals(self) -> list[Arrival]:
        return [*self.updated_arrivals, *self.added_arrivals.values()]

    def get_time_to_arrivals(
        self,
        the_time: datetime | None = None,
        *,
        stop_times_dataset: StopTimesDataset | None = None,
    ) -> list[Arrival]:
        """Get Time To Arrivals."""

        return [a.make_relative_arrival(the_time, stop_times_dataset) for a in self.arrivals]
