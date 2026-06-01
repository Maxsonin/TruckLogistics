from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from app.core.assignment.dto.assignment import CreateAssignmentDTO
from app.core.assignment.services.assignment_service import AssignmentService
from app.core.domain.assignment import Assignment, AssignmentStatus
from app.core.domain.driver import Driver
from app.core.domain.truck import Truck


class FakeAssignmentRepo:
    def __init__(self, assignments: list[Assignment] | None = None) -> None:
        self._data: dict[str, Assignment] = {a.id: a for a in (assignments or [])}
        self._next_id = 1

    def create(self, assignment: Assignment) -> Assignment:
        saved = replace(assignment, id=str(self._next_id))
        self._next_id += 1
        self._data[saved.id] = saved
        return saved

    def get_by_id(self, id: str) -> Assignment | None:
        return self._data.get(id)

    def get_all(self) -> list[Assignment]:
        return list(self._data.values())

    def cancel(self, id: str) -> Assignment:
        cancelled = replace(self._data[id], cancelled_at=datetime.now(timezone.utc))
        self._data[id] = cancelled
        return cancelled


class FakeTruckLookup:
    def __init__(self, trucks: list[Truck]) -> None:
        self._data = {t.id: t for t in trucks}

    def get_by_id(self, id: str) -> Truck | None:
        return self._data.get(id)


class FakeDriverLookup:
    def __init__(self, drivers: list[Driver]) -> None:
        self._data = {d.id: d for d in drivers}

    def get_by_id(self, id: str) -> Driver | None:
        return self._data.get(id)


def active_assignment(id: str, truck_id: str, driver_id: str) -> Assignment:
    return Assignment(
        id=id,
        truck_id=truck_id,
        driver_id=driver_id,
        origin="A",
        destination="B",
        started_at=datetime.now(timezone.utc) + timedelta(hours=1),
        estimated_duration_min=120,
    )


def completed_assignment(id: str, truck_id: str, driver_id: str) -> Assignment:
    return Assignment(
        id=id,
        truck_id=truck_id,
        driver_id=driver_id,
        origin="A",
        destination="B",
        started_at=datetime.now(timezone.utc) - timedelta(hours=5),
        estimated_duration_min=60,
    )


def cancelled_assignment(id: str, truck_id: str, driver_id: str) -> Assignment:
    return Assignment(
        id=id,
        truck_id=truck_id,
        driver_id=driver_id,
        origin="A",
        destination="B",
        started_at=datetime.now(timezone.utc) - timedelta(hours=1),
        estimated_duration_min=120,
        cancelled_at=datetime.now(timezone.utc),
    )


def make_dto(truck_id: str = "t1", driver_id: str = "d1") -> CreateAssignmentDTO:
    return CreateAssignmentDTO(
        truck_id=truck_id,
        driver_id=driver_id,
        origin="Origin City",
        destination="Destination City",
        estimated_duration_min=120,
        started_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )


class TestCreateAssignment:
    def test_creates_successfully(self) -> None:
        service = AssignmentService(FakeAssignmentRepo())
        result = service.create_assignment(make_dto())
        assert result.truck_id == "t1"
        assert result.driver_id == "d1"
        assert result.id != ""

    def test_raises_when_truck_has_active_assignment(self) -> None:
        repo = FakeAssignmentRepo([active_assignment("a1", "t1", "d1")])
        service = AssignmentService(repo)
        with pytest.raises(ValueError, match="t1"):
            service.create_assignment(make_dto(truck_id="t1", driver_id="d2"))

    def test_error_includes_plate_number_when_truck_lookup_provided(self) -> None:
        repo = FakeAssignmentRepo([active_assignment("a1", "t1", "d1")])
        truck_lookup = FakeTruckLookup([Truck(id="t1", plate_number="ABC-123")])
        service = AssignmentService(repo, truck_repo=truck_lookup)
        with pytest.raises(ValueError, match="ABC-123"):
            service.create_assignment(make_dto(truck_id="t1", driver_id="d2"))

    def test_raises_when_driver_has_active_assignment(self) -> None:
        repo = FakeAssignmentRepo([active_assignment("a1", "t1", "d1")])
        service = AssignmentService(repo)
        with pytest.raises(ValueError, match="d1"):
            service.create_assignment(make_dto(truck_id="t2", driver_id="d1"))

    def test_error_includes_driver_name_when_driver_lookup_provided(self) -> None:
        repo = FakeAssignmentRepo([active_assignment("a1", "t1", "d1")])
        driver_lookup = FakeDriverLookup([Driver(id="d1", name="John Doe")])
        service = AssignmentService(repo, driver_repo=driver_lookup)
        with pytest.raises(ValueError, match="John Doe"):
            service.create_assignment(make_dto(truck_id="t2", driver_id="d1"))

    def test_succeeds_when_truck_has_completed_assignment(self) -> None:
        repo = FakeAssignmentRepo([completed_assignment("a1", "t1", "d1")])
        service = AssignmentService(repo)
        result = service.create_assignment(make_dto(truck_id="t1", driver_id="d2"))
        assert result.truck_id == "t1"

    def test_succeeds_when_truck_has_cancelled_assignment(self) -> None:
        repo = FakeAssignmentRepo([cancelled_assignment("a1", "t1", "d1")])
        service = AssignmentService(repo)
        result = service.create_assignment(make_dto(truck_id="t1", driver_id="d2"))
        assert result.truck_id == "t1"

    def test_succeeds_when_driver_has_completed_assignment(self) -> None:
        repo = FakeAssignmentRepo([completed_assignment("a1", "t1", "d1")])
        service = AssignmentService(repo)
        result = service.create_assignment(make_dto(truck_id="t2", driver_id="d1"))
        assert result.driver_id == "d1"


