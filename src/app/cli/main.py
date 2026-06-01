from dotenv import load_dotenv

load_dotenv()

import typer

from app.cli.assignment import assignment_app
from app.cli.driver import driver_app
from app.cli.truck import truck_app

app = typer.Typer()
app.add_typer(truck_app)
app.add_typer(driver_app)
app.add_typer(assignment_app)
