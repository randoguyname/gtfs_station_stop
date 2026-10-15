"""Trip Info."""


from ..enums import DirectionID
from .gtfs_row.trips import Trips


class TripInfo:
    """Trip Info."""

    route_id: str
    trip_id: str
    service_id: str
    trip_headsign: str | None
    trip_short_name: str | None
    direction_id: DirectionID | None
    shape_id: str | None

    def __init__(self, trip_data: Trips) -> None:
        self.route_id = trip_data.route_id
        self.trip_id = trip_data.trip_id
        self.service_id = trip_data.service_id
        self.trip_headsign = getattr(trip_data, "trip_headsign", "")
        self.trip_short_name = getattr(trip_data, "trip_short_name", "")
        self.direction_id = DirectionID.parse(
            getattr(trip_data, "direction_id", None))
        self.shape_id = getattr(trip_data, "shape_id", None)

    def __repr__(self):
        return f"{self.trip_id}: {self.route_id} to {self.trip_headsign}"
