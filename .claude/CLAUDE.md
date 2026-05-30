# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

This project uses [uv](https://docs.astral.sh/uv/) for dependency and environment management.

```bash
# Install dependencies
uv sync

# Run CLI
uv run trucklogistics <command>

# Run GUI
uv run trucklogistics-ui

# Lint
uv run ruff check .

# Type check
uv run mypy .

# Run tests
uv run pytest

# Run a single test
uv run pytest tests/path/to/test_file.py::test_name

# Run Alembic migrations
uv run alembic upgrade head

# Create a new migration (after adding/changing ORM models)
uv run alembic revision --autogenerate -m "description"
```

Requires `DATABASE_URL` set in a `.env` file at the project root (loaded automatically via `python-dotenv`).

## Architecture

The project is a **time-driven logistics simulation** — assignment status (ACTIVE / COMPLETED / CANCELLED) is computed dynamically from timestamps, not stored as a field.

### Layer structure

```
src/app/
  core/
    domain/          # Pure Python dataclasses (frozen=True) — no framework dependencies
    <feature>/
      dto/           # Input/command objects (CreateTruckDTO, etc.)
      services/      # Business logic; receives repo via constructor injection
  infrastructure/
    db/
      models/        # SQLAlchemy ORM classes (*ORM suffix, e.g. TruckORM)
      repositories/  # Session-scoped; map between domain objects and ORM rows
      migrations/    # Alembic migrations (env.py imports all ORM models for autogenerate)
      engine.py      # SQLAlchemy engine (reads DATABASE_URL from env)
      session.py     # get_session() context manager — commits on success, rolls back on error
  cli/
    main.py          # Typer app (entry point: trucklogistics)
  ui/
    main.py          # Entry point (trucklogistics-ui); calls run_app() after load_dotenv()
    app.py           # QApplication setup
    windows/         # QMainWindow subclasses
    widgets/         # Reusable QWidget components (Sidebar, etc.)
    views/           # Page-level widgets (DashboardView, etc.)
```

### Key design rules

- **Domain objects are immutable** (`@dataclass(frozen=True)`). Repositories accept domain objects and return new domain objects — never ORM instances.
- **ORM models are infrastructure-only.** Never import `*ORM` classes into `core/`.
- **Status is never persisted.** `TruckStatus` / `DriverStatus` / `AssignmentStatus` are derived at read time from timestamps and the `is_cancelled` flag.
- **Session management**: always use the `get_session()` context manager from `session.py`; do not create sessions manually.
- **When adding a new ORM model**, import it in `migrations/env.py` alongside the existing models so Alembic autogenerate picks it up.

### Business rules

- A truck or driver cannot be assigned while they have an ACTIVE assignment.
- Cancelling an assignment frees the truck and driver immediately.
- Only the CANCELLED state can be manually set; COMPLETED is automatic once `started_at + estimated_duration_min` has elapsed.

## Code style

- PEP 8, full type annotations on all function signatures, `ruff` for linting.
- Prefer immutable data structures (`@dataclass(frozen=True)`, `NamedTuple`).
