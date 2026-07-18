from __future__ import annotations

import contextlib
import io
import os
import sqlite3
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

import server
from database_migrations.adapters import SQLiteAdapter
from database_migrations.models import AppliedMigration, Migration, validate_registry
from database_migrations.registry import MIGRATIONS, get_registry
from database_migrations.runner import (
    MigrationError,
    baseline_database,
    get_migration_status,
    require_migration_authorization,
    run_database_migrations,
    validate_history,
)
from database_migrations.schema import CURRENT_INDEX_NAMES, CURRENT_SCHEMA_STATEMENTS, CURRENT_TABLE_NAMES


AUTHORIZED_ENV = {"APP_ENV": "development", "MOVA_ALLOW_MIGRATIONS": "true"}


def create_empty_sqlite(path: str) -> None:
    connection = sqlite3.connect(path)
    connection.close()


def create_legacy_schema(path: str, *, omit_index: str = "", omit_discount: bool = False) -> None:
    connection = sqlite3.connect(path)
    try:
        for statement in CURRENT_SCHEMA_STATEMENTS:
            if omit_index and statement.startswith(f"CREATE INDEX {omit_index} "):
                continue
            if omit_index and statement.startswith(f"CREATE UNIQUE INDEX {omit_index} "):
                continue
            if omit_discount and statement.startswith("CREATE TABLE payables"):
                statement = statement.replace("    discount REAL NOT NULL DEFAULT 0,\n", "")
            connection.execute(statement)
        connection.commit()
    finally:
        connection.close()


class RegistryTests(unittest.TestCase):
    def test_registry_contains_only_migration_001(self):
        self.assertEqual([item.version for item in MIGRATIONS], [1])
        self.assertEqual(MIGRATIONS[0].description, "Create current schema")

    def test_registry_metadata_is_valid(self):
        migration = MIGRATIONS[0]
        self.assertIsInstance(migration.version, int)
        self.assertGreater(migration.version, 0)
        self.assertTrue(migration.description)
        self.assertRegex(migration.checksum, r"^[0-9a-f]{64}$")

    def test_checksum_is_deterministic(self):
        self.assertEqual(MIGRATIONS[0].checksum, MIGRATIONS[0].checksum)

    def test_checksum_normalizes_line_endings_and_outer_space(self):
        first = Migration(1, " Test ", ("CREATE\r\nTABLE x (id INTEGER)\r\n",), (" SELECT 1 ",), " code ")
        second = Migration(1, "Test", ("CREATE\nTABLE x (id INTEGER)",), ("SELECT 1",), "code")
        self.assertEqual(first.checksum, second.checksum)

    def test_registry_rejects_duplicate_version(self):
        duplicate = Migration(1, "Duplicate", ("SELECT 1",), ("SELECT 1",))
        with self.assertRaisesRegex(ValueError, "duplicada"):
            validate_registry((MIGRATIONS[0], duplicate))

    def test_registry_rejects_gap(self):
        gap = Migration(2, "Gap", ("SELECT 1",), ("SELECT 1",))
        with self.assertRaisesRegex(ValueError, "lacuna"):
            validate_registry((gap,))

    def test_registry_sorts_migrations(self):
        second = Migration(2, "Second", ("SELECT 1",), ("SELECT 1",))
        self.assertEqual([item.version for item in validate_registry((second, MIGRATIONS[0]))], [1, 2])

    def test_registry_rejects_empty_description(self):
        invalid = Migration(1, " ", ("SELECT 1",), ("SELECT 1",))
        with self.assertRaisesRegex(ValueError, "descricao"):
            validate_registry((invalid,))


class SQLiteMigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "migrations.db")

    def tearDown(self):
        self.temp_dir.cleanup()

    def migrate(self, **kwargs):
        return run_database_migrations(
            environ=AUTHORIZED_ENV,
            sqlite_path=self.db_path,
            create_database=True,
            **kwargs,
        )

    def test_status_missing_database_does_not_create_file(self):
        result = get_migration_status(environ=AUTHORIZED_ENV, sqlite_path=self.db_path)
        self.assertEqual(result["state"], "database_missing")
        self.assertFalse(os.path.exists(self.db_path))

    def test_status_empty_existing_database_is_read_only(self):
        create_empty_sqlite(self.db_path)
        result = get_migration_status(environ=AUTHORIZED_ENV, sqlite_path=self.db_path)
        self.assertEqual(result["state"], "empty")
        with contextlib.closing(sqlite3.connect(self.db_path)) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM sqlite_master").fetchone()[0], 0)

    def test_migrate_without_create_rejects_missing_database(self):
        with self.assertRaisesRegex(MigrationError, "--create"):
            run_database_migrations(environ=AUTHORIZED_ENV, sqlite_path=self.db_path)
        self.assertFalse(os.path.exists(self.db_path))

    def test_migrate_with_create_builds_current_schema(self):
        result = self.migrate()
        self.assertEqual(result["applied"], [1])
        with contextlib.closing(sqlite3.connect(self.db_path)) as connection:
            tables = {
                row[0] for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
            }
        self.assertEqual(tables - {"schema_migrations"}, set(CURRENT_TABLE_NAMES))
        self.assertEqual(len(tables), 20)

    def test_migration_creates_all_thirty_indexes(self):
        self.migrate()
        with contextlib.closing(sqlite3.connect(self.db_path)) as connection:
            indexes = {
                row[0] for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_autoindex_%'"
                )
            }
        self.assertEqual(indexes, set(CURRENT_INDEX_NAMES))
        self.assertEqual(len(indexes), 30)

    def test_migration_includes_payables_discount_without_alter(self):
        self.assertTrue(any("discount REAL NOT NULL DEFAULT 0" in item for item in MIGRATIONS[0].sqlite_statements))
        self.assertFalse(any("ALTER TABLE" in item.upper() for item in MIGRATIONS[0].sqlite_statements))
        self.migrate()
        with contextlib.closing(sqlite3.connect(self.db_path)) as connection:
            columns = {row[1] for row in connection.execute("PRAGMA table_info(payables)")}
        self.assertIn("discount", columns)

    def test_history_has_one_complete_row(self):
        self.migrate()
        with contextlib.closing(sqlite3.connect(self.db_path)) as connection:
            row = connection.execute(
                "SELECT version, description, applied_at, checksum, execution_time_ms FROM schema_migrations"
            ).fetchone()
        self.assertEqual(row[0], 1)
        self.assertEqual(row[1], MIGRATIONS[0].description)
        self.assertEqual(row[3], MIGRATIONS[0].checksum)
        self.assertGreaterEqual(row[4], 0)
        parsed = datetime.fromisoformat(row[2].replace("Z", "+00:00"))
        self.assertEqual(parsed.utcoffset(), timezone.utc.utcoffset(parsed))

    def test_migration_does_not_bootstrap_operational_data(self):
        self.migrate()
        with contextlib.closing(sqlite3.connect(self.db_path)) as connection:
            for table in CURRENT_TABLE_NAMES:
                self.assertEqual(connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0], 0, table)

    def test_migration_does_not_create_store_app_state_or_admin(self):
        self.migrate()
        with contextlib.closing(sqlite3.connect(self.db_path)) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM stores").fetchone()[0], 0)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM app_state").fetchone()[0], 0)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM users").fetchone()[0], 0)

    def test_reexecution_is_idempotent(self):
        first = self.migrate()
        second = self.migrate()
        self.assertEqual(first["applied"], [1])
        self.assertEqual(second["applied"], [])
        self.assertIn("Nenhuma", second["message"])
        with contextlib.closing(sqlite3.connect(self.db_path)) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0], 1)

    def test_status_versioned_database_is_up_to_date(self):
        self.migrate()
        status = get_migration_status(environ=AUTHORIZED_ENV, sqlite_path=self.db_path)
        self.assertTrue(status["ok"])
        self.assertEqual(status["state"], "up_to_date")
        self.assertEqual(status["current_version"], 1)

    def test_status_identifies_pending_migration(self):
        self.migrate()
        second = Migration(2, "Second", ("SELECT 1",), ("SELECT 1",))
        status = get_migration_status(
            environ=AUTHORIZED_ENV,
            sqlite_path=self.db_path,
            migrations=(MIGRATIONS[0], second),
        )
        self.assertEqual(status["state"], "pending")
        self.assertEqual(status["pending"], [2])

    def test_status_identifies_checksum_mismatch(self):
        self.migrate()
        with contextlib.closing(sqlite3.connect(self.db_path)) as connection:
            connection.execute("UPDATE schema_migrations SET checksum = ?", ("0" * 64,))
            connection.commit()
        status = get_migration_status(environ=AUTHORIZED_ENV, sqlite_path=self.db_path)
        self.assertFalse(status["ok"])
        self.assertEqual(status["state"], "checksum_mismatch")

    def test_status_identifies_future_version(self):
        self.migrate()
        with contextlib.closing(sqlite3.connect(self.db_path)) as connection:
            connection.execute(
                "UPDATE schema_migrations SET version = 2, description = 'Future', checksum = ?",
                ("0" * 64,),
            )
            connection.commit()
        status = get_migration_status(environ=AUTHORIZED_ENV, sqlite_path=self.db_path)
        self.assertFalse(status["ok"])
        self.assertEqual(status["state"], "future_version")

    def test_failure_rolls_back_schema_and_history(self):
        broken = Migration(
            1,
            "Broken",
            ("CREATE TABLE temporary_test (id INTEGER)", "INVALID SQL"),
            ("CREATE TABLE temporary_test (id INTEGER)", "INVALID SQL"),
        )
        with self.assertRaises(MigrationError):
            run_database_migrations(
                environ=AUTHORIZED_ENV,
                sqlite_path=self.db_path,
                create_database=True,
                migrations=(broken,),
            )
        with contextlib.closing(sqlite3.connect(self.db_path)) as connection:
            names = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertNotIn("temporary_test", names)
        self.assertNotIn("schema_migrations", names)

    def test_connection_is_closed_after_success(self):
        captured = []

        def factory(target, *, readonly, create):
            adapter = SQLiteAdapter(sqlite3.connect(target.sqlite_path, isolation_level=None), target.sqlite_path, readonly=readonly)
            captured.append(adapter)
            return adapter

        self.migrate(adapter_factory=factory)
        self.assertTrue(captured)
        self.assertTrue(all(adapter.closed for adapter in captured))

    def test_begin_immediate_is_used(self):
        calls = []
        original = SQLiteAdapter.begin_write

        def spy(adapter):
            calls.append(True)
            return original(adapter)

        with mock.patch.object(SQLiteAdapter, "begin_write", spy):
            self.migrate()
        self.assertEqual(calls, [True])

    def test_lock_failure_aborts_without_history(self):
        class LockedAdapter(SQLiteAdapter):
            def begin_write(self):
                raise sqlite3.OperationalError("database is locked")

        def factory(target, *, readonly, create):
            connection = sqlite3.connect(target.sqlite_path, isolation_level=None)
            return LockedAdapter(connection, target.sqlite_path, readonly=readonly)

        with self.assertRaisesRegex(MigrationError, "revertida"):
            self.migrate(adapter_factory=factory)

    def test_real_sqlite_lock_prevents_concurrent_executor(self):
        create_empty_sqlite(self.db_path)
        blocker = sqlite3.connect(self.db_path, isolation_level=None)
        blocker.execute("BEGIN IMMEDIATE")

        def factory(target, *, readonly, create):
            adapter = SQLiteAdapter(
                sqlite3.connect(target.sqlite_path, isolation_level=None),
                target.sqlite_path,
                readonly=readonly,
            )
            adapter.connection.execute("PRAGMA busy_timeout = 10")
            return adapter

        try:
            with self.assertRaisesRegex(MigrationError, "revertida"):
                run_database_migrations(
                    environ=AUTHORIZED_ENV,
                    sqlite_path=self.db_path,
                    adapter_factory=factory,
                )
        finally:
            blocker.rollback()
            blocker.close()

        with contextlib.closing(sqlite3.connect(self.db_path)) as connection:
            self.assertNotIn(
                "schema_migrations",
                {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")},
            )


class SQLiteBaselineTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "legacy.db")

    def tearDown(self):
        self.temp_dir.cleanup()

    def baseline(self, **kwargs):
        return baseline_database(
            environ=AUTHORIZED_ENV,
            sqlite_path=self.db_path,
            confirm_baseline=True,
            **kwargs,
        )

    def test_baseline_rejects_missing_database(self):
        with self.assertRaises(MigrationError):
            self.baseline()
        self.assertFalse(os.path.exists(self.db_path))

    def test_baseline_rejects_empty_database(self):
        create_empty_sqlite(self.db_path)
        with self.assertRaises(MigrationError):
            self.baseline()

    def test_baseline_requires_confirmation(self):
        create_legacy_schema(self.db_path)
        with self.assertRaisesRegex(MigrationError, "confirm-baseline"):
            baseline_database(environ=AUTHORIZED_ENV, sqlite_path=self.db_path)

    def test_baseline_rejects_partial_schema(self):
        with contextlib.closing(sqlite3.connect(self.db_path)) as connection:
            connection.execute("CREATE TABLE stores (id TEXT PRIMARY KEY)")
        with self.assertRaises(MigrationError):
            self.baseline()

    def test_baseline_rejects_missing_discount(self):
        create_legacy_schema(self.db_path, omit_discount=True)
        with self.assertRaises(MigrationError):
            self.baseline()

    def test_baseline_rejects_missing_required_index(self):
        create_legacy_schema(self.db_path, omit_index="idx_users_store_login")
        with self.assertRaises(MigrationError):
            self.baseline()

    def test_baseline_accepts_integral_legacy_schema(self):
        create_legacy_schema(self.db_path)
        result = self.baseline()
        self.assertFalse(result["already_baselined"])
        with contextlib.closing(sqlite3.connect(self.db_path)) as connection:
            row = connection.execute("SELECT version, checksum FROM schema_migrations").fetchone()
        self.assertEqual(row, (1, MIGRATIONS[0].checksum))

    def test_baseline_only_adds_history_table(self):
        create_legacy_schema(self.db_path)
        with contextlib.closing(sqlite3.connect(self.db_path)) as connection:
            before = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.baseline()
        with contextlib.closing(sqlite3.connect(self.db_path)) as connection:
            after = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertEqual(after - before, {"schema_migrations"})

    def test_baseline_preserves_business_rows(self):
        create_legacy_schema(self.db_path)
        with contextlib.closing(sqlite3.connect(self.db_path)) as connection:
            connection.execute("INSERT INTO stores (id, name, created_at) VALUES ('legacy', 'Legacy', '2026-01-01T00:00:00Z')")
            connection.commit()
        self.baseline()
        with contextlib.closing(sqlite3.connect(self.db_path)) as connection:
            self.assertEqual(connection.execute("SELECT name FROM stores WHERE id='legacy'").fetchone()[0], "Legacy")

    def test_baseline_is_idempotent_with_clear_result(self):
        create_legacy_schema(self.db_path)
        self.baseline()
        result = self.baseline()
        self.assertTrue(result["already_baselined"])

    def test_baseline_rejects_existing_incompatible_history(self):
        create_legacy_schema(self.db_path)
        self.baseline()
        with contextlib.closing(sqlite3.connect(self.db_path)) as connection:
            connection.execute("UPDATE schema_migrations SET checksum = ?", ("0" * 64,))
            connection.commit()
        with self.assertRaises(MigrationError) as context:
            self.baseline()
        self.assertEqual(context.exception.code, "checksum_mismatch")

    def test_status_marks_compatible_legacy_database(self):
        create_legacy_schema(self.db_path)
        status = get_migration_status(environ=AUTHORIZED_ENV, sqlite_path=self.db_path)
        self.assertEqual(status["state"], "legacy_compatible")
        self.assertTrue(status["baseline_possible"])

    def test_migrate_refuses_legacy_without_baseline(self):
        create_legacy_schema(self.db_path)
        with self.assertRaisesRegex(MigrationError, "baseline"):
            run_database_migrations(environ=AUTHORIZED_ENV, sqlite_path=self.db_path)


