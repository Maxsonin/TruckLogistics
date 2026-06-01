# TruckLogistics

A desktop application for managing truck dispatch operations — track trucks, drivers, and route assignments through both a command-line interface and a native GUI.

## Features

- Manage trucks, drivers, and route assignments
- Automatic status computation: assignments transition from `ACTIVE` → `COMPLETED` based on elapsed time, no manual updates needed
- Full CRUD via CLI or GUI, with business-rule enforcement (no double-booking, no deletion of in-use records)
- Light / dark theme with automatic system-theme detection
- PostgreSQL backend with Alembic-managed migrations

---

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- PostgreSQL database

---

## Setup

```bash
# Clone and install dependencies
git clone <repo-url>
cd TruckLogistics
uv sync

# Configure database connection
echo 'DATABASE_URL=postgresql+psycopg://user:password@localhost/trucklogistics' > .env

# Run migrations
uv run alembic upgrade head
```

---

## Running

```bash
# Launch the desktop GUI
uv run trucklogistics-ui

# Use the CLI
uv run trucklogistics --help
```

---

## CLI Reference

### Trucks

```bash
# List all trucks (default: all)
uv run trucklogistics truck list
uv run trucklogistics truck list active      # Only trucks with an active assignment
uv run trucklogistics truck list inactive    # Only trucks without an active assignment

# Get a specific truck
uv run trucklogistics truck get <id>
```

### Drivers

```bash
# List all drivers
uv run trucklogistics driver list

# Get a specific driver
uv run trucklogistics driver get <id>
```

### Assignments

```bash
# List all assignments (default: all statuses)
uv run trucklogistics assignment list
uv run trucklogistics assignment list ACTIVE
uv run trucklogistics assignment list COMPLETED
uv run trucklogistics assignment list CANCELLED

# Get full details of an assignment
uv run trucklogistics assignment get <id>
```

All output is rendered as tables in the terminal. IDs are shown truncated (first 8 characters) in list views; `get` shows the full UUID.

---

## GUI Overview

Launch with `uv run trucklogistics-ui`. The interface has a left sidebar with three sections:

### Assignments

- Table view: Truck, Driver, Origin → Destination, Started, Duration, ETA, Status
- Status is color-coded: **Active** (green), **Cancelled** (gray), **Completed** (default)
- Click any row to open a detail panel with full information
- Active assignments can be cancelled from the detail panel
- "+ New Assignment" dialog: select truck and driver, enter origin/destination, set start time and estimated duration

### Trucks

- Table view: Plate Number, Model
- Click a row to view full details, with options to **Edit** or **Delete**
- Plate numbers are automatically uppercased and must be at least 3 characters
- Trucks with an active assignment cannot be deleted

### Drivers

- Table view: Name, Phone
- Click a row to view full details, with options to **Edit** or **Delete**
- Drivers with an active assignment cannot be deleted

The toolbar includes a **theme toggle** (sun / moon icon) to switch between light and dark themes at any time.

---

## Business Rules

**Assignments**

- A truck or driver may only have one `ACTIVE` assignment at a time
- Status is computed, not stored:
  - `CANCELLED` — if a cancellation timestamp is recorded
  - `COMPLETED` — if `started_at + estimated_duration_min` is in the past
  - `ACTIVE` — otherwise
- Cancelling an assignment immediately frees the truck and driver for new assignments
- Completed assignments cannot be cancelled

**Trucks**

- Plate numbers must be unique
- Cannot delete a truck that has an active assignment

**Drivers**

- Name is required
- Cannot delete a driver that has an active assignment

---

## Architecture

```
src/app/
  core/
    domain/          # Immutable domain models (@dataclass frozen=True)
    <feature>/
      dto/           # Input objects (CreateTruckDTO, etc.)
      services/      # Business logic, injected with repository protocols
  infrastructure/
    db/
      models/        # SQLAlchemy ORM models (*ORM suffix)
      repositories/  # Map between domain objects and ORM rows
      migrations/    # Alembic migrations
      engine.py      # SQLAlchemy engine
      session.py     # get_session() context manager
  cli/
    main.py          # Typer entry point (trucklogistics)
  ui/
    main.py          # GUI entry point (trucklogistics-ui)
    views/           # Page-level widgets (AssignmentsView, TrucksView, DriversView)
    widgets/         # Reusable components (Sidebar, etc.)
    windows/         # QMainWindow subclasses
```

Key design decisions:

- Domain models are immutable — repositories accept and return domain objects, never ORM instances
- ORM models are infrastructure-only and never imported into `core/`
- Assignment status is always derived at read time, never persisted
- All database access goes through the `get_session()` context manager

---

## Development

```bash
# Lint
uv run ruff check .

# Type check
uv run mypy .

# Run tests
uv run pytest

# Run a single test
uv run pytest tests/path/to/test_file.py::test_name

# Generate a new migration after changing ORM models
uv run alembic revision --autogenerate -m "describe the change"
uv run alembic upgrade head
```

---

## Database Schema

| Table         | Key columns                                                                                  |
|---------------|----------------------------------------------------------------------------------------------|
| `trucks`      | `id` (UUID PK), `plate_number` (unique), `model`                                             |
| `drivers`     | `id` (UUID PK), `name`, `phone`                                                              |
| `assignments` | `id` (UUID PK), `truck_id` (FK), `driver_id` (FK), `origin`, `destination`, `started_at`, `estimated_duration_min`, `cancelled_at`, `created_at` |

All timestamps are timezone-aware. Status is not a column — it is computed from `cancelled_at` and `started_at + estimated_duration_min`.
