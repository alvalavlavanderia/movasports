from __future__ import annotations

import unittest
from unittest import mock

from database_bootstrap.adapters import (
    BOOTSTRAP_POSTGRES_ADVISORY_LOCK_KEY,
    BootstrapPostgreSQLAdapter,
)
from database_bootstrap.models import BootstrapError
from database_bootstrap.runner import get_bootstrap_status, run_database_bootstrap
from database_migrations.adapters import POSTGRES_ADVISORY_LOCK_KEY, SchemaValidation
from database_migrations.models import AppliedMigration
from database_migrations.registry import MIGRATIONS
from database_migrations.schema import CURRENT_TABLE_NAMES


class FakeBootstrapAdapter:
    driver = "postgresql"

    def __init__(self):
        migration = MIGRATIONS[0]
        self.history = [AppliedMigration(
            version=1,
            description=migration.description,
            applied_at="2026-01-01T00:00:00Z",
            checksum=migration.checksum,
            execution_time_ms=1,
        )]
        self.stores = []
        self.app_states = []
        self.users = []
        self.events = []
        self.closed = False
        self.readonly = False
        self.fail_on = ""

    def table_names(self):
        self.events.append("table_names")
        return set(CURRENT_TABLE_NAMES) | {"schema_migrations"}

    def history_exists(self):
        self.events.append("history_exists")
        return True

    def load_history(self):
        self.events.append("load_history")
        return list(self.history)

    def validate_current_schema(self):
        self.events.append("validate_schema")
        return SchemaValidation(True, ())

    def begin_write(self):
        self.events.append("begin_write")

    def acquire_bootstrap_lock(self):
        self.events.append("bootstrap_lock")

    def commit(self):
        self.events.append("commit")

    def rollback(self):
        self.events.append("rollback")

    def close(self):
        self.events.append("close")
        self.closed = True

    def fetch_stores(self):
        self.events.append("fetch_stores")
        return list(self.stores)

    def fetch_app_states(self):
        self.events.append("fetch_app_states")
        return list(self.app_states)

    def fetch_users(self):
        self.events.append("fetch_users")
        return list(self.users)

    def _fail(self, name):
        if self.fail_on == name:
            raise RuntimeError("synthetic failure")

    def insert_store(self, store_id, name, created_at):
        self.events.append("insert_store")
        self._fail("store")
        self.stores.append({"id": store_id, "name": name, "created_at": created_at})

    def insert_app_state(self, data, updated_at):
        self.events.append("insert_app_state")
        self._fail("app_state")
        self.app_states.append({"id": 1, "data": data, "updated_at": updated_at})

    def insert_admin(self, user_id, store_id, name, login, password_hash, updated_at):
        self.events.append("insert_admin")
        self._fail("admin")
        self.users.append({
            "id": user_id,
            "store_id": store_id,
            "name": name,
            "login": login,
            "password_hash": password_hash,
            "role": "admin",
            "active": True,
            "updated_at": updated_at,
        })


class FakeConnection:
    def __init__(self):
        self.autocommit = True
        self.session = None
        self.commands = []
        self.commits = 0
        self.rollbacks = 0
        self.closed = False

    def set_session(self, **kwargs):
        self.session = kwargs

    def cursor(self):
        connection = self

        class Cursor:
            description = []

            def execute(self, sql, params=()):
                connection.commands.append((" ".join(sql.split()), params))

            def close(self):
                return None

            def fetchall(self):
                return []

        return Cursor()

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        self.closed = True


