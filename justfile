ui:
    uv run trucklogistics-ui

test:
    uv run pytest

lint:
    uv run ruff check .

format:
    uv run ruff format .

typecheck:
    uv run mypy src