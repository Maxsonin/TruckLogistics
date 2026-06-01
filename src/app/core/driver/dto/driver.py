from dataclasses import dataclass


@dataclass(frozen=True)
class CreateDriverDTO:
    name: str
    phone: str | None = None


@dataclass(frozen=True)
class UpdateDriverDTO:
    name: str
    phone: str | None = None