class BootstrapPostgreSQLTests(unittest.TestCase):
    def setUp(self):
        self.adapter = FakeBootstrapAdapter()
        self.env = {
            "APP_ENV": "development",
            "MOVA_ALLOW_BOOTSTRAP": "true",
            "BOOTSTRAP_PASSWORD": "Strong-123",
        }

    def factory(self, target, *, readonly):
        self.adapter.readonly = readonly
        return self.adapter

    def bootstrap(self):
        return run_database_bootstrap(
            store_name="Matriz",
            admin_name="Administrador",
            admin_login="admin",
            admin_password_env="BOOTSTRAP_PASSWORD",
            confirm_bootstrap=True,
            environ=self.env,
            database_url="postgresql://example.invalid/database",
            adapter_factory=self.factory,
        )

    def test_postgresql_bootstrap_creates_components_in_order(self):
        result = self.bootstrap()
        self.assertTrue(result.ok)
        self.assertLess(self.adapter.events.index("insert_store"), self.adapter.events.index("insert_app_state"))
        self.assertLess(self.adapter.events.index("insert_app_state"), self.adapter.events.index("insert_admin"))

    def test_postgresql_locks_before_writes(self):
        self.bootstrap()
        self.assertLess(self.adapter.events.index("bootstrap_lock"), self.adapter.events.index("insert_store"))

    def test_postgresql_reloads_status_after_lock(self):
        self.bootstrap()
        lock = self.adapter.events.index("bootstrap_lock")
        self.assertIn("load_history", self.adapter.events[lock + 1:])
        self.assertIn("fetch_stores", self.adapter.events[lock + 1:])

    def test_postgresql_commits_on_success(self):
        self.bootstrap()
        self.assertIn("commit", self.adapter.events)
        self.assertNotIn("rollback", self.adapter.events)

    def test_postgresql_rolls_back_on_failure(self):
        self.adapter.fail_on = "admin"
        with self.assertRaises(BootstrapError):
            self.bootstrap()
        self.assertIn("rollback", self.adapter.events)
        self.assertNotIn("commit", self.adapter.events)

    def test_postgresql_closes_on_success(self):
        self.bootstrap()
        self.assertTrue(self.adapter.closed)
        self.assertEqual(self.adapter.events[-1], "close")

    def test_postgresql_closes_on_failure(self):
        self.adapter.fail_on = "app_state"
        with self.assertRaises(BootstrapError):
            self.bootstrap()
        self.assertTrue(self.adapter.closed)

    def test_postgresql_status_is_read_only(self):
        status = get_bootstrap_status(
            environ=self.env,
            database_url="postgresql://example.invalid/database",
            adapter_factory=self.factory,
        )
        self.assertEqual(status.state, "BOOTSTRAP_NOT_STARTED")
        self.assertTrue(self.adapter.readonly)
        self.assertNotIn("begin_write", self.adapter.events)
        self.assertNotIn("insert_store", self.adapter.events)

    def test_postgresql_status_closes_connection(self):
        get_bootstrap_status(
            environ=self.env,
            database_url="postgresql://example.invalid/database",
            adapter_factory=self.factory,
        )
        self.assertTrue(self.adapter.closed)

    def test_bootstrap_lock_key_differs_from_migrations(self):
        self.assertNotEqual(BOOTSTRAP_POSTGRES_ADVISORY_LOCK_KEY, POSTGRES_ADVISORY_LOCK_KEY)

    def test_real_adapter_sets_autocommit_false(self):
        connection = FakeConnection()
        adapter = BootstrapPostgreSQLAdapter(connection)
        self.assertFalse(connection.autocommit)
        adapter.close()

    def test_real_readonly_adapter_sets_readonly_session(self):
        connection = FakeConnection()
        adapter = BootstrapPostgreSQLAdapter(connection, readonly=True)
        self.assertEqual(connection.session, {"readonly": True, "autocommit": False})
        adapter.close()

    def test_real_adapter_configures_timeouts(self):
        connection = FakeConnection()
        adapter = BootstrapPostgreSQLAdapter(connection)
        adapter.begin_write()
        sql = " ".join(command[0] for command in connection.commands)
        self.assertIn("lock_timeout", sql)
        self.assertIn("statement_timeout", sql)
        adapter.close()

    def test_real_adapter_uses_bootstrap_advisory_lock(self):
        connection = FakeConnection()
        adapter = BootstrapPostgreSQLAdapter(connection)
        adapter.acquire_bootstrap_lock()
        self.assertEqual(connection.commands[-1][1], (BOOTSTRAP_POSTGRES_ADVISORY_LOCK_KEY,))
        adapter.close()

    def test_no_external_postgresql_connection_is_used_by_simulation(self):
        with mock.patch(
            "database_bootstrap.runner.open_bootstrap_adapter",
            side_effect=AssertionError("external connection"),
        ):
            self.bootstrap()


if __name__ == "__main__":
    unittest.main()
