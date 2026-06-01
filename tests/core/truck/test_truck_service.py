import pytest

from app.core.domain.truck import Truck
from app.core.truck.dto.truck import CreateTruckDTO, UpdateTruckDTO
from app.core.truck.services.truck_service import TruckFilter, TruckService


class FakeTruckRepo:
    def __init__(self, trucks: list[Truck] | None = None) -> None:
        self._data: dict[str, Truck] = {t.id: t for t in (trucks or [])}
        self._next_id = 1

    def create(self, truck: Truck) -> Truck:
        saved = Truck(id=str(self._next_id), plate_number=truck.plate_number, model=truck.model)
        self._next_id += 1
        self._data[saved.id] = saved
        return saved

    def get_all(self) -> list[Truck]:
        return list(self._data.values())

    def get_by_id(self, id: str) -> Truck | None:
        return self._data.get(id)

    def update(self, truck: Truck) -> Truck:
        self._data[truck.id] = truck
        return truck

    def delete(self, id: str) -> None:
        self._data.pop(id, None)


class FakeAssignmentQuery:
    def __init__(self, active_ids: frozenset[str] = frozenset()) -> None:
        self._active_ids = active_ids

    def get_active_truck_ids(self) -> frozenset[str]:
        return self._active_ids


class TestRegisterTruck:
    def test_creates_truck_with_valid_plate(self) -> None:
        service = TruckService(FakeTruckRepo())
        result = service.register_truck(CreateTruckDTO(plate_number="ABC-123"))
        assert result.plate_number == "ABC-123"

    def test_strips_and_uppercases_plate(self) -> None:
        service = TruckService(FakeTruckRepo())
        result = service.register_truck(CreateTruckDTO(plate_number="  abc-123  "))
        assert result.plate_number == "ABC-123"

    def test_raises_when_plate_too_short(self) -> None:
        service = TruckService(FakeTruckRepo())
        with pytest.raises(ValueError, match="Invalid plate number"):
            service.register_truck(CreateTruckDTO(plate_number="AB"))

    def test_raises_when_plate_is_whitespace_only(self) -> None:
        service = TruckService(FakeTruckRepo())
        with pytest.raises(ValueError, match="Invalid plate number"):
            service.register_truck(CreateTruckDTO(plate_number="   "))

    def test_accepts_minimum_three_char_plate(self) -> None:
        service = TruckService(FakeTruckRepo())
        result = service.register_truck(CreateTruckDTO(plate_number="ABC"))
        assert result.plate_number == "ABC"

    def test_stores_optional_model(self) -> None:
        service = TruckService(FakeTruckRepo())
        result = service.register_truck(CreateTruckDTO(plate_number="ABC-123", model="Volvo FH"))
        assert result.model == "Volvo FH"

    def test_model_is_none_by_default(self) -> None:
        service = TruckService(FakeTruckRepo())
        result = service.register_truck(CreateTruckDTO(plate_number="ABC-123"))
        assert result.model is None


class TestGetTruck:
    def test_returns_existing_truck(self) -> None:
        repo = FakeTruckRepo([Truck(id="1", plate_number="ABC-123")])
        service = TruckService(repo)
        result = service.get_truck("1")
        assert result.plate_number == "ABC-123"

    def test_raises_when_not_found(self) -> None:
        service = TruckService(FakeTruckRepo())
        with pytest.raises(ValueError, match="not found"):
            service.get_truck("missing")


class TestUpdateTruck:
    def test_updates_plate_successfully(self) -> None:
        repo = FakeTruckRepo([Truck(id="1", plate_number="OLD-111")])
        service = TruckService(repo)
        result = service.update_truck("1", UpdateTruckDTO(plate_number="NEW-222"))
        assert result.plate_number == "NEW-222"

    def test_normalizes_plate_on_update(self) -> None:
        repo = FakeTruckRepo([Truck(id="1", plate_number="OLD-111")])
        service = TruckService(repo)
        result = service.update_truck("1", UpdateTruckDTO(plate_number="  new-222  "))
        assert result.plate_number == "NEW-222"

    def test_raises_when_not_found(self) -> None:
        service = TruckService(FakeTruckRepo())
        with pytest.raises(ValueError, match="not found"):
            service.update_truck("missing", UpdateTruckDTO(plate_number="ABC-123"))

    def test_raises_on_short_plate(self) -> None:
        repo = FakeTruckRepo([Truck(id="1", plate_number="ABC-123")])
        service = TruckService(repo)
        with pytest.raises(ValueError, match="Invalid plate number"):
            service.update_truck("1", UpdateTruckDTO(plate_number="AB"))


