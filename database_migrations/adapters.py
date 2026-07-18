from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .models import AppliedMigration, Migration
from .schema import CURRENT_INDEXES, CURRENT_TABLES


POSTGRES_ADVISORY_LOCK_KEY = 556_079_114_083_002_501
POSTGRES_LOCK_TIMEOUT = "30s"
POSTGRES_STATEMENT_TIMEOUT = "10min"

SQLITE_HISTORY_DDL = """
CREATE TABLE schema_migrations (
    version INTEGER PRIMARY KEY CHECK (version > 0),
    description TEXT NOT NULL,
    applied_at TEXT NOT NULL,
    checksum TEXT NOT NULL,
    execution_time_ms INTEGER NOT NULL CHECK (execution_time_ms >= 0)
)
""".strip()

POSTGRES_HISTORY_DDL = """
CREATE TABLE schema_migrations (
    version INTEGER PRIMARY KEY CHECK (version > 0),
    description TEXT NOT NULL,
    applied_at TIMESTAMPTZ NOT NULL,
    checksum TEXT NOT NULL,
    execution_time_ms BIGINT NOT NULL CHECK (execution_time_ms >= 0)
)
""".strip()


@dataclass(frozen=True)
class SchemaValidation:
    compatible: bool
    errors: tuple[str, ...] = ()


def _compact_sql(value: object) -> str:
    return re.sub(r"\s+", "", str(value or "")).lower().replace('"', "")


def _normalize_default(value: object) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    while normalized.startswith("(") and normalized.endswith(")"):
        normalized = normalized[1:-1].strip()
    normalized = re.sub(r"::[a-zA-Z0-9_ ]+$", "", normalized)
    return normalized


