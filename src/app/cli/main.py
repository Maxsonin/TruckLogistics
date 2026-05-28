from dotenv import load_dotenv

load_dotenv()

import typer

app = typer.Typer()


@app.command()
def hello(name: str) -> None:
    print(f"Hello {name}")


@app.command()
def add(a: int, b: int) -> None:
    print(a + b)


@app.command()
def version() -> None:
    print("TruckLogistics v1.0.0")