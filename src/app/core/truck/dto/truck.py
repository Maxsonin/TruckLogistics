from dataclasses import dataclass


@dataclass(frozen=True)
class CreateTruckDTO:
    plate_number: str
    model: str | None = None
