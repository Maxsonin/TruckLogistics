from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base


class AssignmentORM(Base):
    __tablename__ = "assignments"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        server_default=text("gen_random_uuid()::text"),
    )
    truck_id: Mapped[str] = mapped_column(
        String, ForeignKey("trucks.id"), nullable=False
    )
    driver_id: Mapped[str] = mapped_column(
        String, ForeignKey("drivers.id"), nullable=False
    )
    origin: Mapped[str] = mapped_column(String(200), nullable=False)
    destination: Mapped[str] = mapped_column(String(200), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    estimated_duration_min: Mapped[int] = mapped_column(Integer, nullable=False)
    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
