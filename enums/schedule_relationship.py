from enum import Enum


class StopTimeScheduleRelationship(Enum):
    """
    Schedule Relationship.
    see https://gtfs.org/documentation/realtime/reference/#enum-schedulerelationship
    """

    SCHEDULED = 0
    SKIPPED = 1
    NO_DATA = 2
    UNSCHEDULED = 3

    @classmethod
    def _missing_(cls, value) -> StopTimeScheduleRelationship | None:
        try:
            if isinstance(value, str):
                value = int(value)
                for member in cls:
                    if member.value == value:
                        return member
        except ValueError:
            pass

        return cls.SCHEDULED


class TripDescriptorScheduleRelationship(Enum):
    SCHEDULED = 0
    ADDED = 1
    UNSCHEDULED = 2
    CANCELED = 3
    REPLACEMENT = 5
    DUPLICATED = 6
    DELETED = 7
    NEW = 8
