from enum import Enum


class FeedEntityType(Enum):
    TRIP_UPDATES = 0
    VEHICLE_POSITION = 1
    ALERT = 2
    SHAPE = 3
    STOP = 4
    TRIP_MODIFICATIONS = 5
