from dataclasses import dataclass


@dataclass(frozen=True)
class Driver:
    id: str
    name: str
    phone: str | None = None
