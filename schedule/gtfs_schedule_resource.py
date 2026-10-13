from pathlib import Path
from dataclasses import dataclass, field


@dataclass(order=True)
class GtfsScheduleResource:
    path: Path
    sorted_asc_by_first_column: bool | None = field(
        default=None, compare=False)

    def __hash__(self) -> int:
        return hash(self.path)
