from datetime import date
from typing import Iterable, override
from .base import GtfsRowTuple


class Calendar(GtfsRowTuple):
    _service_id_idx: int
    _monday_idx: int
    _tuesday_idx: int
    _wednesday_idx: int
    _thursday_idx: int
    _friday_idx: int
    _saturday_idx: int
    _sunday_idx: int
    _start_date_idx: int
    _end_date_idx: int

    @staticmethod
    @override
    def make_named_tuple(name: str, headers: Iterable[str]) -> type[Calendar]:
        header_dict = {}

        for index, header in enumerate(headers):
            match header:
                case "service_id":
                    header_dict["_service_id_idx"] = index
                case "monday":
                    header_dict["_monday_idx"] = index
                case "tuesday":
                    header_dict["_tuesday_idx"] = index
                case "wednesday":
                    header_dict["_wednesday_idx"] = index
                case "thursday":
                    header_dict["_thursday_idx"] = index
                case "friday":
                    header_dict["_friday_idx"] = index
                case "saturday":
                    header_dict["_saturday_idx"] = index
                case "sunday":
                    header_dict["_sunday_idx"] = index
                case "start_date":
                    header_dict["_start_date_idx"] = index
                case "end_date":
                    header_dict["_end_date_idx"] = index

        return type(name, (Calendar,), header_dict)

    @property
    def service_id(self) -> str:
        return self[self._service_id_idx]

    @property
    def monday(self) -> bool:
        return self[self._monday_idx] == "1"

    @property
    def tuesday(self) -> bool:
        return self[self._tuesday_idx] == "1"

    @property
    def wednesday(self) -> bool:
        return self[self._wednesday_idx] == "1"

    @property
    def thursday(self) -> bool:
        return self[self._thursday_idx] == "1"

    @property
    def friday(self) -> bool:
        return self[self._friday_idx] == "1"

    @property
    def saturday(self) -> bool:
        return self[self._saturday_idx] == "1"

    @property
    def sunday(self) -> bool:
        return self[self._sunday_idx] == "1"

    @property
    def start_date(self) -> date:
        return date.strptime(self[self._start_date_idx], "%Y%m%d")

    @property
    def end_date(self) -> date:
        return date.strptime(self[self._end_date_idx], "%Y%m%d")
