from enum import Enum
from typing import Protocol

from app.core.domain.truck import Truck
from app.core.truck.dto.truck import CreateTruckDTO, UpdateTruckDTO


class TruckFilter(str, Enum):
    ALL = "all"
    ACTIVE = "active"
    INACTIVE = "inactive"


class TruckRepositoryProtocol(Protocol):
    def create(self, truck: Truck) -> Truck: ...
    def get_all(self) -> list[Truck]: ...
    def get_by_id(self, id: str) -> Truck | None: ...
    def update(self, truck: Truck) -> Truck: ...
    def delete(self, id: str) -> None: ...


class AssignmentQueryProtocol(Protocol):
    def get_active_truck_ids(self) -> frozenset[str]: ...


class TruckService:
    def __init__(
        self,
        repo: TruckRepositoryProtocol,
        assignment_query: AssignmentQueryProtocol | None = None,
    ) -> None:
        self.repo = repo
        self.assignment_query = assignment_query

    def register_truck(self, cmd: CreateTruckDTO) -> Truck:
        plate = cmd.plate_number.strip().upper()

        if len(plate) < 3:
            raise ValueError("Invalid plate number")

        truck = Truck(
            id="",
            plate_number=plate,
            model=cmd.model,
        )

        return self.repo.create(truck)

    def get_truck(self, id: str) -> Truck:
        truck = self.repo.get_by_id(id)
        if truck is None:
            raise ValueError(f"Truck '{id}' not found")
        return truck

    def update_truck(self, truck_id: str, cmd: UpdateTruckDTO) -> Truck:
        existing = self.repo.get_by_id(truck_id)
        if existing is None:
            raise ValueError(f"Truck '{truck_id}' not found")
        plate = cmd.plate_number.strip().upper()
        if len(plate) < 3:
            raise ValueError("Invalid plate number")
        return self.repo.update(Truck(id=truck_id, plate_number=plate, model=cmd.model))

    def delete_truck(self, truck_id: str) -> None:
        if self.repo.get_by_id(truck_id) is None:
            raise ValueError(f"Truck '{truck_id}' not found")
        if self.assignment_query:
            if truck_id in self.assignment_query.get_active_truck_ids():
                raise ValueError("Cannot delete a truck with an active assignment")
        self.repo.delete(truck_id)

    def list_trucks(self, filter: TruckFilter = TruckFilter.ALL) -> list[Truck]:
        trucks = self.repo.get_all()

        if filter == TruckFilter.ALL:
            return trucks

        active_ids = (
            self.assignment_query.get_active_truck_ids()
            if self.assignment_query
            else frozenset()
        )

        if filter == TruckFilter.ACTIVE:
            return [t for t in trucks if t.id in active_ids]

        return [t for t in trucks if t.id not in active_ids]
