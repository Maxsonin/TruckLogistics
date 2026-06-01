import pytest

from app.core.domain.driver import Driver
from app.core.driver.dto.driver import CreateDriverDTO, UpdateDriverDTO
from app.core.driver.services.driver_service import DriverService


class FakeDriverRepo:
    def __init__(self, drivers: list[Driver] | None = None) -> None:
        self._data: dict[str, Driver] = {d.id: d for d in (drivers or [])}
        self._next_id = 1

    def create(self, driver: Driver) -> Driver:
        saved = Driver(id=str(self._next_id), name=driver.name, phone=driver.phone)
        self._next_id += 1
        self._data[saved.id] = saved
        return saved

    def get_all(self) -> list[Driver]:
        return list(self._data.values())

    def get_by_id(self, id: str) -> Driver | None:
        return self._data.get(id)

    def update(self, driver: Driver) -> Driver:
        self._data[driver.id] = driver
        return driver

    def delete(self, id: str) -> None:
        self._data.pop(id, None)


class FakeAssignmentQuery:
    def __init__(self, active_ids: frozenset[str] = frozenset()) -> None:
        self._active_ids = active_ids

    def get_active_driver_ids(self) -> frozenset[str]:
        return self._active_ids


class TestRegisterDriver:
    def test_creates_driver_with_valid_name(self) -> None:
        service = DriverService(FakeDriverRepo())
        result = service.register_driver(CreateDriverDTO(name="John Doe"))
        assert result.name == "John Doe"

    def test_strips_whitespace_from_name(self) -> None:
        service = DriverService(FakeDriverRepo())
        result = service.register_driver(CreateDriverDTO(name="  John Doe  "))
        assert result.name == "John Doe"

    def test_raises_on_empty_name(self) -> None:
        service = DriverService(FakeDriverRepo())
        with pytest.raises(ValueError, match="cannot be empty"):
            service.register_driver(CreateDriverDTO(name=""))

    def test_raises_on_whitespace_only_name(self) -> None:
        service = DriverService(FakeDriverRepo())
        with pytest.raises(ValueError, match="cannot be empty"):
            service.register_driver(CreateDriverDTO(name="   "))

    def test_stores_optional_phone(self) -> None:
        service = DriverService(FakeDriverRepo())
        result = service.register_driver(CreateDriverDTO(name="John", phone="+1-555-0100"))
        assert result.phone == "+1-555-0100"

    def test_phone_is_none_by_default(self) -> None:
        service = DriverService(FakeDriverRepo())
        result = service.register_driver(CreateDriverDTO(name="John"))
        assert result.phone is None


class TestGetDriver:
    def test_returns_existing_driver(self) -> None:
        repo = FakeDriverRepo([Driver(id="1", name="John Doe")])
        service = DriverService(repo)
        result = service.get_driver("1")
        assert result.name == "John Doe"

    def test_raises_when_not_found(self) -> None:
        service = DriverService(FakeDriverRepo())
        with pytest.raises(ValueError, match="not found"):
            service.get_driver("missing")


class TestUpdateDriver:
    def test_updates_name_successfully(self) -> None:
        repo = FakeDriverRepo([Driver(id="1", name="Old Name")])
        service = DriverService(repo)
        result = service.update_driver("1", UpdateDriverDTO(name="New Name"))
        assert result.name == "New Name"

    def test_normalizes_name_on_update(self) -> None:
        repo = FakeDriverRepo([Driver(id="1", name="Old")])
        service = DriverService(repo)
        result = service.update_driver("1", UpdateDriverDTO(name="  New Name  "))
        assert result.name == "New Name"

    def test_raises_when_not_found(self) -> None:
        service = DriverService(FakeDriverRepo())
        with pytest.raises(ValueError, match="not found"):
            service.update_driver("missing", UpdateDriverDTO(name="Name"))

    def test_raises_on_empty_name(self) -> None:
        repo = FakeDriverRepo([Driver(id="1", name="John")])
        service = DriverService(repo)
        with pytest.raises(ValueError, match="cannot be empty"):
            service.update_driver("1", UpdateDriverDTO(name=""))

    def test_raises_on_whitespace_only_name(self) -> None:
        repo = FakeDriverRepo([Driver(id="1", name="John")])
        service = DriverService(repo)
        with pytest.raises(ValueError, match="cannot be empty"):
            service.update_driver("1", UpdateDriverDTO(name="   "))


class TestDeleteDriver:
    def test_deletes_driver_successfully(self) -> None:
        repo = FakeDriverRepo([Driver(id="1", name="John")])
        service = DriverService(repo)
        service.delete_driver("1")
        assert repo.get_by_id("1") is None

    def test_raises_when_not_found(self) -> None:
        service = DriverService(FakeDriverRepo())
        with pytest.raises(ValueError, match="not found"):
            service.delete_driver("missing")

    def test_raises_when_driver_has_active_assignment(self) -> None:
        repo = FakeDriverRepo([Driver(id="1", name="John")])
        query = FakeAssignmentQuery(frozenset(["1"]))
        service = DriverService(repo, assignment_query=query)
        with pytest.raises(ValueError, match="active assignment"):
            service.delete_driver("1")

    def test_deletes_when_driver_has_no_active_assignment(self) -> None:
        repo = FakeDriverRepo([Driver(id="1", name="John")])
        query = FakeAssignmentQuery(frozenset())
        service = DriverService(repo, assignment_query=query)
        service.delete_driver("1")
        assert repo.get_by_id("1") is None

    def test_skips_active_check_without_assignment_query(self) -> None:
        repo = FakeDriverRepo([Driver(id="1", name="John")])
        service = DriverService(repo)
        service.delete_driver("1")
        assert repo.get_by_id("1") is None


class TestListDrivers:
    def test_returns_all_drivers(self) -> None:
        repo = FakeDriverRepo([Driver(id="1", name="Alice"), Driver(id="2", name="Bob")])
        service = DriverService(repo)
        assert len(service.list_drivers()) == 2

    def test_returns_empty_list_when_no_drivers(self) -> None:
        service = DriverService(FakeDriverRepo())
        assert service.list_drivers() == []
