from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CreateTruckDTO:
    plate_number: str
    model: Optional[str] = None