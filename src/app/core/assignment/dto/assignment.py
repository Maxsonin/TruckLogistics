from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CreateAssignmentDTO:
    truck_id: str
    driver_id: str
    origin: str
    destination: str
    estimated_duration_min: int
    started_at: datetime
    truck_label: str = ""
    driver_label: str = ""
