# Truck Assignment Management System

## Purpose

A minimal logistics simulation system for managing truck assignments. The system is **time-driven, not state-driven**. An assignment does not require manual progression between states. Instead, its state is derived from time.

The system supports:

- creating assignments
- assigning driver + truck
- simulating delivery progress over time(time based change)
- preventing conflicting assignments

## Domain Model

### Truck

```py
@dataclass
class Truck:
    id: str
    plate_number: str
    model: Optional[str] = None
```

TruckStatus = 'IDLE' | 'BUSY' - NOT USED IN ACTUAL DB

---

### Driver

```py
@dataclass
class Driver:
    id: str
    name: str
    phone: Optional[str] = None
```

DriverStatus = 'AVAILABLE' | 'ON_DELIVERY' - NOT USED IN ACTUAL DB

---

### Assignment

```py
@dataclass
class Assignment:
    id: str

    truck_id: str
    driver_id: str

    origin: str
    destination: str

    started_at: datetime
    estimated_duration_min: int

    cancelled_at: Optional[datetime] = None

    created_at: datetime = None
```

---

## Assignment State

Assignment status is computed dynamically.

```py
class AssignmentStatus(str, Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
```

## Business Rules

- A truck cannot have more than one ACTIVE assignment
- A driver cannot have more than one ACTIVE assignment

- Assignments can be cancelled at any time
- Cancelled assignments remain in history
- Cancelled assignments do not block reuse of truck/driver

- Only 'CANCELLED' status can be manually changed

- Assignment automatically becomes COMPLETED after duration passes

## Lifecycle Model

```text
CREATE ASSIGNMENT
      ↓
ACTIVE (time-based)
      ↓
COMPLETED (automatic)
```

Optional branch:

```text
ACTIVE → CANCELLED
```

## Conflict Detection Rules

Before creating assignment:

```text
Reject if:
- truck has ACTIVE assignment
- driver has ACTIVE assignment
```

## CLI Scope

### Commands

```bash
assignment list
assignment cancel <id>

truck list
driver list
```

## UI Scope

### Page 1 — Dashboard (List of Assignments)

Main table:

| ID | Driver | Truck | From | To | Status | ETA |

- ETA derived from startedAt + duration(random)
- Clicking on any assignment will then open another view where full details will be displayed

### Page 2 — List of Trucks

### Page 3 — List of Drivers
