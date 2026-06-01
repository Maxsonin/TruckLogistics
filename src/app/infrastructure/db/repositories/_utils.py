from typing import Any, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

_T = TypeVar("_T")


def find_by_id_prefix(session: Session, model: type[_T], id: str) -> _T | None:
    """Return the row whose primary key exactly matches *id*, or whose PK starts
    with *id* when exactly one such row exists.  Returns None on no match or an
    ambiguous prefix."""
    row: Any = session.get(model, id)
    if row is not None:
        return row
    rows = session.scalars(select(model).where(model.id.like(f"{id}%"))).all()  # type: ignore[attr-defined]
    return rows[0] if len(rows) == 1 else None
