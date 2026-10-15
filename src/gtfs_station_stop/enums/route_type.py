from enum import IntEnum


class HVTCategory(IntEnum):
    RAILWAY_SERVICE = 100
    COACH_SERVICE = 200
    URBAN_RAILWAY_SERVICE = 400
    BUS_SERVICE = 700
    TROLLEYBUS_SERVICE = 800
    TRAM_SERVICE = 900
    WATER_TRANSPORT_SERVICE = 1000
    AIR_SERVICE = 1100
    FERRY_SERVICE = 1200
    AERIAL_LIFT_SERVICE = 1300
    FUNICULAR_SERVICE = 1400
    TAXI_SERVICE = 1500
    MISCELLANEOUS_SERVICE = 1700


class RouteType(IntEnum):
    """
    Route types from GTFS
    see https://gtfs.org/documentation/schedule/reference/#routestxt
    and https://developers.google.com/transit/gtfs/reference/extended-route-types
    """

    UNKNOWN = -1

    TRAM = 0
    SUBWAY = 1
    RAIL = 2
    BUS = 3
    FERRY = 4
    CABLE_TRAM = 5
    AERIAL_LIFT = 6
    FUNICULAR = 7
    TROLLEYBUS = 11

    # Extended GTFS (HVT)

    RAILWAY_SERVICE = 100
    HIGH_SPEED_RAIL_SERVICE = 101
    LONG_DISTANCE_TRAINS = 102
    INTER_REGIONAL_RAIL_SERVICE = 103
    CAR_TRANSPORT_RAIL_SERVICE = 104
    SLEEPER_RAIL_SERVICE = 105
    REGIONAL_RAIL_SERVICE = 106
    TOURIST_RAILWAY_SERVICE = 107
    RAIL_SHUTTLE__WITHIN_COMPLEX_ = 108
    SUBURBAN_RAILWAY = 109
    REPLACEMENT_RAIL_SERVICE = 110
    SPECIAL_RAIL_SERVICE = 111
    LORRY_TRANSPORT_RAIL_SERVICE = 112
    ALL_RAIL_SERVICES = 113
    CROSS_COUNTRY_RAIL_SERVICE = 114
    VEHICLE_TRANSPORT_RAIL_SERVICE = 115
    RACK_AND_PINION_RAILWAY = 116
    ADDITIONAL_RAIL_SERVICE = 117

    COACH_SERVICE = 200
    INTERNATIONAL_COACH_SERVICE = 201
    NATIONAL_COACH_SERVICE = 202
    SHUTTLE_COACH_SERVICE = 203
    REGIONAL_COACH_SERVICE = 204
    SPECIAL_COACH_SERVICE = 205
    SIGHTSEEING_COACH_SERVICE = 206
    TOURIST_COACH_SERVICE = 207
    COMMUTER_COACH_SERVICE = 208
    ALL_COACH_SERVICES = 209

    URBAN_RAILWAY_SERVICE_CATEGORY = 400
    METRO_SERVICE = 401
    UNDERGROUND_SERVICE = 402
    URBAN_RAILWAY_SERVICE = 403
    ALL_URBAN_RAILWAY_SERVICES = 404
    MONORAIL = 405

    BUS_SERVICE = 700
    REGIONAL_BUS_SERVICE = 701
    EXPRESS_BUS_SERVICE = 702
    STOPPING_BUS_SERVICE = 703
    LOCAL_BUS_SERVICE = 704
    NIGHT_BUS_SERVICE = 705
    POST_BUS_SERVICE = 706
    SPECIAL_NEEDS_BUS = 707
    MOBILITY_BUS_SERVICE = 708
    MOBILITY_BUS_FOR_REGISTERED_DISABLED = 709
    SIGHTSEEING_BUS = 710
    SHUTTLE_BUS = 711
    SCHOOL_BUS = 712
    SCHOOL_AND_PUBLIC_SERVICE_BUS = 713
    RAIL_REPLACEMENT_BUS_SERVICE = 714
    DEMAND_AND_RESPONSE_BUS_SERVICE = 715
    ALL_BUS_SERVICES = 716

    TROLLEYBUS_SERVICE = 800

    TRAM_SERVICE = 900
    CITY_TRAM_SERVICE = 901
    LOCAL_TRAM_SERVICE = 902
    REGIONAL_TRAM_SERVICE = 903
    SIGHTSEEING_TRAM_SERVICE = 904
    SHUTTLE_TRAM_SERVICE = 905
    ALL_TRAM_SERVICES = 906

    WATER_TRANSPORT_SERVICE = 1000

    AIR_SERVICE = 1100

    FERRY_SERVICE = 1200

    AERIAL_LIFT_SERVICE = 1300
    TELECABIN_SERVICE = 1301
    CABLE_CAR_SERVICE = 1302
    ELEVATOR_SERVICE = 1303
    CHAIR_LIFT_SERVICE = 1304
    DRAG_LIFT_SERVICE = 1305
    SMALL_TELECABIN_SERVICE = 1306
    ALL_TELECABIN_SERVICES = 1307

    FUNICULAR_SERVICE = 1400

    TAXI_SERVICE = 1500
    COMMUNAL_TAXI_SERVICE = 1501
    WATER_TAXI_SERVICE = 1502
    RAIL_TAXI_SERVICE = 1503
    BIKE_TAXI_SERVICE = 1504
    LICENSED_TAXI_SERVICE = 1505
    PRIVATE_HIRE_SERVICE_VEHICLE = 1506
    ALL_TAXI_SERVICES = 1507

    MISCELLANEOUS_SERVICE = 1700
    HORSE_DRAWN_CARRIAGE = 1702

    @classmethod
    def _missing_(cls, value):
        try:
            if isinstance(value, str):
                value = int(value)
                for member in cls:
                    if member.value == value:
                        return member
        except ValueError:
            pass

        return cls.UNKNOWN

    def pretty_name(self):
        """Provides a nice name for various enums."""
        return PRETTY_NAMES.get(self) or self.name

    def is_extended(self) -> bool:
        return self >= 100

    def get_category(self) -> HVTCategory:
        assert self.is_extended()

        return HVTCategory((self // 100) * 100)

    def to_basic(self) -> RouteType:
        if not self.is_extended():
            return self

        category = self.get_category()

        match category:
            case HVTCategory.RAILWAY_SERVICE \
                    | HVTCategory.URBAN_RAILWAY_SERVICE:
                return RouteType.RAIL
            case HVTCategory.COACH_SERVICE \
                    | HVTCategory.BUS_SERVICE:
                return RouteType.BUS
            case HVTCategory.TROLLEYBUS_SERVICE:
                return RouteType.TROLLEYBUS
            case HVTCategory.TRAM_SERVICE:
                return RouteType.TRAM
            case HVTCategory.FERRY_SERVICE:
                return RouteType.FERRY
            case HVTCategory.AERIAL_LIFT_SERVICE:
                return RouteType.AERIAL_LIFT
            case HVTCategory.FUNICULAR_SERVICE:
                return RouteType.FUNICULAR
            case _:
                return RouteType.UNKNOWN


PRETTY_NAMES = {
    RouteType.UNKNOWN: "Unknown",
    RouteType.TRAM: "Tram",
    RouteType.SUBWAY: "Subway",
    RouteType.RAIL: "Rail",
    RouteType.BUS: "Bus",
    RouteType.FERRY: "Ferry",
    RouteType.CABLE_TRAM: "Cable Tram",
    RouteType.AERIAL_LIFT: "Aerial Lift",
    RouteType.FUNICULAR: "Funicular",
    RouteType.TROLLEYBUS: "Trolleybus",

    RouteType.RAILWAY_SERVICE: "Railway Service",
    RouteType.HIGH_SPEED_RAIL_SERVICE: "High Speed Rail Service",
    RouteType.LONG_DISTANCE_TRAINS: "Long Distance Trains",
    RouteType.INTER_REGIONAL_RAIL_SERVICE: "Inter Regional Rail Service",
    RouteType.CAR_TRANSPORT_RAIL_SERVICE: "Car Transport Rail Service",
    RouteType.SLEEPER_RAIL_SERVICE: "Sleeper Rail Service",
    RouteType.REGIONAL_RAIL_SERVICE: "Regional Rail Service",
    RouteType.TOURIST_RAILWAY_SERVICE: "Tourist Railway Service",
    RouteType.RAIL_SHUTTLE__WITHIN_COMPLEX_: "Rail Shuttle (Within Complex)",
    RouteType.SUBURBAN_RAILWAY: "Suburban Railway",
    RouteType.REPLACEMENT_RAIL_SERVICE: "Replacement Rail Service",
    RouteType.SPECIAL_RAIL_SERVICE: "Special Rail Service",
    RouteType.LORRY_TRANSPORT_RAIL_SERVICE: "Lorry Transport Rail Service",
    RouteType.ALL_RAIL_SERVICES: "All Rail Services",
    RouteType.CROSS_COUNTRY_RAIL_SERVICE: "Cross-Country Rail Service",
    RouteType.VEHICLE_TRANSPORT_RAIL_SERVICE: "Vehicle Transport Rail Service",
    RouteType.RACK_AND_PINION_RAILWAY: "Rack and Pinion Railway",
    RouteType.ADDITIONAL_RAIL_SERVICE: "Additional Rail Service",
    RouteType.COACH_SERVICE: "Coach Service",
    RouteType.INTERNATIONAL_COACH_SERVICE: "International Coach Service",
    RouteType.NATIONAL_COACH_SERVICE: "National Coach Service",
    RouteType.SHUTTLE_COACH_SERVICE: "Shuttle Coach Service",
    RouteType.REGIONAL_COACH_SERVICE: "Regional Coach Service",
    RouteType.SPECIAL_COACH_SERVICE: "Special Coach Service",
    RouteType.SIGHTSEEING_COACH_SERVICE: "Sightseeing Coach Service",
    RouteType.TOURIST_COACH_SERVICE: "Tourist Coach Service",
    RouteType.COMMUTER_COACH_SERVICE: "Commuter Coach Service",
    RouteType.ALL_COACH_SERVICES: "All Coach Services",
    RouteType.URBAN_RAILWAY_SERVICE_CATEGORY: "Urban Railway Service",
    RouteType.METRO_SERVICE: "Metro Service",
    RouteType.UNDERGROUND_SERVICE: "Underground Service",
    RouteType.URBAN_RAILWAY_SERVICE: "Urban Railway Service",
    RouteType.ALL_URBAN_RAILWAY_SERVICES: "All Urban Railway Services",
    RouteType.MONORAIL: "Monorail",
    RouteType.BUS_SERVICE: "Bus Service",
    RouteType.REGIONAL_BUS_SERVICE: "Regional Bus Service",
    RouteType.EXPRESS_BUS_SERVICE: "Express Bus Service",
    RouteType.STOPPING_BUS_SERVICE: "Stopping Bus Service",
    RouteType.LOCAL_BUS_SERVICE: "Local Bus Service",
    RouteType.NIGHT_BUS_SERVICE: "Night Bus Service",
    RouteType.POST_BUS_SERVICE: "Post Bus Service",
    RouteType.SPECIAL_NEEDS_BUS: "Special Needs Bus",
    RouteType.MOBILITY_BUS_SERVICE: "Mobility Bus Service",
    RouteType.MOBILITY_BUS_FOR_REGISTERED_DISABLED: "Mobility Bus for Registered Disabled",
    RouteType.SIGHTSEEING_BUS: "Sightseeing Bus",
    RouteType.SHUTTLE_BUS: "Shuttle Bus",
    RouteType.SCHOOL_BUS: "School Bus",
    RouteType.SCHOOL_AND_PUBLIC_SERVICE_BUS: "School and Public Service Bus",
    RouteType.RAIL_REPLACEMENT_BUS_SERVICE: "Rail Replacement Bus Service",
    RouteType.DEMAND_AND_RESPONSE_BUS_SERVICE: "Demand and Response Bus Service",
    RouteType.ALL_BUS_SERVICES: "All Bus Services",
    RouteType.TROLLEYBUS_SERVICE: "Trolleybus Service",
    RouteType.TRAM_SERVICE: "Tram Service",
    RouteType.CITY_TRAM_SERVICE: "City Tram Service",
    RouteType.LOCAL_TRAM_SERVICE: "Local Tram Service",
    RouteType.REGIONAL_TRAM_SERVICE: "Regional Tram Service",
    RouteType.SIGHTSEEING_TRAM_SERVICE: "Sightseeing Tram Service",
    RouteType.SHUTTLE_TRAM_SERVICE: "Shuttle Tram Service",
    RouteType.ALL_TRAM_SERVICES: "All Tram Services",
    RouteType.WATER_TRANSPORT_SERVICE: "Water Transport Service",
    RouteType.AIR_SERVICE: "Air Service",
    RouteType.FERRY_SERVICE: "Ferry Service",
    RouteType.AERIAL_LIFT_SERVICE: "Aerial Lift Service",
    RouteType.TELECABIN_SERVICE: "Telecabin Service",
    RouteType.CABLE_CAR_SERVICE: "Cable Car Service",
    RouteType.ELEVATOR_SERVICE: "Elevator Service",
    RouteType.CHAIR_LIFT_SERVICE: "Chair Lift Service",
    RouteType.DRAG_LIFT_SERVICE: "Drag Lift Service",
    RouteType.SMALL_TELECABIN_SERVICE: "Small Telecabin Service",
    RouteType.ALL_TELECABIN_SERVICES: "All Telecabin Services",
    RouteType.FUNICULAR_SERVICE: "Funicular Service",
    RouteType.TAXI_SERVICE: "Taxi Service",
    RouteType.COMMUNAL_TAXI_SERVICE: "Communal Taxi Service",
    RouteType.WATER_TAXI_SERVICE: "Water Taxi Service",
    RouteType.RAIL_TAXI_SERVICE: "Rail Taxi Service",
    RouteType.BIKE_TAXI_SERVICE: "Bike Taxi Service",
    RouteType.LICENSED_TAXI_SERVICE: "Licensed Taxi Service",
    RouteType.PRIVATE_HIRE_SERVICE_VEHICLE: "Private Hire Service Vehicle",
    RouteType.ALL_TAXI_SERVICES: "All Taxi Services",
    RouteType.MISCELLANEOUS_SERVICE: "Miscellaneous Service",
    RouteType.HORSE_DRAWN_CARRIAGE: "Horse-drawn Carriage",
}
