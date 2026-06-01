from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.domain.truck import Truck
from app.infrastructure.db.models.truck import TruckORM
from app.infrastructure.db.repositories._utils import find_by_id_prefix


class TruckRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, truck: Truck) -> Truck:
        row = TruckORM(
            plate_number=truck.plate_number,
            model=truck.model,
        )

        self.session.add(row)
        self.session.flush()

        return Truck(
            id=row.id,
            plate_number=row.plate_number,
            model=row.model,
        )

    def get_by_id(self, id: str) -> Truck | None:
        row = find_by_id_prefix(self.session, TruckORM, id)
        if row is None:
            return None
        return Truck(id=row.id, plate_number=row.plate_number, model=row.model)

    def get_all(self) -> list[Truck]:
        rows = self.session.scalars(select(TruckORM)).all()

        return [
            Truck(
                id=r.id,
                plate_number=r.plate_number,
                model=r.model,
            )
            for r in rows
        ]

    def update(self, truck: Truck) -> Truck:
        row = find_by_id_prefix(self.session, TruckORM, truck.id)
        if row is None:
            raise ValueError(f"Truck '{truck.id}' not found")
        row.plate_number = truck.plate_number
        row.model = truck.model
        self.session.flush()
        return Truck(id=row.id, plate_number=row.plate_number, model=row.model)

    def delete(self, id: str) -> None:
        row = find_by_id_prefix(self.session, TruckORM, id)
        if row is not None:
            self.session.delete(row)
            self.session.flush()
