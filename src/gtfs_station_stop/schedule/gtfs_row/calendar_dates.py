from typing import Iterable, override
from datetime import date
from ...enums import ServiceExceptionType
from .base import GtfsRowTuple


class CalendarDates(GtfsRowTuple):
    _service_id_idx: int
    _date_idx: int
    _exception_type_idx: int

    @staticmethod
    @override
    def make_named_tuple(name: str, headers: Iterable[str]) -> type[CalendarDates]:
        header_dict = {}

        for index, header in enumerate(headers):
            match header:
                case "service_id":
                    header_dict["_service_id_idx"] = index
                case "date":
                    header_dict["_date_idx"] = index
                case "exception_type":
                    header_dict["_exception_type_idx"] = index

        return type(name, (CalendarDates,), header_dict)

    @property
    def service_id(self) -> str:
        return self[self._service_id_idx]

    @property
    def date(self) -> date:
        return date.strptime(self[self._date_idx], "%Y%m%d")

    @property
    def exception_type(self) -> ServiceExceptionType:
        return ServiceExceptionType(int(self[self._exception_type_idx]))
