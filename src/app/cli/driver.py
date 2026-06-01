import typer

from app.core.driver.services.driver_service import DriverService
from app.infrastructure.db.repositories.driver_repository import DriverRepository
from app.infrastructure.db.session import get_session

driver_app = typer.Typer(name="driver", help="View drivers")

_ID_COL = 10
_NAME_COL = 24
_PHONE_COL = 16


def _fmt_row(id: str, name: str, phone: str) -> str:
    return f"{id:<{_ID_COL}}  {name:<{_NAME_COL}}  {phone:<{_PHONE_COL}}"


@driver_app.command("list")
def list_drivers() -> None:
    """List all drivers."""
    with get_session() as session:
        service = DriverService(DriverRepository(session))
        drivers = service.list_drivers()

    if not drivers:
        typer.echo("No drivers found.")
        return
    typer.echo(_fmt_row("ID", "NAME", "PHONE"))
    typer.echo("-" * (_ID_COL + _NAME_COL + _PHONE_COL + 4))
    for d in drivers:
        typer.echo(_fmt_row(d.id[:8], d.name, d.phone or "-"))


@driver_app.command("get")
def get_driver(
    id: str = typer.Argument(..., help="Driver ID"),
) -> None:
    """Show details of a specific driver."""
    with get_session() as session:
        service = DriverService(DriverRepository(session))
        try:
            driver = service.get_driver(id)
        except ValueError as e:
            typer.echo(str(e), err=True)
            raise typer.Exit(1)

    typer.echo(f"ID:    {driver.id}")
    typer.echo(f"Name:  {driver.name}")
    typer.echo(f"Phone: {driver.phone or '-'}")