class HistoryValidationTests(unittest.TestCase):
    def valid_row(self, **changes):
        values = {
            "version": 1,
            "description": MIGRATIONS[0].description,
            "applied_at": "2026-07-18T12:00:00Z",
            "checksum": MIGRATIONS[0].checksum,
            "execution_time_ms": 1,
        }
        values.update(changes)
        return AppliedMigration(**values)

    def test_valid_history_is_accepted(self):
        self.assertEqual(len(validate_history([self.valid_row()], MIGRATIONS)), 1)

    def test_checksum_mismatch_is_blocked(self):
        with self.assertRaisesRegex(MigrationError, "Checksum"):
            validate_history([self.valid_row(checksum="0" * 64)], MIGRATIONS)

    def test_description_mismatch_is_blocked(self):
        with self.assertRaisesRegex(MigrationError, "Descricao"):
            validate_history([self.valid_row(description="Changed")], MIGRATIONS)

    def test_future_version_is_blocked(self):
        with self.assertRaises(MigrationError) as context:
            validate_history([self.valid_row(version=2)], MIGRATIONS)
        self.assertEqual(context.exception.code, "future_version")

    def test_duplicate_version_is_blocked(self):
        with self.assertRaises(MigrationError) as context:
            validate_history([self.valid_row(), self.valid_row()], MIGRATIONS)
        self.assertEqual(context.exception.code, "duplicate_version")

    def test_gap_is_blocked(self):
        second = Migration(2, "Second", ("SELECT 1",), ("SELECT 1",))
        registry = get_registry((MIGRATIONS[0], second))
        row = AppliedMigration(2, second.description, "2026-07-18T12:00:00Z", second.checksum, 1)
        with self.assertRaises(MigrationError) as context:
            validate_history([row], registry)
        self.assertEqual(context.exception.code, "version_gap")

    def test_negative_execution_time_is_blocked(self):
        with self.assertRaises(MigrationError):
            validate_history([self.valid_row(execution_time_ms=-1)], MIGRATIONS)

    def test_naive_timestamp_is_blocked(self):
        with self.assertRaises(MigrationError):
            validate_history([self.valid_row(applied_at="2026-07-18T12:00:00")], MIGRATIONS)


