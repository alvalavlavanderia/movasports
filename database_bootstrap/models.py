from __future__ import annotations

from dataclasses import asdict, dataclass


class BootstrapError(RuntimeError):
    def __init__(self, message: str, *, code: str = "bootstrap_error"):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class BootstrapStatus:
    ok: bool
    state: str
    environment: str
    driver: str
    schema_version: int | None
    store: str
    app_state: str
    admin: str
    action: str
    errors: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["errors"] = list(self.errors)
        return payload


@dataclass(frozen=True)
class BootstrapResult:
    ok: bool
    status: str
    environment: str
    driver: str
    schema_version: int
    store_created: bool
    app_state_created: bool
    admin_created: bool
    already_complete: bool
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["warnings"] = list(self.warnings)
        return payload
