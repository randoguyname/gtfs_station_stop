from typing import Iterable, override

from ...enums import RouteType, ContinuousPickupType, ContinuousDropOffType, CEMVSupport
from .base import GtfsRowTuple


class Routes(GtfsRowTuple):
    _route_id_idx: int
    _agency_id_idx: int | None = None
    _route_short_name_idx: int | None = None
    _route_long_name_idx: int | None = None
    _route_desc_idx: int | None = None
    _route_type_idx: int
    _route_url_idx: int | None = None
    _route_color_idx: int | None = None
    _route_text_color_idx: int | None = None
    _route_sort_order_idx: int | None = None
    _continuous_pickup_idx: int | None = None
    _continuous_drop_off_idx: int | None = None
    _network_id_idx: int | None = None
    _cemv_support_idx: int | None = None

    @staticmethod
    @override
    def make_named_tuple(name: str, headers: Iterable[str]) -> type[Routes]:
        header_dict = {}

        for index, header in enumerate(headers):
            match header:
                case "route_id":
                    header_dict["_route_id_idx"] = index
                case "agency_id":
                    header_dict["_agency_id_idx"] = index
                case "route_short_name":
                    header_dict["_route_short_name_idx"] = index
                case "route_long_name":
                    header_dict["_route_long_name_idx"] = index
                case "route_desc":
                    header_dict["_route_desc_idx"] = index
                case "route_type":
                    header_dict["_route_type_idx"] = index
                case "route_url":
                    header_dict["_route_url_idx"] = index
                case "route_color":
                    header_dict["_route_color_idx"] = index
                case "route_text_color":
                    header_dict["_route_text_color_idx"] = index
                case "route_sort_order":
                    header_dict["_route_sort_order_idx"] = index
                case "continuous_pickup":
                    header_dict["_continuous_pickup_idx"] = index
                case "continuous_drop_off":
                    header_dict["_continuous_drop_off_idx"] = index
                case "network_id":
                    header_dict["_network_id_idx"] = index
                case "cemv_support":
                    header_dict["_cemv_support_idx"] = index

        return type(name, (Routes,), header_dict)

    @property
    def route_id(self) -> str:
        return self[self._route_id_idx]

    @property
    def agency_id(self) -> str | None:
        if self._agency_id_idx is None:
            return None

        return self[self._agency_id_idx]

    @property
    def route_short_name(self) -> str | None:
        if self._route_short_name_idx is None:
            return None

        return self[self._route_short_name_idx]

    @property
    def route_long_name(self) -> str | None:
        if self._route_long_name_idx is None:
            return None

        return self[self._route_long_name_idx]

    @property
    def route_desc(self) -> str | None:
        if self._route_desc_idx is None:
            return None

        return self[self._route_desc_idx]

    @property
    def route_type(self) -> RouteType:
        return RouteType(self[self._route_type_idx])

    @property
    def route_url(self) -> str | None:
        if self._route_url_idx is None:
            return None

        return self[self._route_url_idx]

    @property
    def route_color(self) -> str | None:
        if self._route_color_idx is None:
            return None

        return self[self._route_color_idx]

    @property
    def route_text_color(self) -> str | None:
        if self._route_text_color_idx is None:
            return None

        return self[self._route_text_color_idx]

    @property
    def route_sort_order(self) -> str | None:
        if self._route_sort_order_idx is None:
            return None

        return self[self._route_sort_order_idx]

    @property
    def continuous_pickup(self) -> ContinuousPickupType:
        if self._continuous_pickup_idx is None:
            return ContinuousPickupType(None)

        return ContinuousPickupType(self[self._continuous_pickup_idx])

    @property
    def continuous_drop_off(self) -> ContinuousDropOffType:
        if self._continuous_drop_off_idx is None:
            return ContinuousDropOffType(None)

        return ContinuousDropOffType(self[self._continuous_drop_off_idx])

    @property
    def network_id(self) -> str | None:
        if self._network_id_idx is None:
            return None

        return self[self._network_id_idx]

    @property
    def cemv_support(self) -> CEMVSupport:
        if self._cemv_support_idx is None:
            return CEMVSupport(None)

        return CEMVSupport(self[self._cemv_support_idx])
