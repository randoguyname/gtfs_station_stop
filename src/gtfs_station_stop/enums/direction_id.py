from typing import Self
from enum import IntEnum


class DirectionID(IntEnum):
    ONE_DIRECTION = 0
    OPPOSITE_DIRECTION = 1

    @classmethod
    def parse(cls, direction_id: str | int | None) -> Self | None:
        if direction_id is None:
            return None

        try:
            return cls(direction_id)
        except ValueError:
            try:
                return cls(int(direction_id))
            except ValueError:
                return None
