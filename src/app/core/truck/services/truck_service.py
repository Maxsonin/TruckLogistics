import uuid
from enum import Enum
from typing import Protocol

from app.core.domain.truck import Truck
from app.core.truck.dto.truck import CreateTruckDTO


class TruckFilter(str, Enum):
    ALL = "all"
    ACTIVE = "active"
    INACTIVE = "inactive"


class TruckRepositoryProtocol(Protocol):
    def create(self, truck: Truck) -> Truck: ...
    def get_all(self) -> list[Truck]: ...
    def get_by_id(self, id: str) -> Truck | None: ...


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
            id=str(uuid.uuid4()),
            plate_number=plate,
            model=cmd.model,
        )

        return self.repo.create(truck)

    def get_truck(self, id: str) -> Truck:
        truck = self.repo.get_by_id(id)
        if truck is None:
            raise ValueError(f"Truck '{id}' not found")
        return truck

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
