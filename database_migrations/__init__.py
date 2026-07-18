"""Versioned database migrations for Mova Sports.

Importing this package only builds immutable metadata in memory. It never
opens a database connection or applies a migration.
"""

from .registry import MIGRATIONS, get_registry
from .runner import (
    MigrationError,
    baseline_database,
    get_migration_status,
    run_database_migrations,
)

__all__ = [
    "MIGRATIONS",
    "MigrationError",
    "baseline_database",
    "get_migration_status",
    "get_registry",
    "run_database_migrations",
]
