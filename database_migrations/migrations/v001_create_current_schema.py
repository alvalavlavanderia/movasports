from __future__ import annotations

from ..models import Migration
from ..schema import CURRENT_SCHEMA_STATEMENTS


MIGRATION_001 = Migration(
    version=1,
    description="Create current schema",
    sqlite_statements=CURRENT_SCHEMA_STATEMENTS,
    postgresql_statements=CURRENT_SCHEMA_STATEMENTS,
    code_id="mova-sports-schema-baseline-v1",
)
