from sqlalchemy import String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base


class DriverORM(Base):
    __tablename__ = "drivers"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        server_default=text("gen_random_uuid()::text"),
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
