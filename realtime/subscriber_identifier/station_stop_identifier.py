from .base import SubscriberIdentifier
from ...enums.location_type import LocationType


from dataclasses import dataclass
from typing import override


@dataclass(frozen=True)
class StationStopIdentifier(SubscriberIdentifier):
    stop_id: str
    location_type: LocationType = LocationType.STOP
    parent_station_id: str | None = None

    def __post_init__(self):
        if self.location_type == LocationType.STATION:
            assert self.parent_station_id is None

        if self.location_type == LocationType.ENTRANCE or \
                self.location_type == LocationType.GENERIC_NODE or \
                self.location_type == LocationType.BOARDING_AREA:
            assert self.parent_station_id is not None

    @override
    def __lt__(self, value: object) -> bool:
        if not isinstance(value, SubscriberIdentifier):
            raise TypeError(
                f"Cannot compare {__class__} with {value.__class__}")

        if isinstance(value, StationStopIdentifier):
            if self.stop_id != value.stop_id:
                return self.stop_id < value.stop_id

            if self.location_type != value.location_type:
                return self.location_type < value.location_type

            if self.parent_station_id == value.parent_station_id:
                return False  # equal, so return False

            # not equal
            if self.parent_station_id is None:
                return True

            if value.parent_station_id is None:
                return False

            return self.parent_station_id < value.parent_station_id

        return hash(self) < hash(value)

    @override
    def __hash__(self) -> int:

        if self.parent_station_id is not None:
            return hash((self.stop_id, self.location_type, self.parent_station_id))

        return hash((self.stop_id, self.location_type))

    @override
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, SubscriberIdentifier):
            raise TypeError(
                f"Cannot compare {__class__} with {value.__class__}")

        if not isinstance(value, StationStopIdentifier):
            return False

        return self.stop_id == value.stop_id \
            and self.location_type == value.location_type \
            and self.parent_station_id == value.parent_station_id

    @override
    def listens_to(self, other: SubscriberIdentifier) -> bool:
        if not isinstance(other, StationStopIdentifier):
            return False

        if self.stop_id == other.stop_id:
            return True

        if self.parent_station_id is not None and self.parent_station_id == other.stop_id:
            return True

        return False
