from datetime import timedelta
from typing import Optional

import typer

from app.core.assignment.services.assignment_service import AssignmentService
from app.core.domain.assignment import Assignment, AssignmentStatus
from app.infrastructure.db.repositories.assignment_repository import AssignmentRepository
from app.infrastructure.db.session import get_session

assignment_app = typer.Typer(name="assignment", help="View truck assignments")

_ID_COL = 10
_DRIVER_COL = 10
_TRUCK_COL = 10
_FROM_COL = 14
_TO_COL = 14
_STATUS_COL = 10
_ETA_COL = 20


def _fmt_row(
    id: str,
    driver: str,
    truck: str,
    origin: str,
    destination: str,
    status: str,
    eta: str,
) -> str:
    return (
        f"{id:<{_ID_COL}}  {driver:<{_DRIVER_COL}}  {truck:<{_TRUCK_COL}}  "
        f"{origin:<{_FROM_COL}}  {destination:<{_TO_COL}}  "
        f"{status:<{_STATUS_COL}}  {eta:<{_ETA_COL}}"
    )


def _eta(assignment: Assignment) -> str:
    if assignment.status == AssignmentStatus.COMPLETED:
        return "Done"
    if assignment.status == AssignmentStatus.CANCELLED:
        return "-"
    eta_dt = assignment.started_at + timedelta(minutes=assignment.estimated_duration_min)
    return eta_dt.strftime("%Y-%m-%d %H:%M UTC")


def _print_assignments(assignments: list[Assignment]) -> None:
    if not assignments:
        typer.echo("No assignments found.")
        return
    header = _fmt_row("ID", "DRIVER", "TRUCK", "FROM", "TO", "STATUS", "ETA")
    sep_len = _ID_COL + _DRIVER_COL + _TRUCK_COL + _FROM_COL + _TO_COL + _STATUS_COL + _ETA_COL + 12
    typer.echo(header)
    typer.echo("-" * sep_len)
    for a in assignments:
        typer.echo(
            _fmt_row(
                a.id[:8],
                a.driver_id[:8],
                a.truck_id[:8],
                a.origin[:_FROM_COL],
                a.destination[:_TO_COL],
                a.status.value,
                _eta(a),
            )
        )


@assignment_app.command("list")
def list_assignments(
    status: Optional[AssignmentStatus] = typer.Argument(
        None, help="Filter: ACTIVE | COMPLETED | CANCELLED"
    ),
) -> None:
    """List assignments. Optionally filter by status."""
    with get_session() as session:
        service = AssignmentService(AssignmentRepository(session))
        assignments = service.list_assignments(status)
    _print_assignments(assignments)


@assignment_app.command("get")
def get_assignment(
    id: str = typer.Argument(..., help="Assignment ID"),
) -> None:
    """Show full details of a specific assignment."""
    with get_session() as session:
        service = AssignmentService(AssignmentRepository(session))
        try:
            a = service.get_assignment(id)
        except ValueError as e:
            typer.echo(str(e), err=True)
            raise typer.Exit(1)

    typer.echo(f"ID:          {a.id}")
    typer.echo(f"Truck:       {a.truck_id}")
    typer.echo(f"Driver:      {a.driver_id}")
    typer.echo(f"Origin:      {a.origin}")
    typer.echo(f"Destination: {a.destination}")
    typer.echo(f"Status:      {a.status.value}")
    typer.echo(f"Started:     {a.started_at.isoformat()}")
    typer.echo(f"Duration:    {a.estimated_duration_min} min")
    typer.echo(f"ETA:         {_eta(a)}")
    if a.cancelled_at:
        typer.echo(f"Cancelled:   {a.cancelled_at.isoformat()}")
    if a.created_at:
        typer.echo(f"Created:     {a.created_at.isoformat()}")
