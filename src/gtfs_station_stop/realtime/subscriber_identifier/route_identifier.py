from .base import SubscriberIdentifier


from dataclasses import dataclass
from typing import override


@dataclass(frozen=True)
class RouteIdentifier(SubscriberIdentifier):
    route_id: str

    @override
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, SubscriberIdentifier):
            raise TypeError(
                f"Cannot compare {__class__} with {value.__class__}")

        if not isinstance(value, RouteIdentifier):
            return False

        return self.route_id == value.route_id

    @override
    def __lt__(self, value: object) -> bool:
        if not isinstance(value, SubscriberIdentifier):
            raise TypeError(
                f"Cannot compare {__class__} with {value.__class__}")

        if not isinstance(value, RouteIdentifier):
            return hash(self) < hash(value)

        return self.route_id < value.route_id

    @override
    def __hash__(self) -> int:
        return hash((self.route_id))

    @override
    def listens_to(self, other: SubscriberIdentifier) -> bool:
        if not isinstance(other, RouteIdentifier):
            return False

        return self.route_id == other.route_id
