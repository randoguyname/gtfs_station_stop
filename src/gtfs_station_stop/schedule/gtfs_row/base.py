from typing import Iterable
from collections import namedtuple


class GtfsRowTuple(tuple[str, ...]):
    @staticmethod
    def make_named_tuple(name: str, headers: Iterable[str]) -> type:
        return namedtuple(name, headers)
