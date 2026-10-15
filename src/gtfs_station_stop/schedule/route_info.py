from ..enums import RouteType
from .gtfs_row.routes import Routes as RouteRow


class RouteInfo:
    """Route Info."""
    color: str | None
    text_color: str | None
    url: str | None
    desc: str | None
    type: RouteType
    long_name: str | None
    short_name: str | None
    agency_id: str | None
    id: str

    def __init__(self, route_data: RouteRow) -> None:
        self.id = route_data.route_id
        self.type = route_data.route_type
        self.agency_id = route_data.agency_id
        self.short_name = route_data.route_short_name
        self.long_name = route_data.route_long_name
        if self.short_name is None and self.long_name is None:
            raise ValueError(
                "Either 'route_short_name' or 'route_long_name' must be provided."
            )

        self.desc = route_data.route_desc
        self.url = route_data.route_url
        self.color = route_data.route_color
        self.text_color = route_data.route_text_color
