from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Iterable


def normalize_checksum_text(value: str) -> str:
    return str(value).replace("\r\n", "\n").replace("\r", "\n").strip()


@dataclass(frozen=True)
class Migration:
    version: int
    description: str
    sqlite_statements: tuple[str, ...]
    postgresql_statements: tuple[str, ...]
    code_id: str = ""

    @property
    def checksum(self) -> str:
        payload = {
            "code_id": normalize_checksum_text(self.code_id),
            "description": normalize_checksum_text(self.description),
            "postgresql": [normalize_checksum_text(item) for item in self.postgresql_statements],
            "sqlite": [normalize_checksum_text(item) for item in self.sqlite_statements],
            "version": self.version,
        }
        canonical = json.dumps(
            payload,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()


@dataclass(frozen=True)
class AppliedMigration:
    version: object
    description: object
    applied_at: object
    checksum: object
    execution_time_ms: object


def validate_registry(migrations: Iterable[Migration]) -> tuple[Migration, ...]:
    ordered = tuple(sorted(migrations, key=lambda item: item.version))
    if not ordered:
        raise ValueError("O registry de migrations nao pode estar vazio.")

    versions: set[int] = set()
    for migration in ordered:
        if isinstance(migration.version, bool) or not isinstance(migration.version, int) or migration.version <= 0:
            raise ValueError("Toda migration deve possuir versao inteira positiva.")
        if migration.version in versions:
            raise ValueError(f"Versao duplicada no registry: {migration.version}.")
        if not migration.description.strip():
            raise ValueError(f"Migration {migration.version} sem descricao.")
        if not migration.sqlite_statements or not migration.postgresql_statements:
            raise ValueError(f"Migration {migration.version} sem operacoes para um dos bancos.")
        versions.add(migration.version)

    expected = tuple(range(1, len(ordered) + 1))
    actual = tuple(item.version for item in ordered)
    if actual != expected:
        raise ValueError(f"Registry possui lacuna de versoes: esperado {expected}, encontrado {actual}.")
    return ordered
