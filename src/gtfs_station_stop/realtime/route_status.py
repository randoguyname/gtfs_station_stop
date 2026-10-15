"""Route Status."""

import time
from typing import override

from .subscriber_identifier import RouteIdentifier

from .feed_subject import FeedSubject
from .subscriber import AlertSubscriber


class RouteStatus(AlertSubscriber):
    """Route Status."""

    def __init__(self, route_id: str, updater: FeedSubject) -> None:
        super().__init__()
        self.id = RouteIdentifier(route_id)
        self.updater = updater
        self.updater.subscribe(self.id, self)

    @override
    def begin_update(self, timestamp: float | None = None) -> None:
        if timestamp is None:
            timestamp = time.time()
        self.alerts.clear()
        self._last_updated = timestamp if timestamp is not None else time.time()
