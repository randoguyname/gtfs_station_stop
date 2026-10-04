from dataclasses import dataclass

@dataclass(order=True)
class Alert:
    """Class for keeping alert data."""

    ends_at: float | None
    header_text: dict[str, str]  # key is language
    description_text: dict[str, str]  # key is language
