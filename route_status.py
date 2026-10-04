"""Route Status."""

import time
from typing import TYPE_CHECKING

from .feed_subject import FeedSubject
from .updatable import Updatable

if TYPE_CHECKING:
    from .alert import Alert


class RouteStatus(Updatable):
    """Route Status."""

    def __init__(self, route_id: str, updater: FeedSubject) -> None:
        super().__init__()
        self.id = route_id
        self.updater = updater
        self.updater.subscribe(self)
        self.alerts: list[Alert] = []

    def begin_update(self, timestamp: float | None = None) -> None:
        if timestamp is None:
            timestamp = time.time()
        self.alerts.clear()
        self._last_updated = timestamp if timestamp is not None else time.time()