class TestGetAssignment:
    def test_returns_assignment(self) -> None:
        repo = FakeAssignmentRepo([active_assignment("a1", "t1", "d1")])
        service = AssignmentService(repo)
        result = service.get_assignment("a1")
        assert result.id == "a1"

    def test_raises_when_not_found(self) -> None:
        service = AssignmentService(FakeAssignmentRepo())
        with pytest.raises(ValueError, match="not found"):
            service.get_assignment("missing")


class TestListAssignments:
    def test_returns_all_when_no_filter(self) -> None:
        repo = FakeAssignmentRepo([
            active_assignment("a1", "t1", "d1"),
            completed_assignment("a2", "t2", "d2"),
        ])
        service = AssignmentService(repo)
        assert len(service.list_assignments()) == 2

    def test_filters_active(self) -> None:
        repo = FakeAssignmentRepo([
            active_assignment("a1", "t1", "d1"),
            completed_assignment("a2", "t2", "d2"),
        ])
        service = AssignmentService(repo)
        results = service.list_assignments(AssignmentStatus.ACTIVE)
        assert len(results) == 1
        assert results[0].id == "a1"

    def test_filters_completed(self) -> None:
        repo = FakeAssignmentRepo([
            active_assignment("a1", "t1", "d1"),
            completed_assignment("a2", "t2", "d2"),
        ])
        service = AssignmentService(repo)
        results = service.list_assignments(AssignmentStatus.COMPLETED)
        assert len(results) == 1
        assert results[0].id == "a2"

    def test_filters_cancelled(self) -> None:
        repo = FakeAssignmentRepo([
            active_assignment("a1", "t1", "d1"),
            cancelled_assignment("a3", "t3", "d3"),
        ])
        service = AssignmentService(repo)
        results = service.list_assignments(AssignmentStatus.CANCELLED)
        assert len(results) == 1
        assert results[0].id == "a3"

    def test_returns_empty_when_no_assignments(self) -> None:
        service = AssignmentService(FakeAssignmentRepo())
        assert service.list_assignments() == []


class TestCancelAssignment:
    def test_cancels_active_assignment(self) -> None:
        repo = FakeAssignmentRepo([active_assignment("a1", "t1", "d1")])
        service = AssignmentService(repo)
        result = service.cancel_assignment("a1")
        assert result.status == AssignmentStatus.CANCELLED

    def test_raises_when_not_found(self) -> None:
        service = AssignmentService(FakeAssignmentRepo())
        with pytest.raises(ValueError, match="not found"):
            service.cancel_assignment("missing")

    def test_raises_when_already_cancelled(self) -> None:
        repo = FakeAssignmentRepo([cancelled_assignment("a1", "t1", "d1")])
        service = AssignmentService(repo)
        with pytest.raises(ValueError, match="already cancelled"):
            service.cancel_assignment("a1")

    def test_raises_when_already_completed(self) -> None:
        repo = FakeAssignmentRepo([completed_assignment("a1", "t1", "d1")])
        service = AssignmentService(repo)
        with pytest.raises(ValueError, match="already completed"):
            service.cancel_assignment("a1")
