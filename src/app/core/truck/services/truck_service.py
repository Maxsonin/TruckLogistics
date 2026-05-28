import uuid

from app.core.domain.truck import Truck
from app.core.truck.dto.truck import CreateTruckDTO
from app.infrastructure.db.repositories.truck_repository import TruckRepository


class TruckService:
    def __init__(self, repo: TruckRepository):
        self.repo = repo

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