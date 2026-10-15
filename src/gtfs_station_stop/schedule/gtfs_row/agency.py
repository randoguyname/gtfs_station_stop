from typing import Iterable, override

from ...enums import CEMVSupport
from .base import GtfsRowTuple


class Agency(GtfsRowTuple):
    _agency_id_idx: int | None = None
    _agency_name_idx: int
    _agency_url_idx: int
    _agency_timezone_idx: int
    _agency_lang_idx: int | None = None
    _agency_phone_idx: int | None = None
    _agency_fare_url_idx: int | None = None
    _agency_email_idx: int | None = None
    _cemv_support_idx: int | None = None

    @staticmethod
    @override
    def make_named_tuple(name: str, headers: Iterable[str]) -> type[Agency]:
        header_dict = {}

        for index, header in enumerate(headers):
            match header:
                case "agency_id":
                    header_dict["_agency_id_idx"] = index
                case "agency_name":
                    header_dict["_agency_name_idx"] = index
                case "agency_url":
                    header_dict["_agency_url_idx"] = index
                case "agency_timezone":
                    header_dict["_agency_timezone_idx"] = index
                case "agency_lang":
                    header_dict["_agency_lang_idx"] = index
                case "agency_fare_url":
                    header_dict["_agency_fare_url_idx"] = index
                case "agency_email":
                    header_dict["_agency_email_idx"] = index
                case "cemv_support":
                    header_dict["_cemv_support_idx"] = index

        return type(name, (Agency,), header_dict)

    @property
    def agency_id(self) -> str | None:
        if self._agency_id_idx is None:
            return None

        return self[self._agency_id_idx]

    @property
    def agency_name(self) -> str:
        return self[self._agency_name_idx]

    @property
    def agency_url(self) -> str:
        return self[self._agency_url_idx]

    @property
    def agency_timezone(self) -> str:
        return self[self._agency_timezone_idx]

    @property
    def agency_lang(self) -> str | None:
        if self._agency_lang_idx is None:
            return None

        return self[self._agency_lang_idx]

    @property
    def agency_phone(self) -> str | None:
        if self._agency_phone_idx is None:
            return None

        return self[self._agency_phone_idx]

    @property
    def agency_fare_url(self) -> str | None:
        if self._agency_fare_url_idx is None:
            return None

        return self[self._agency_fare_url_idx]

    @property
    def agency_email(self) -> str | None:
        if self._agency_email_idx is None:
            return None

        return self[self._agency_email_idx]

    @property
    def cemv_support(self) -> CEMVSupport:
        if self._cemv_support_idx is None:
            return CEMVSupport(None)

        return CEMVSupport(self[self._cemv_support_idx])