class AuthorizationTests(unittest.TestCase):
    def test_development_requires_flag(self):
        with self.assertRaises(MigrationError):
            require_migration_authorization({"APP_ENV": "development"})

    def test_staging_with_true_flag_is_allowed(self):
        self.assertEqual(
            require_migration_authorization({"APP_ENV": "staging", "MOVA_ALLOW_MIGRATIONS": "yes"}),
            "staging",
        )

    def test_production_requires_flag(self):
        with self.assertRaises(MigrationError):
            require_migration_authorization({"APP_ENV": "production"}, confirm_production=True)

    def test_production_requires_confirmation(self):
        with self.assertRaises(MigrationError) as context:
            require_migration_authorization({"APP_ENV": "production", "MOVA_ALLOW_MIGRATIONS": "true"})
        self.assertEqual(context.exception.code, "production_confirmation_required")

    def test_production_with_double_authorization_is_allowed(self):
        self.assertEqual(
            require_migration_authorization(
                {"APP_ENV": "production", "MOVA_ALLOW_MIGRATIONS": "on"},
                confirm_production=True,
            ),
            "production",
        )

    def test_unknown_flag_is_false(self):
        with self.assertRaises(MigrationError):
            require_migration_authorization({"APP_ENV": "development", "MOVA_ALLOW_MIGRATIONS": "maybe"})

    def test_missing_or_invalid_environment_is_blocked(self):
        for environment in ("", "invalid", "test"):
            with self.subTest(environment=environment), self.assertRaises(MigrationError):
                require_migration_authorization({"APP_ENV": environment, "MOVA_ALLOW_MIGRATIONS": "true"})

    def test_controlled_test_mode_is_allowed_without_environment(self):
        self.assertEqual(require_migration_authorization({}, test_mode=True), "test")


class ReadinessAndSentinelTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "readiness.db")
        self.original = (server.DB_PATH, server.DATABASE_URL, server.USE_POSTGRES)

    def tearDown(self):
        server.DB_PATH, server.DATABASE_URL, server.USE_POSTGRES = self.original
        self.temp_dir.cleanup()

    def test_migrated_database_is_ready_and_readiness_is_read_only(self):
        run_database_migrations(environ=AUTHORIZED_ENV, sqlite_path=self.db_path, create_database=True)
        server.DB_PATH = self.db_path
        server.DATABASE_URL = ""
        server.USE_POSTGRES = False
        with mock.patch("database_migrations.runner.run_database_migrations") as migration_runner:
            response = server.app.test_client().get("/api/readiness")
        self.assertEqual(response.status_code, 200)
        migration_runner.assert_not_called()

    def test_baselined_database_is_ready(self):
        create_legacy_schema(self.db_path)
        baseline_database(environ=AUTHORIZED_ENV, sqlite_path=self.db_path, confirm_baseline=True)
        server.DB_PATH = self.db_path
        server.DATABASE_URL = ""
        server.USE_POSTGRES = False
        self.assertEqual(server.app.test_client().get("/api/readiness").status_code, 200)

    def test_runner_never_calls_runtime_bootstrap_functions(self):
        with (
            mock.patch.object(server, "init_db") as init_db,
            mock.patch.object(server, "write_state") as write_state,
            mock.patch.object(server, "sync_business_tables") as sync_business_tables,
            mock.patch.object(server, "create_initial_admin_user") as create_admin,
        ):
            run_database_migrations(environ=AUTHORIZED_ENV, sqlite_path=self.db_path, create_database=True)
        init_db.assert_not_called()
        write_state.assert_not_called()
        sync_business_tables.assert_not_called()
        create_admin.assert_not_called()

    def test_no_http_migration_route_exists(self):
        routes = {rule.rule for rule in server.app.url_map.iter_rules()}
        self.assertFalse(any("migration" in route for route in routes))

    def test_health_does_not_execute_runner(self):
        with mock.patch("database_migrations.runner.run_database_migrations") as migration_runner:
            response = server.app.test_client().get("/api/health")
        self.assertEqual(response.status_code, 200)
        migration_runner.assert_not_called()

    def test_importing_package_does_not_open_connection(self):
        import importlib
        import database_migrations

        with mock.patch("sqlite3.connect") as connect:
            importlib.reload(database_migrations)
        connect.assert_not_called()

    def test_server_and_wsgi_do_not_reference_migration_runner(self):
        root = Path(server.__file__).resolve().parent
        for filename in ("server.py", "wsgi.py"):
            source = (root / filename).read_text(encoding="utf-8")
            self.assertNotIn("run_database_migrations", source, filename)
            self.assertNotIn("baseline_database", source, filename)

    def test_readiness_does_not_change_migration_history(self):
        run_database_migrations(environ=AUTHORIZED_ENV, sqlite_path=self.db_path, create_database=True)
        with contextlib.closing(sqlite3.connect(self.db_path)) as connection:
            before = connection.execute(
                "SELECT version, description, applied_at, checksum, execution_time_ms FROM schema_migrations"
            ).fetchall()
        server.DB_PATH = self.db_path
        server.DATABASE_URL = ""
        server.USE_POSTGRES = False
        self.assertEqual(server.app.test_client().get("/api/readiness").status_code, 200)
        with contextlib.closing(sqlite3.connect(self.db_path)) as connection:
            after = connection.execute(
                "SELECT version, description, applied_at, checksum, execution_time_ms FROM schema_migrations"
            ).fetchall()
        self.assertEqual(after, before)


if __name__ == "__main__":
    unittest.main()
