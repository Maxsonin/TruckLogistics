from dataclasses import dataclass


@dataclass(frozen=True)
class CreateTruckDTO:
    plate_number: str
    model: str | None = None


@dataclass(frozen=True)
class UpdateTruckDTO:
    plate_number: str
    model: str | None = None
