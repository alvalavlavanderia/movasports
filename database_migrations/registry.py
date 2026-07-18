from __future__ import annotations

from collections.abc import Iterable

from .migrations.v001_create_current_schema import MIGRATION_001
from .models import Migration, validate_registry


MIGRATIONS = validate_registry((MIGRATION_001,))


def get_registry(migrations: Iterable[Migration] | None = None) -> tuple[Migration, ...]:
    return validate_registry(MIGRATIONS if migrations is None else migrations)
