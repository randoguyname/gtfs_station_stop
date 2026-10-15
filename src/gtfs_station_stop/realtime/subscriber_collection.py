from weakref import WeakSet
from dataclasses import dataclass, field
from typing import Generator

from .subscriber_identifier import SubscriberIdentifier
from .subscriber import Subscriber


@dataclass
class SubscriberCollection:
    subscribers: list[tuple[SubscriberIdentifier, WeakSet[Subscriber]]] = field(
        default_factory=list, init=False)

    def __contains__(self, key: SubscriberIdentifier) -> bool:
        for identifier, _ in self.subscribers:
            if identifier == key:
                return True

        return False

    def index(self, key: SubscriberIdentifier) -> int:
        for idx, (identifier, _) in enumerate(self.subscribers):
            if identifier == key:
                return idx

        raise ValueError(f"Key {key} not in {self.__class__}")

    def subscribe(self, identifier: SubscriberIdentifier, subscriber: Subscriber):
        if identifier in self:
            idx = self.index(identifier)
            self.subscribers[idx][1].add(subscriber)
            return

        self.subscribers.append((identifier, WeakSet({subscriber})))

    def unsubscribe(self, identifier: SubscriberIdentifier, subscriber: Subscriber):
        if identifier not in self:
            raise ValueError(f"{identifier} not in {self.__class__}")

        idx = self.index(identifier)

        self.subscribers[idx][1].remove(subscriber)

    def get_notified_subscribers(self, *identifiers: SubscriberIdentifier) -> Generator[Subscriber]:
        for id, subscribers in self.subscribers:
            for identifier in identifiers:
                if id.listens_to(identifier):
                    yield from subscribers
                    break

    def listens_to(self, *identifiers: SubscriberIdentifier) -> bool:
        for _ in self.get_notified_subscribers(*identifiers):
            return True

        return False

    def values(self) -> Generator[Subscriber]:
        for _, subscribers in self.subscribers:
            yield from subscribers
