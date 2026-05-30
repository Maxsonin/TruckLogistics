from dotenv import load_dotenv

load_dotenv()

import typer

from app.cli.truck import truck_app

app = typer.Typer()
app.add_typer(truck_app)
