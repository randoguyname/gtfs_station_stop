from ..route_info import RouteInfo
from .static_dataset import GtfsStaticDataset


from dataclasses import dataclass, field
from typing import override
from ..gtfs_row.routes import Routes as RouteRow


@dataclass
class RouteInfoDataset(GtfsStaticDataset):
    """Wrapper for map of Route Info."""

    route_infos: dict[str, RouteInfo] = field(default_factory=dict, init=False)

    @override
    async def async_add_gtfs_data(self, resource):
        async for line in self._get_gtfs_record_iter(resource.path, "routes.txt", RouteRow):
            route_id = line.route_id
            self.route_infos[route_id] = RouteInfo(line)

    @override
    def __getitem__(self, key):
        return self.route_infos[key]

    def get_routes(self):
        """Return all routes."""
        return self.route_infos.keys()

    def get(self, key: str, default: RouteInfo | None = None):
        """Get a RouteInfo or a default."""
        return self.route_infos.get(key, default)
