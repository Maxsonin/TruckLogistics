from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.domain.driver import Driver
from app.infrastructure.db.models.driver import DriverORM
from app.infrastructure.db.repositories._utils import find_by_id_prefix


def _to_domain(row: DriverORM) -> Driver:
    return Driver(id=row.id, name=row.name, phone=row.phone)


class DriverRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, driver: Driver) -> Driver:
        row = DriverORM(name=driver.name, phone=driver.phone)
        self.session.add(row)
        self.session.flush()
        return _to_domain(row)

    def get_by_id(self, id: str) -> Driver | None:
        row = find_by_id_prefix(self.session, DriverORM, id)
        return _to_domain(row) if row is not None else None

    def get_all(self) -> list[Driver]:
        rows = self.session.scalars(select(DriverORM)).all()
        return [_to_domain(r) for r in rows]

    def update(self, driver: Driver) -> Driver:
        row = find_by_id_prefix(self.session, DriverORM, driver.id)
        if row is None:
            raise ValueError(f"Driver '{driver.id}' not found")
        row.name = driver.name
        row.phone = driver.phone
        self.session.flush()
        return _to_domain(row)

    def delete(self, id: str) -> None:
        row = find_by_id_prefix(self.session, DriverORM, id)
        if row is not None:
            self.session.delete(row)
            self.session.flush()
