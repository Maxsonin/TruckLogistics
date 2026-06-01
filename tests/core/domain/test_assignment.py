from datetime import datetime, timedelta, timezone

import pytest

from app.core.domain.assignment import Assignment, AssignmentStatus


def make_assignment(**kwargs: object) -> Assignment:
    defaults: dict[str, object] = {
        "id": "test-id",
        "truck_id": "truck-1",
        "driver_id": "driver-1",
        "origin": "City A",
        "destination": "City B",
        "started_at": datetime.now(timezone.utc) + timedelta(hours=1),
        "estimated_duration_min": 60,
    }
    defaults.update(kwargs)
    return Assignment(**defaults)  # type: ignore[arg-type]


class TestAssignmentStatus:
    def test_cancelled_when_cancelled_at_is_set(self) -> None:
        a = make_assignment(cancelled_at=datetime.now(timezone.utc))
        assert a.status == AssignmentStatus.CANCELLED

    def test_cancelled_takes_priority_over_expired_deadline(self) -> None:
        past = datetime.now(timezone.utc) - timedelta(hours=5)
        a = make_assignment(
            started_at=past,
            estimated_duration_min=60,
            cancelled_at=datetime.now(timezone.utc),
        )
        assert a.status == AssignmentStatus.CANCELLED

    def test_active_when_deadline_is_in_the_future(self) -> None:
        a = make_assignment(
            started_at=datetime.now(timezone.utc) + timedelta(hours=1),
            estimated_duration_min=60,
        )
        assert a.status == AssignmentStatus.ACTIVE

    def test_completed_when_deadline_has_passed(self) -> None:
        a = make_assignment(
            started_at=datetime.now(timezone.utc) - timedelta(hours=5),
            estimated_duration_min=60,
        )
        assert a.status == AssignmentStatus.COMPLETED

    def test_completed_exactly_at_deadline(self) -> None:
        # started 60 min ago, duration 60 min → now is exactly at the deadline
        a = make_assignment(
            started_at=datetime.now(timezone.utc) - timedelta(minutes=60),
            estimated_duration_min=60,
        )
        assert a.status == AssignmentStatus.COMPLETED

    def test_active_just_before_deadline(self) -> None:
        a = make_assignment(
            started_at=datetime.now(timezone.utc) - timedelta(minutes=59),
            estimated_duration_min=60,
        )
        assert a.status == AssignmentStatus.ACTIVE

    def test_none_cancelled_at_does_not_trigger_cancelled(self) -> None:
        a = make_assignment(cancelled_at=None)
        assert a.status != AssignmentStatus.CANCELLED
