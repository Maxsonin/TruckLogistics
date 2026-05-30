from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum


class AssignmentStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class Assignment:
    id: str
    truck_id: str
    started_at: datetime
    estimated_duration_min: int
    is_cancelled: bool
    driver_id: str | None = None

    @property
    def status(self) -> AssignmentStatus:
        if self.is_cancelled:
            return AssignmentStatus.CANCELLED
        deadline = self.started_at + timedelta(minutes=self.estimated_duration_min)
        if datetime.now(timezone.utc) >= deadline:
            return AssignmentStatus.COMPLETED
        return AssignmentStatus.ACTIVE
