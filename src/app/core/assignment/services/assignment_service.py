from datetime import datetime, timezone
from typing import Protocol

from app.core.assignment.dto.assignment import CreateAssignmentDTO
from app.core.domain.assignment import Assignment, AssignmentStatus
from app.core.domain.driver import Driver
from app.core.domain.truck import Truck


class AssignmentRepositoryProtocol(Protocol):
    def create(self, assignment: Assignment) -> Assignment: ...
    def get_by_id(self, id: str) -> Assignment | None: ...
    def get_all(self) -> list[Assignment]: ...
    def cancel(self, id: str) -> Assignment: ...


class TruckLookupProtocol(Protocol):
    def get_by_id(self, id: str) -> Truck | None: ...


class DriverLookupProtocol(Protocol):
    def get_by_id(self, id: str) -> Driver | None: ...


class AssignmentService:
    def __init__(
        self,
        repo: AssignmentRepositoryProtocol,
        truck_repo: TruckLookupProtocol | None = None,
        driver_repo: DriverLookupProtocol | None = None,
    ) -> None:
        self.repo = repo
        self.truck_repo = truck_repo
        self.driver_repo = driver_repo

    def create_assignment(self, cmd: CreateAssignmentDTO) -> Assignment:
        all_assignments = self.repo.get_all()

        truck_conflict = any(
            a.truck_id == cmd.truck_id and a.status == AssignmentStatus.ACTIVE
            for a in all_assignments
        )
        if truck_conflict:
            truck = self.truck_repo.get_by_id(cmd.truck_id) if self.truck_repo else None
            label = truck.plate_number if truck else cmd.truck_id
            raise ValueError(f"Truck '{label}' already has an active assignment")

        driver_conflict = any(
            a.driver_id == cmd.driver_id and a.status == AssignmentStatus.ACTIVE
            for a in all_assignments
        )
        if driver_conflict:
            driver = self.driver_repo.get_by_id(cmd.driver_id) if self.driver_repo else None
            label = driver.name if driver else cmd.driver_id
            raise ValueError(f"Driver '{label}' already has an active assignment")

        assignment = Assignment(
            id="",
            truck_id=cmd.truck_id,
            driver_id=cmd.driver_id,
            origin=cmd.origin,
            destination=cmd.destination,
            started_at=cmd.started_at,
            estimated_duration_min=cmd.estimated_duration_min,
            created_at=datetime.now(timezone.utc),
        )
        return self.repo.create(assignment)

    def get_assignment(self, id: str) -> Assignment:
        assignment = self.repo.get_by_id(id)
        if assignment is None:
            raise ValueError(f"Assignment '{id}' not found")
        return assignment

    def list_assignments(
        self, status: AssignmentStatus | None = None
    ) -> list[Assignment]:
        assignments = self.repo.get_all()
        if status is None:
            return assignments
        return [a for a in assignments if a.status == status]

    def cancel_assignment(self, id: str) -> Assignment:
        assignment = self.repo.get_by_id(id)
        if assignment is None:
            raise ValueError(f"Assignment '{id}' not found")
        if assignment.status == AssignmentStatus.CANCELLED:
            raise ValueError(f"Assignment '{id}' is already cancelled")
        if assignment.status == AssignmentStatus.COMPLETED:
            raise ValueError(f"Assignment '{id}' is already completed")
        return self.repo.cancel(id)
