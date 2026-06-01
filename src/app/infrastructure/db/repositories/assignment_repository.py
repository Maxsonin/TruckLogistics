from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.domain.assignment import Assignment, AssignmentStatus
from app.infrastructure.db.models.assignment import AssignmentORM
from app.infrastructure.db.repositories._utils import find_by_id_prefix


def _to_domain(row: AssignmentORM) -> Assignment:
    return Assignment(
        id=row.id,
        truck_id=row.truck_id,
        driver_id=row.driver_id,
        origin=row.origin,
        destination=row.destination,
        started_at=row.started_at,
        estimated_duration_min=row.estimated_duration_min,
        cancelled_at=row.cancelled_at,
        created_at=row.created_at,
    )


class AssignmentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, assignment: Assignment) -> Assignment:
        row = AssignmentORM(
            truck_id=assignment.truck_id,
            driver_id=assignment.driver_id,
            origin=assignment.origin,
            destination=assignment.destination,
            started_at=assignment.started_at,
            estimated_duration_min=assignment.estimated_duration_min,
            cancelled_at=assignment.cancelled_at,
            created_at=assignment.created_at,
        )
        self.session.add(row)
        self.session.flush()
        return _to_domain(row)

    def get_by_id(self, id: str) -> Assignment | None:
        row = find_by_id_prefix(self.session, AssignmentORM, id)
        return _to_domain(row) if row is not None else None

    def get_all(self) -> list[Assignment]:
        rows = self.session.scalars(select(AssignmentORM)).all()
        return [_to_domain(r) for r in rows]

    def cancel(self, id: str) -> Assignment:
        row = find_by_id_prefix(self.session, AssignmentORM, id)
        if row is None:
            raise ValueError(f"Assignment '{id}' not found")
        row.cancelled_at = datetime.now(timezone.utc)
        self.session.flush()
        return _to_domain(row)

    def get_active_truck_ids(self) -> frozenset[str]:
        return frozenset(
            a.truck_id for a in self.get_all() if a.status == AssignmentStatus.ACTIVE
        )

    def get_active_driver_ids(self) -> frozenset[str]:
        return frozenset(
            a.driver_id for a in self.get_all() if a.status == AssignmentStatus.ACTIVE
        )
