ui:
    uv run trucklogistics-ui

docker-up:
    docker compose up -d

docker-down:
    docker compose down

test:
    uv run pytest

lint:
    uv run ruff check .

format:
    uv run ruff format .

typecheck:
    uv run mypy src/app