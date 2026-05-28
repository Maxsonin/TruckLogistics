import uuid
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.db.base import Base


class TruckORM(Base):
    __tablename__ = "trucks"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    
    plate_number: Mapped[str] = mapped_column(String(20), unique=True)
    model: Mapped[str | None] = mapped_column(String(50), nullable=True)