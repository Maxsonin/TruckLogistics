from typing import Protocol

from app.core.domain.driver import Driver
from app.core.driver.dto.driver import CreateDriverDTO, UpdateDriverDTO


class DriverRepositoryProtocol(Protocol):
    def create(self, driver: Driver) -> Driver: ...
    def get_all(self) -> list[Driver]: ...
    def get_by_id(self, id: str) -> Driver | None: ...
    def update(self, driver: Driver) -> Driver: ...
    def delete(self, id: str) -> None: ...


class AssignmentQueryProtocol(Protocol):
    def get_active_driver_ids(self) -> frozenset[str]: ...


class DriverService:
    def __init__(
        self,
        repo: DriverRepositoryProtocol,
        assignment_query: AssignmentQueryProtocol | None = None,
    ) -> None:
        self.repo = repo
        self.assignment_query = assignment_query

    def register_driver(self, cmd: CreateDriverDTO) -> Driver:
        name = cmd.name.strip()
        if not name:
            raise ValueError("Driver name cannot be empty")

        driver = Driver(id="", name=name, phone=cmd.phone)
        return self.repo.create(driver)

    def get_driver(self, id: str) -> Driver:
        driver = self.repo.get_by_id(id)
        if driver is None:
            raise ValueError(f"Driver '{id}' not found")
        return driver

    def update_driver(self, driver_id: str, cmd: UpdateDriverDTO) -> Driver:
        if self.repo.get_by_id(driver_id) is None:
            raise ValueError(f"Driver '{driver_id}' not found")
        name = cmd.name.strip()
        if not name:
            raise ValueError("Driver name cannot be empty")
        return self.repo.update(Driver(id=driver_id, name=name, phone=cmd.phone))

    def delete_driver(self, driver_id: str) -> None:
        if self.repo.get_by_id(driver_id) is None:
            raise ValueError(f"Driver '{driver_id}' not found")
        if self.assignment_query:
            if driver_id in self.assignment_query.get_active_driver_ids():
                raise ValueError("Cannot delete a driver with an active assignment")
        self.repo.delete(driver_id)

    def list_drivers(self) -> list[Driver]:
        return self.repo.get_all()
