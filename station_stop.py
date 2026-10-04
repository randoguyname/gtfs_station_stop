"""Station Stop."""

from datetime import datetime
import time
from copy import copy
from typing import TYPE_CHECKING

from .arrival import Arrival
from .feed_subject import FeedSubject
from .stop_times import StopTimesDataset
from .updatable import Updatable

if TYPE_CHECKING:
    from .alert import Alert


class StationStop(Updatable):
    """Station Stop."""

    def __init__(self, stop_id: str, updater: FeedSubject) -> None:
        super().__init__()
        self.id = stop_id
        self.updater = updater
        self.updater.subscribe(self)
        self.arrivals: list[Arrival] = []
        self.alerts: list[Alert] = []

    def begin_update(self, timestamp: float | None = None) -> None:
        if timestamp is None:
            timestamp = time.time()
        self.alerts.clear()
        self.arrivals.clear()
        self._last_updated = timestamp

    def get_time_to_arrivals(
        self,
        the_time: datetime | None = None,
        *,
        stop_times_dataset: StopTimesDataset | None = None,
    ) -> list[Arrival]:
        """Get Time To Arrivals."""

        return [a.make_relative_arrival(the_time, stop_times_dataset) for a in self.arrivals]
