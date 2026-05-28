from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Truck:
    id: str
    plate_number: str
    model: Optional[str] = None