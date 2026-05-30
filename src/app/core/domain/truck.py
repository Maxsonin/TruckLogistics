from dataclasses import dataclass


@dataclass(frozen=True)
class Truck:
    id: str
    plate_number: str
    model: str | None = None
