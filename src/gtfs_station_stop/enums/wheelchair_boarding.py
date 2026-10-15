from enum import Enum


class WheelchairBoarding(Enum):
    NO_INFORMATION = 0
    ACCESSIBLE = 1
    INACCESSIBLE = 2

    def __str__(self) -> str:
        if self == WheelchairBoarding.NO_INFORMATION:
            return "no_information"
        elif self == WheelchairBoarding.ACCESSIBLE:
            return "accessible"
        else:  # self == WheelchairBoarding.INACCESSIBLE:
            return "inaccessible"

    @classmethod
    def _missing_(cls, value: object) -> WheelchairBoarding:
        try:
            if isinstance(value, str):
                value = int(value)
                for member in cls:
                    if member.value == value:
                        return member
        except ValueError:
            pass

        return cls.NO_INFORMATION
