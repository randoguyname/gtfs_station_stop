"""Subscriber"""

from abc import abstractmethod, ABC
from typing import Self, override
from types import TracebackType
from dataclasses import dataclass

from ..enums import FeedEntityType, TripDescriptorScheduleRelationship, StopTimeScheduleRelationship
from ..arrival import Arrival
from ..alert import Alert
from ..trip_identifier import TripIdentifier
from .subscriber_identifier import SubscriberIdentifier


@dataclass(frozen=True)
class BaseSubscriberUpdate(ABC):
    def add_to(self, context_manager: SubscriberUpdateContextManager) -> None:
        context_manager.add_update(self)


@dataclass(frozen=True)
class ArrivalSubscriberUpdate(BaseSubscriberUpdate):
    arrival: Arrival


@dataclass(frozen=True)
class AlertSubscriberUpdate(BaseSubscriberUpdate):
    alert: Alert


class SubscriberUpdateContextManager:
    subscriber: Subscriber
    context: SubscriberUpdateContext

    updates: list[BaseSubscriberUpdate]

    def __init__(self, subscriber: Subscriber, context: SubscriberUpdateContext) -> None:
        self.subscriber = subscriber
        self.context = context
        self.updates = []

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None) -> None:
        if exc is not None:
            raise exc.with_traceback(tb)

        # apply changes upstream
        for update in self.updates:
            self.subscriber.apply_update(update, self.context)

    def add_update(self, update: BaseSubscriberUpdate):
        self.updates.append(update)


@dataclass(frozen=True)
class SubscriberUpdateContext:
    id: SubscriberIdentifier
    feed_entity_type: FeedEntityType


@dataclass(frozen=True)
class StopTimeUpdateSubscriberUpdateContext(SubscriberUpdateContext):
    trip_schedule_relationship: TripDescriptorScheduleRelationship
    stop_time_schedule_relationship: StopTimeScheduleRelationship
    trip_identifier: TripIdentifier


@dataclass(frozen=True)
class AlertSubscriberUpdateContext(SubscriberUpdateContext):
    ...


class Subscriber(ABC):
    """Subscriber Base class."""

    _last_updated: float | None = None

    @property
    def last_updated(self) -> float | None:
        """Time Last Updated."""
        return self._last_updated

    @abstractmethod
    def begin_update(self, timestamp: float | None = None) -> None:
        """Prepare for update by Feed Subject"""
        raise NotImplementedError

    def get_update_manager(self, context: SubscriberUpdateContext) -> SubscriberUpdateContextManager:
        return SubscriberUpdateContextManager(self, context)

    @abstractmethod
    def apply_update(self, update: BaseSubscriberUpdate, context: SubscriberUpdateContext) -> None:
        raise NotImplementedError


class BaseArrivalSubscriber(Subscriber, ABC):
    @abstractmethod
    def add_arrival(self, arrival: Arrival, trip_identifier: TripIdentifier) -> None:
        """Notifies a subscriber of a new added arrival"""
        raise NotImplementedError

    @abstractmethod
    def update_arrival(self, arrival: Arrival) -> None:
        """Notifies a subscriber of updated arrival details"""
        raise NotImplementedError

    @abstractmethod
    def cancel_arrival(self, trip_id: str | None = None, route_id: str | None = None) -> None:
        """Notifies a subscriber that a particular arrival has been cancelled"""
        raise NotImplementedError


class ArrivalSubscriber(BaseArrivalSubscriber, ABC):
    arrivals: list[Arrival]

    def add_arrival(self, arrival: Arrival, trip_identifier: TripIdentifier) -> None:
        self.arrivals.append(arrival)

    def cancel_arrival(self, trip_id: str | None = None, route_id: str | None = None) -> None:
        assert trip_id is not None or route_id is not None

        self.arrivals = list(filter(lambda arrival: (arrival.trip_id == trip_id if trip_id is not None else True) and (
            arrival.route_id == route_id if route_id is not None else True), self.arrivals))

    def update_arrival(self, arrival: Arrival) -> None:
        self.arrivals.append(arrival)

    @override
    def apply_update(self, update: BaseSubscriberUpdate, context: SubscriberUpdateContext) -> None:
        if not isinstance(update, ArrivalSubscriberUpdate):
            return

        self.arrivals.append(update.arrival)


class BaseAlertSubscriber(Subscriber, ABC):
    @abstractmethod
    def add_alert(self, alert: Alert) -> None:
        """Notifies a subscriber of an added allert"""
        raise NotImplementedError


class AlertSubscriber(BaseAlertSubscriber, ABC):
    alerts: list[Alert]

    def __init__(self) -> None:
        self.alerts = []

    def add_alert(self, alert: Alert) -> None:
        self.alerts.append(alert)

    @override
    def apply_update(self, update: BaseSubscriberUpdate, context: SubscriberUpdateContext) -> None:
        if not isinstance(update, AlertSubscriberUpdate):
            return

        self.alerts.append(update.alert)