class TestDeleteTruck:
    def test_deletes_truck_successfully(self) -> None:
        repo = FakeTruckRepo([Truck(id="1", plate_number="ABC-123")])
        service = TruckService(repo)
        service.delete_truck("1")
        assert repo.get_by_id("1") is None

    def test_raises_when_not_found(self) -> None:
        service = TruckService(FakeTruckRepo())
        with pytest.raises(ValueError, match="not found"):
            service.delete_truck("missing")

    def test_raises_when_truck_has_active_assignment(self) -> None:
        repo = FakeTruckRepo([Truck(id="1", plate_number="ABC-123")])
        query = FakeAssignmentQuery(frozenset(["1"]))
        service = TruckService(repo, assignment_query=query)
        with pytest.raises(ValueError, match="active assignment"):
            service.delete_truck("1")

    def test_deletes_when_truck_has_no_active_assignment(self) -> None:
        repo = FakeTruckRepo([Truck(id="1", plate_number="ABC-123")])
        query = FakeAssignmentQuery(frozenset())
        service = TruckService(repo, assignment_query=query)
        service.delete_truck("1")
        assert repo.get_by_id("1") is None

    def test_skips_active_check_without_assignment_query(self) -> None:
        repo = FakeTruckRepo([Truck(id="1", plate_number="ABC-123")])
        service = TruckService(repo)
        service.delete_truck("1")
        assert repo.get_by_id("1") is None


class TestListTrucks:
    def test_all_filter_returns_every_truck(self) -> None:
        repo = FakeTruckRepo([
            Truck(id="1", plate_number="A-111"),
            Truck(id="2", plate_number="A-222"),
        ])
        service = TruckService(repo)
        assert len(service.list_trucks(TruckFilter.ALL)) == 2

    def test_active_filter_returns_trucks_with_active_assignments(self) -> None:
        repo = FakeTruckRepo([
            Truck(id="1", plate_number="A-111"),
            Truck(id="2", plate_number="A-222"),
        ])
        service = TruckService(repo, assignment_query=FakeAssignmentQuery(frozenset(["1"])))
        result = service.list_trucks(TruckFilter.ACTIVE)
        assert len(result) == 1
        assert result[0].id == "1"

    def test_inactive_filter_returns_trucks_without_active_assignments(self) -> None:
        repo = FakeTruckRepo([
            Truck(id="1", plate_number="A-111"),
            Truck(id="2", plate_number="A-222"),
        ])
        service = TruckService(repo, assignment_query=FakeAssignmentQuery(frozenset(["1"])))
        result = service.list_trucks(TruckFilter.INACTIVE)
        assert len(result) == 1
        assert result[0].id == "2"

    def test_active_filter_without_query_returns_empty_list(self) -> None:
        repo = FakeTruckRepo([Truck(id="1", plate_number="A-111")])
        service = TruckService(repo)
        assert service.list_trucks(TruckFilter.ACTIVE) == []

    def test_inactive_filter_without_query_returns_all(self) -> None:
        repo = FakeTruckRepo([Truck(id="1", plate_number="A-111")])
        service = TruckService(repo)
        result = service.list_trucks(TruckFilter.INACTIVE)
        assert len(result) == 1

    def test_default_filter_is_all(self) -> None:
        repo = FakeTruckRepo([
            Truck(id="1", plate_number="A-111"),
            Truck(id="2", plate_number="A-222"),
        ])
        service = TruckService(repo)
        assert len(service.list_trucks()) == 2
