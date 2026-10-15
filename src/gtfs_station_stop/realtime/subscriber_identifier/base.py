from abc import abstractmethod, ABC
from dataclasses import dataclass


@dataclass(frozen=True)
class SubscriberIdentifier(ABC):
    # only bother implementing __lt__
    @abstractmethod
    def __lt__(self, value: object) -> bool:
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, value: object) -> bool:
        raise NotImplementedError

    # __hash__ used for comparison when types differ
    @abstractmethod
    def __hash__(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def listens_to(self, other: SubscriberIdentifier) -> bool:
        raise NotImplementedError