class SQLiteAdapter:
    driver = "sqlite"

    def __init__(self, connection: sqlite3.Connection, path: str, *, readonly: bool = False):
        self.connection = connection
        self.path = path
        self.readonly = readonly
        self.closed = False
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.execute("PRAGMA busy_timeout = 5000")

    def begin_write(self) -> None:
        if self.readonly:
            raise RuntimeError("Conexao SQLite somente leitura.")
        self.connection.execute("BEGIN IMMEDIATE")

    def acquire_migration_lock(self) -> None:
        # BEGIN IMMEDIATE is the SQLite write lock for the migration transaction.
        return None

    def commit(self) -> None:
        self.connection.commit()

    def rollback(self) -> None:
        self.connection.rollback()

    def close(self) -> None:
        if not self.closed:
            self.connection.close()
            self.closed = True

    def table_names(self) -> set[str]:
        rows = self.connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        return {str(row["name"]) for row in rows}

    def history_exists(self) -> bool:
        return "schema_migrations" in self.table_names()

    def create_history_table(self) -> None:
        self.connection.execute(SQLITE_HISTORY_DDL)

    def load_history(self) -> list[AppliedMigration]:
        if not self.history_exists():
            return []
        rows = self.connection.execute(
            """
            SELECT version, description, applied_at, checksum, execution_time_ms
            FROM schema_migrations
            ORDER BY version
            """
        ).fetchall()
        return [AppliedMigration(**dict(row)) for row in rows]

    def apply_migration(self, migration: Migration) -> None:
        for statement in migration.sqlite_statements:
            self.connection.execute(statement)

    def insert_history(self, migration: Migration, applied_at: str, execution_time_ms: int) -> None:
        self.connection.execute(
            """
            INSERT INTO schema_migrations (
                version, description, applied_at, checksum, execution_time_ms
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                migration.version,
                migration.description,
                applied_at,
                migration.checksum,
                execution_time_ms,
            ),
        )

    def validate_current_schema(self) -> SchemaValidation:
        errors: list[str] = []
        expected_tables = {table.name for table in CURRENT_TABLES}
        actual_tables = self.table_names() - {"schema_migrations"}
        if actual_tables != expected_tables:
            missing = sorted(expected_tables - actual_tables)
            unexpected = sorted(actual_tables - expected_tables)
            if missing:
                errors.append(f"Tabelas ausentes: {', '.join(missing)}")
            if unexpected:
                errors.append(f"Tabelas inesperadas: {', '.join(unexpected)}")

        for table in CURRENT_TABLES:
            if table.name not in actual_tables:
                continue
            column_rows = self.connection.execute(f'PRAGMA table_info("{table.name}")').fetchall()
            actual_columns = {str(row["name"]): row for row in column_rows}
            expected_names = {column.name for column in table.columns}
            if set(actual_columns) != expected_names:
                errors.append(f"Colunas divergentes em {table.name}")
                continue
            for column in table.columns:
                row = actual_columns[column.name]
                if str(row["type"]).upper() != column.sql_type.upper():
                    errors.append(f"Tipo divergente em {table.name}.{column.name}")
                if bool(row["notnull"]) != column.not_null:
                    errors.append(f"Nullability divergente em {table.name}.{column.name}")
                if bool(row["pk"]) != column.primary_key:
                    errors.append(f"Primary key divergente em {table.name}.{column.name}")
                if _normalize_default(row["dflt_value"]) != _normalize_default(column.default):
                    errors.append(f"Default divergente em {table.name}.{column.name}")

            fk_rows = self.connection.execute(f'PRAGMA foreign_key_list("{table.name}")').fetchall()
            actual_fks = {
                (str(row["from"]), str(row["table"]), str(row["to"]), str(row["on_delete"]).upper())
                for row in fk_rows
            }
            expected_fks = {
                (fk.column, fk.target_table, fk.target_column, fk.on_delete.upper())
                for fk in table.foreign_keys
            }
            if actual_fks != expected_fks:
                errors.append(f"Foreign keys divergentes em {table.name}")

            table_row = self.connection.execute(
                "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?",
                (table.name,),
            ).fetchone()
            table_sql = _compact_sql(table_row["sql"] if table_row else "")
            for check in table.checks:
                if f"check({_compact_sql(check)})" not in table_sql:
                    errors.append(f"Check constraint ausente em {table.name}")

        expected_indexes = {index.name: index for index in CURRENT_INDEXES}
        actual_custom_indexes: set[str] = set()
        for table in CURRENT_TABLES:
            if table.name not in actual_tables:
                continue
            index_rows = self.connection.execute(f'PRAGMA index_list("{table.name}")').fetchall()
            for row in index_rows:
                index_name = str(row["name"])
                if index_name.startswith("sqlite_autoindex_"):
                    continue
                actual_custom_indexes.add(index_name)
                expected = expected_indexes.get(index_name)
                if expected is None:
                    continue
                column_rows = self.connection.execute(f'PRAGMA index_info("{index_name}")').fetchall()
                columns = tuple(str(item["name"]) for item in column_rows)
                if columns != expected.columns or bool(row["unique"]) != expected.unique:
                    errors.append(f"Indice divergente: {index_name}")
                sql_row = self.connection.execute(
                    "SELECT sql FROM sqlite_master WHERE type = 'index' AND name = ?",
                    (index_name,),
                ).fetchone()
                sql = str(sql_row["sql"] or "") if sql_row else ""
                actual_predicate = sql.split(" WHERE ", 1)[1] if " WHERE " in sql.upper() else ""
                if _compact_sql(actual_predicate) != _compact_sql(expected.predicate):
                    errors.append(f"Predicado divergente: {index_name}")

        expected_names = set(expected_indexes)
        if actual_custom_indexes != expected_names:
            missing = sorted(expected_names - actual_custom_indexes)
            unexpected = sorted(actual_custom_indexes - expected_names)
            if missing:
                errors.append(f"Indices ausentes: {', '.join(missing)}")
            if unexpected:
                errors.append(f"Indices inesperados: {', '.join(unexpected)}")
        return SchemaValidation(not errors, tuple(errors))

    def business_row_count(self) -> int:
        total = 0
        for table in CURRENT_TABLES:
            total += int(self.connection.execute(f'SELECT COUNT(*) AS total FROM "{table.name}"').fetchone()["total"])
        return total


class PostgreSQLAdapter:
    driver = "postgresql"

    def __init__(self, connection, *, readonly: bool = False):
        self.connection = connection
        self.readonly = readonly
        self.closed = False
        self.connection.autocommit = False
        if readonly and hasattr(self.connection, "set_session"):
            self.connection.set_session(readonly=True, autocommit=False)

    def _execute(self, sql: str, params=()):
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, params)
            return cursor
        except Exception:
            cursor.close()
            raise

    @staticmethod
    def _rows(cursor) -> list[dict]:
        keys = [item[0] for item in cursor.description] if cursor.description else []
        return [dict(zip(keys, row)) for row in cursor.fetchall()]

    def begin_write(self) -> None:
        if self.readonly:
            raise RuntimeError("Conexao PostgreSQL somente leitura.")
        cursor = self._execute("SET LOCAL lock_timeout = %s", (POSTGRES_LOCK_TIMEOUT,))
        cursor.close()
        cursor = self._execute("SET LOCAL statement_timeout = %s", (POSTGRES_STATEMENT_TIMEOUT,))
        cursor.close()

    def acquire_migration_lock(self) -> None:
        cursor = self._execute("SELECT pg_advisory_xact_lock(%s)", (POSTGRES_ADVISORY_LOCK_KEY,))
        cursor.close()

    def commit(self) -> None:
        self.connection.commit()

    def rollback(self) -> None:
        self.connection.rollback()

    def close(self) -> None:
        if not self.closed:
            self.connection.close()
            self.closed = True

    def table_names(self) -> set[str]:
        cursor = self._execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        )
        try:
            return {str(row["table_name"]) for row in self._rows(cursor)}
        finally:
            cursor.close()

    def history_exists(self) -> bool:
        return "schema_migrations" in self.table_names()

    def create_history_table(self) -> None:
        cursor = self._execute(POSTGRES_HISTORY_DDL)
        cursor.close()

    def load_history(self) -> list[AppliedMigration]:
        if not self.history_exists():
            return []
        cursor = self._execute(
            """
            SELECT version, description, applied_at, checksum, execution_time_ms
            FROM schema_migrations
            ORDER BY version
            """
        )
        try:
            return [AppliedMigration(**row) for row in self._rows(cursor)]
        finally:
            cursor.close()

    def apply_migration(self, migration: Migration) -> None:
        for statement in migration.postgresql_statements:
            cursor = self._execute(statement)
            cursor.close()

    def insert_history(self, migration: Migration, applied_at: str, execution_time_ms: int) -> None:
        cursor = self._execute(
            """
            INSERT INTO schema_migrations (
                version, description, applied_at, checksum, execution_time_ms
            ) VALUES (%s, %s, %s, %s, %s)
            """,
            (
                migration.version,
                migration.description,
                applied_at,
                migration.checksum,
                execution_time_ms,
            ),
        )
        cursor.close()

    def validate_current_schema(self) -> SchemaValidation:
        errors: list[str] = []
        expected_tables = {table.name for table in CURRENT_TABLES}
        actual_tables = self.table_names() - {"schema_migrations"}
        if actual_tables != expected_tables:
            missing = sorted(expected_tables - actual_tables)
            unexpected = sorted(actual_tables - expected_tables)
            if missing:
                errors.append(f"Tabelas ausentes: {', '.join(missing)}")
            if unexpected:
                errors.append(f"Tabelas inesperadas: {', '.join(unexpected)}")
            return SchemaValidation(False, tuple(errors))

        cursor = self._execute(
            """
            SELECT table_name, column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = 'public'
            """
        )
        try:
            column_rows = self._rows(cursor)
        finally:
            cursor.close()
        by_table: dict[str, dict[str, dict]] = {}
        for row in column_rows:
            by_table.setdefault(str(row["table_name"]), {})[str(row["column_name"])] = row

        cursor = self._execute(
            """
            SELECT tc.table_name, kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema = kcu.table_schema
            WHERE tc.table_schema = 'public' AND tc.constraint_type = 'PRIMARY KEY'
            """
        )
        try:
            primary_keys = {(str(row["table_name"]), str(row["column_name"])) for row in self._rows(cursor)}
        finally:
            cursor.close()

        for table in CURRENT_TABLES:
            actual_columns = by_table.get(table.name, {})
            if set(actual_columns) != {column.name for column in table.columns}:
                errors.append(f"Colunas divergentes em {table.name}")
                continue
            for column in table.columns:
                row = actual_columns[column.name]
                expected_type = column.sql_type.lower()
                if str(row["data_type"]).lower() != expected_type:
                    errors.append(f"Tipo divergente em {table.name}.{column.name}")
                actual_not_null = str(row["is_nullable"]).upper() == "NO"
                if actual_not_null != (column.not_null or column.primary_key):
                    errors.append(f"Nullability divergente em {table.name}.{column.name}")
                if ((table.name, column.name) in primary_keys) != column.primary_key:
                    errors.append(f"Primary key divergente em {table.name}.{column.name}")
                if _normalize_default(row["column_default"]) != _normalize_default(column.default):
                    errors.append(f"Default divergente em {table.name}.{column.name}")

        cursor = self._execute(
            """
            SELECT tc.table_name, kcu.column_name, ccu.table_name AS target_table,
                   ccu.column_name AS target_column, rc.delete_rule
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage ccu
              ON tc.constraint_name = ccu.constraint_name AND tc.table_schema = ccu.table_schema
            JOIN information_schema.referential_constraints rc
              ON tc.constraint_name = rc.constraint_name AND tc.table_schema = rc.constraint_schema
            WHERE tc.table_schema = 'public' AND tc.constraint_type = 'FOREIGN KEY'
            """
        )
        try:
            fk_rows = self._rows(cursor)
        finally:
            cursor.close()
        actual_fks = {
            (
                str(row["table_name"]), str(row["column_name"]), str(row["target_table"]),
                str(row["target_column"]), str(row["delete_rule"]).upper(),
            )
            for row in fk_rows
        }
        expected_fks = {
            (table.name, fk.column, fk.target_table, fk.target_column, fk.on_delete.upper())
            for table in CURRENT_TABLES for fk in table.foreign_keys
        }
        if actual_fks != expected_fks:
            errors.append("Foreign keys divergentes")

        cursor = self._execute(
            """
            SELECT c.relname AS table_name, pg_get_constraintdef(pc.oid) AS definition
            FROM pg_constraint pc
            JOIN pg_class c ON c.oid = pc.conrelid
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = 'public' AND pc.contype = 'c'
            """
        )
        try:
            check_rows = self._rows(cursor)
        finally:
            cursor.close()
        checks_by_table: dict[str, set[str]] = {}
        for row in check_rows:
            checks_by_table.setdefault(str(row["table_name"]), set()).add(_compact_sql(row["definition"]))
        for table in CURRENT_TABLES:
            actual_checks = checks_by_table.get(table.name, set())
            for check in table.checks:
                expected_check = f"check(({_compact_sql(check)}))"
                alternate_check = f"check({_compact_sql(check)})"
                if expected_check not in actual_checks and alternate_check not in actual_checks:
                    errors.append(f"Check constraint ausente em {table.name}")

        cursor = self._execute(
            "SELECT tablename, indexname, indexdef FROM pg_indexes WHERE schemaname = 'public'"
        )
        try:
            index_rows = {str(row["indexname"]): row for row in self._rows(cursor)}
        finally:
            cursor.close()
        actual_custom = {name for name in index_rows if not name.endswith("_pkey")}
        expected_names = {index.name for index in CURRENT_INDEXES}
        if actual_custom != expected_names:
            errors.append("Conjunto de indices divergente")
        for index in CURRENT_INDEXES:
            row = index_rows.get(index.name)
            if not row:
                continue
            definition = _compact_sql(row["indexdef"])
            expected_columns = f"({','.join(column.lower() for column in index.columns)})"
            if expected_columns not in definition:
                errors.append(f"Indice divergente: {index.name}")
            if ("createuniqueindex" in definition) != index.unique:
                errors.append(f"Unicidade divergente: {index.name}")
            if index.predicate and _compact_sql(index.predicate) not in definition:
                errors.append(f"Predicado divergente: {index.name}")
        return SchemaValidation(not errors, tuple(errors))

    def business_row_count(self) -> int:
        total = 0
        for table in CURRENT_TABLES:
            cursor = self._execute(f'SELECT COUNT(*) AS total FROM "{table.name}"')
            try:
                rows = self._rows(cursor)
                total += int(rows[0]["total"])
            finally:
                cursor.close()
        return total


def open_sqlite_adapter(path: str, *, readonly: bool, create: bool = False) -> SQLiteAdapter:
    resolved = Path(path).resolve()
    if readonly or not create:
        mode = "ro" if readonly else "rw"
        connection = sqlite3.connect(
            f"{resolved.as_uri()}?mode={mode}",
            uri=True,
            isolation_level=None,
        )
    else:
        if not resolved.parent.exists():
            raise FileNotFoundError(f"Diretorio do banco SQLite nao existe: {resolved.parent}")
        connection = sqlite3.connect(resolved, isolation_level=None)
    return SQLiteAdapter(connection, str(resolved), readonly=readonly)


def open_postgresql_adapter(database_url: str, *, readonly: bool) -> PostgreSQLAdapter:
    import psycopg2

    connection = psycopg2.connect(database_url)
    return PostgreSQLAdapter(connection, readonly=readonly)


AdapterFactory = Callable[..., SQLiteAdapter | PostgreSQLAdapter]
