from typing import Optional

import typer

from app.core.truck.services.truck_service import TruckFilter, TruckService
from app.infrastructure.db.repositories.truck_repository import TruckRepository
from app.infrastructure.db.session import get_session

truck_app = typer.Typer(name="truck", help="Manage trucks")

_ID_COL = 10
_PLATE_COL = 14
_MODEL_COL = 20


def _fmt_row(id: str, plate: str, model: str) -> str:
    return f"{id:<{_ID_COL}}  {plate:<{_PLATE_COL}}  {model:<{_MODEL_COL}}"


def _print_trucks(trucks: list) -> None:  # type: ignore[type-arg]
    if not trucks:
        typer.echo("No trucks found.")
        return
    typer.echo(_fmt_row("ID", "PLATE", "MODEL"))
    typer.echo("-" * (_ID_COL + _PLATE_COL + _MODEL_COL + 4))
    for t in trucks:
        typer.echo(_fmt_row(t.id[:8], t.plate_number, t.model or "-"))


@truck_app.command("list")
def list_trucks(
    filter: Optional[TruckFilter] = typer.Argument(None, help="Filter: all | active | inactive"),
) -> None:
    """List trucks. Optionally filter by active or inactive status."""
    effective_filter = filter if filter is not None else TruckFilter.ALL
    with get_session() as session:
        service = TruckService(TruckRepository(session))
        trucks = service.list_trucks(effective_filter)
    _print_trucks(trucks)


@truck_app.command("get")
def get_truck(id: str = typer.Argument(..., help="Truck ID")) -> None:
    """Show details of a specific truck."""
    with get_session() as session:
        service = TruckService(TruckRepository(session))
        try:
            truck = service.get_truck(id)
        except ValueError as e:
            typer.echo(str(e), err=True)
            raise typer.Exit(1)

    typer.echo(f"ID:    {truck.id}")
    typer.echo(f"Plate: {truck.plate_number}")
    typer.echo(f"Model: {truck.model or '-'}")
