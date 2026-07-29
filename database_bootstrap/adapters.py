from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Callable

from database_migrations.adapters import PostgreSQLAdapter, SQLiteAdapter
from database_migrations.migrations.v003_supplier_auxiliary_catalogs import (
    EXPENSE_CATEGORY_NAMES,
    _normalized_name,
    _slug,
)
from database_migrations.runner import DatabaseTarget


BOOTSTRAP_POSTGRES_ADVISORY_LOCK_KEY = 556079114083002502


class BootstrapSQLiteAdapter(SQLiteAdapter):
    def acquire_bootstrap_lock(self) -> None:
        # BEGIN IMMEDIATE, called first, owns the SQLite write lock.
        return None

    def fetch_stores(self) -> list[dict]:
        return [dict(row) for row in self.connection.execute(
            "SELECT id, name, created_at FROM stores ORDER BY id"
        ).fetchall()]

    def fetch_app_states(self) -> list[dict]:
        return [dict(row) for row in self.connection.execute(
            "SELECT id, data, updated_at FROM app_state ORDER BY id"
        ).fetchall()]

    def fetch_users(self) -> list[dict]:
        return [dict(row) for row in self.connection.execute(
            """
            SELECT id, store_id, name, login, password_hash, role, active, updated_at
            FROM users
            ORDER BY id
            """
        ).fetchall()]

    def insert_store(self, store_id: str, name: str, created_at: str) -> None:
        self.connection.execute(
            "INSERT INTO stores (id, name, created_at) VALUES (?, ?, ?)",
            (store_id, name, created_at),
        )

    def insert_app_state(self, data: str, updated_at: str) -> None:
        self.connection.execute(
            "INSERT INTO app_state (id, data, updated_at) VALUES (1, ?, ?)",
            (data, updated_at),
        )

    def insert_default_customer(self, store_id: str, created_at: str) -> None:
        self.connection.execute(
            """
            INSERT INTO customers (
                id, store_id, code, name, cpf, rg, birth, whatsapp, email,
                address, city, district, zip, credit_limit, status, updated_at,
                address_number, state, notes, is_default, created_at
            )
            VALUES (?, ?, 'PADRAO', 'Cliente padrao', '', '', '', '', '', '',
                    '', '', '', 0, 'active', ?, '', '', '', 1, ?)
            """,
            (f"{store_id}:customer:default", store_id, created_at, created_at),
        )

    def insert_default_expense_categories(self, store_id: str, created_at: str) -> None:
        self.connection.executemany(
            """
            INSERT INTO expense_categories (
                id, store_id, name, normalized_name, status, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, 'active', ?, ?)
            """,
            [
                (
                    f"{store_id}:expense-category:{_slug(name)}",
                    store_id,
                    name,
                    _normalized_name(name),
                    created_at,
                    created_at,
                )
                for name in EXPENSE_CATEGORY_NAMES
            ],
        )

    def insert_admin(
        self,
        user_id: str,
        store_id: str,
        name: str,
        login: str,
        password_hash: str,
        updated_at: str,
    ) -> None:
        self.connection.execute(
            """
            INSERT INTO users (id, store_id, name, login, password_hash, role, active, updated_at)
            VALUES (?, ?, ?, ?, ?, 'admin', 1, ?)
            """,
            (user_id, store_id, name, login, password_hash, updated_at),
        )


class BootstrapPostgreSQLAdapter(PostgreSQLAdapter):
    def acquire_bootstrap_lock(self) -> None:
        cursor = self._execute(
            "SELECT pg_advisory_xact_lock(%s)",
            (BOOTSTRAP_POSTGRES_ADVISORY_LOCK_KEY,),
        )
        cursor.close()

    def _fetch(self, sql: str) -> list[dict]:
        cursor = self._execute(sql)
        try:
            return self._rows(cursor)
        finally:
            cursor.close()

    def fetch_stores(self) -> list[dict]:
        return self._fetch("SELECT id, name, created_at FROM stores ORDER BY id")

    def fetch_app_states(self) -> list[dict]:
        return self._fetch("SELECT id, data, updated_at FROM app_state ORDER BY id")

    def fetch_users(self) -> list[dict]:
        return self._fetch(
            """
            SELECT id, store_id, name, login, password_hash, role, active, updated_at
            FROM users
            ORDER BY id
            """
        )

    def insert_store(self, store_id: str, name: str, created_at: str) -> None:
        cursor = self._execute(
            "INSERT INTO stores (id, name, created_at) VALUES (%s, %s, %s)",
            (store_id, name, created_at),
        )
        cursor.close()

    def insert_app_state(self, data: str, updated_at: str) -> None:
        cursor = self._execute(
            "INSERT INTO app_state (id, data, updated_at) VALUES (1, %s, %s)",
            (data, updated_at),
        )
        cursor.close()

    def insert_default_customer(self, store_id: str, created_at: str) -> None:
        cursor = self._execute(
            """
            INSERT INTO customers (
                id, store_id, code, name, cpf, rg, birth, whatsapp, email,
                address, city, district, zip, credit_limit, status, updated_at,
                address_number, state, notes, is_default, created_at
            )
            VALUES (%s, %s, 'PADRAO', 'Cliente padrao', '', '', '', '', '', '',
                    '', '', '', 0, 'active', %s, '', '', '', 1, %s)
            """,
            (f"{store_id}:customer:default", store_id, created_at, created_at),
        )
        cursor.close()

    def insert_default_expense_categories(self, store_id: str, created_at: str) -> None:
        for name in EXPENSE_CATEGORY_NAMES:
            cursor = self._execute(
                """
                INSERT INTO expense_categories (
                    id, store_id, name, normalized_name, status, created_at, updated_at
                )
                VALUES (%s, %s, %s, %s, 'active', %s, %s)
                """,
                (
                    f"{store_id}:expense-category:{_slug(name)}",
                    store_id,
                    name,
                    _normalized_name(name),
                    created_at,
                    created_at,
                ),
            )
            cursor.close()

    def insert_admin(
        self,
        user_id: str,
        store_id: str,
        name: str,
        login: str,
        password_hash: str,
        updated_at: str,
    ) -> None:
        cursor = self._execute(
            """
            INSERT INTO users (id, store_id, name, login, password_hash, role, active, updated_at)
            VALUES (%s, %s, %s, %s, %s, 'admin', 1, %s)
            """,
            (user_id, store_id, name, login, password_hash, updated_at),
        )
        cursor.close()


def open_sqlite_bootstrap_adapter(path: str, *, readonly: bool) -> BootstrapSQLiteAdapter:
    resolved = Path(path).resolve()
    mode = "ro" if readonly else "rw"
    connection = sqlite3.connect(
        f"{resolved.as_uri()}?mode={mode}",
        uri=True,
        isolation_level=None,
    )
    return BootstrapSQLiteAdapter(connection, str(resolved), readonly=readonly)


def open_postgresql_bootstrap_adapter(
    database_url: str,
    *,
    readonly: bool,
) -> BootstrapPostgreSQLAdapter:
    import psycopg2

    connection = psycopg2.connect(database_url)
    return BootstrapPostgreSQLAdapter(connection, readonly=readonly)


def open_bootstrap_adapter(target: DatabaseTarget, *, readonly: bool):
    if target.driver == "postgresql":
        return open_postgresql_bootstrap_adapter(target.database_url, readonly=readonly)
    return open_sqlite_bootstrap_adapter(target.sqlite_path, readonly=readonly)


AdapterFactory = Callable[..., BootstrapSQLiteAdapter | BootstrapPostgreSQLAdapter]
