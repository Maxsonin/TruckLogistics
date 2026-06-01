from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum


class AssignmentStatus(Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class Assignment:
    id: str
    truck_id: str
    driver_id: str
    origin: str
    destination: str
    started_at: datetime
    estimated_duration_min: int
    cancelled_at: datetime | None = None
    created_at: datetime | None = None

    @property
    def status(self) -> AssignmentStatus:
        if self.cancelled_at is not None:
            return AssignmentStatus.CANCELLED
        deadline = self.started_at + timedelta(minutes=self.estimated_duration_min)
        if datetime.now(timezone.utc) >= deadline:
            return AssignmentStatus.COMPLETED
        return AssignmentStatus.ACTIVE
