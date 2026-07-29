from __future__ import annotations

import unittest
from copy import deepcopy

from database_migrations.adapters import (
    POSTGRES_ADVISORY_LOCK_KEY,
    POSTGRES_LOCK_TIMEOUT,
    POSTGRES_STATEMENT_TIMEOUT,
    PostgreSQLAdapter,
    SchemaValidation,
    _normalize_check_constraint,
    _normalize_index_predicate,
    _postgres_custom_index_names,
)
from database_migrations.models import AppliedMigration, Migration
from database_migrations.registry import MIGRATIONS
from database_migrations.runner import (
    MigrationError,
    baseline_database,
    get_migration_status,
    run_database_migrations,
)


AUTHORIZED_ENV = {
    "APP_ENV": "development",
    "MOVA_ALLOW_MIGRATIONS": "true",
    "DATABASE_URL": "postgresql://not-used.invalid/mova",
}


class RecordingCursor:
    def __init__(self, connection):
        self.connection = connection
        self.description = None
        self.closed = False

    def execute(self, sql, params=()):
        self.connection.statements.append((" ".join(sql.split()), tuple(params)))

    def fetchall(self):
        return []

    def close(self):
        self.closed = True


class RecordingConnection:
    def __init__(self):
        self.autocommit = True
        self.statements = []
        self.session_calls = []
        self.commits = 0
        self.rollbacks = 0
        self.closed = False

    def cursor(self):
        return RecordingCursor(self)

    def set_session(self, **kwargs):
        self.session_calls.append(kwargs)

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        self.closed = True


class PostgreSQLAdapterTests(unittest.TestCase):
    def test_postgresql_check_normalizes_numeric_cast(self):
        self.assertEqual(
            _normalize_check_constraint("CHECK ((total_cost > (0)::double precision))"),
            _normalize_check_constraint("total_cost > 0"),
        )

    def test_postgresql_check_normalizes_in_as_any_array(self):
        self.assertEqual(
            _normalize_check_constraint(
                "CHECK ((theme = ANY (ARRAY['light'::text, 'dark'::text, 'system'::text])))"
            ),
            _normalize_check_constraint("theme IN ('light', 'dark', 'system')"),
        )

    def test_postgresql_check_preserves_semantic_difference(self):
        self.assertNotEqual(
            _normalize_check_constraint("quantity > 0"),
            _normalize_check_constraint("quantity >= 0"),
        )

    def test_postgresql_constraint_indexes_are_not_custom_indexes(self):
        self.assertEqual(
            _postgres_custom_index_names(
                {"idx_business", "users_login_key", "users_pkey"},
                {"users_login_key", "users_pkey"},
            ),
            {"idx_business"},
        )

    def test_postgresql_index_predicate_normalizes_equivalent_text_cast(self):
        expected = "cpf IS NOT NULL AND cpf <> ''"
        actual = "((cpf IS NOT NULL) AND (cpf <> ''::text))"
        self.assertEqual(
            _normalize_index_predicate(actual),
            _normalize_index_predicate(expected),
        )

    def test_postgresql_index_predicate_preserves_semantic_difference(self):
        expected = "cpf IS NOT NULL AND cpf <> ''"
        actual = "cpf IS NOT NULL"
        self.assertNotEqual(
            _normalize_index_predicate(actual),
            _normalize_index_predicate(expected),
        )

    def test_adapter_disables_autocommit(self):
        connection = RecordingConnection()
        PostgreSQLAdapter(connection)
        self.assertFalse(connection.autocommit)

    def test_readonly_adapter_configures_readonly_session(self):
        connection = RecordingConnection()
        PostgreSQLAdapter(connection, readonly=True)
        self.assertEqual(connection.session_calls, [{"readonly": True, "autocommit": False}])

    def test_begin_configures_safe_timeouts(self):
        connection = RecordingConnection()
        adapter = PostgreSQLAdapter(connection)
        adapter.begin_write()
        self.assertEqual(
            connection.statements,
            [
                ("SET LOCAL lock_timeout = %s", (POSTGRES_LOCK_TIMEOUT,)),
                ("SET LOCAL statement_timeout = %s", (POSTGRES_STATEMENT_TIMEOUT,)),
            ],
        )

    def test_advisory_lock_uses_stable_key(self):
        connection = RecordingConnection()
        adapter = PostgreSQLAdapter(connection)
        adapter.acquire_migration_lock()
        self.assertEqual(
            connection.statements,
            [("SELECT pg_advisory_xact_lock(%s)", (POSTGRES_ADVISORY_LOCK_KEY,))],
        )

    def test_apply_uses_postgresql_statements_in_order(self):
        connection = RecordingConnection()
        adapter = PostgreSQLAdapter(connection)
        migration = Migration(1, "test", ("SQLITE",), ("FIRST", "SECOND"))
        adapter.apply_migration(migration)
        self.assertEqual([item[0] for item in connection.statements], ["FIRST", "SECOND"])

    def test_commit_rollback_and_close_are_delegated(self):
        connection = RecordingConnection()
        adapter = PostgreSQLAdapter(connection)
        adapter.commit()
        adapter.rollback()
        adapter.close()
        adapter.close()
        self.assertEqual(connection.commits, 1)
        self.assertEqual(connection.rollbacks, 1)
        self.assertTrue(connection.closed)


class FakePostgresState:
    def __init__(self, *, schema=False, history=None):
        self.schema = schema
        self.history = list(history or [])
        self.business_rows = 0
        self.begin_calls = 0
        self.lock_calls = 0
        self.commit_calls = 0
        self.rollback_calls = 0
        self.close_calls = 0
        self.history_create_calls = 0
        self.apply_calls = []
        self.readonly_writes = 0
        self.fail_apply = False
        self.v17_validation_calls = 0


class FakePostgresAdapter:
    driver = "postgresql"

    def __init__(self, state: FakePostgresState, *, readonly: bool):
        self.state = state
        self.readonly = readonly
        self.closed = False
        self._pending = None

    def _working(self):
        return self._pending if self._pending is not None else {
            "schema": self.state.schema,
            "history": deepcopy(self.state.history),
        }

    def begin_write(self):
        if self.readonly:
            self.state.readonly_writes += 1
            raise AssertionError("write in readonly adapter")
        self.state.begin_calls += 1
        self._pending = {"schema": self.state.schema, "history": deepcopy(self.state.history)}

    def acquire_migration_lock(self):
        self.state.lock_calls += 1

    def commit(self):
        self.state.commit_calls += 1
        if self._pending is not None:
            self.state.schema = self._pending["schema"]
            self.state.history = self._pending["history"]
            self._pending = None

    def rollback(self):
        self.state.rollback_calls += 1
        self._pending = None

    def close(self):
        if not self.closed:
            self.closed = True
            self.state.close_calls += 1

    def table_names(self):
        working = self._working()
        names = {"stores"} if working["schema"] else set()
        if working["history"] is not None and (self.state.history_create_calls or self.state.history):
            names.add("schema_migrations")
        return names

    def history_exists(self):
        return "schema_migrations" in self.table_names()

    def create_history_table(self):
        self.state.history_create_calls += 1

    def load_history(self):
        return deepcopy(self._working()["history"])

    def apply_migration(self, migration):
        self.state.apply_calls.append(migration.version)
        if self.state.fail_apply:
            raise RuntimeError("simulated failure")
        self._pending["schema"] = True

    def insert_history(self, migration, applied_at, execution_time_ms):
        self._pending["history"].append(
            AppliedMigration(
                migration.version,
                migration.description,
                applied_at,
                migration.checksum,
                execution_time_ms,
            )
        )

    def validate_current_schema(self):
        return SchemaValidation(bool(self._working()["schema"]), () if self._working()["schema"] else ("schema",))

    def validate_v1_schema(self):
        return self.validate_current_schema()

    def validate_v17_schema(self):
        self.state.v17_validation_calls += 1
        return self.validate_current_schema()

    def business_row_count(self):
        return self.state.business_rows


def factory_for(state):
    def factory(_target, *, readonly, create):
        if create:
            raise AssertionError("PostgreSQL must not use SQLite create semantics")
        return FakePostgresAdapter(state, readonly=readonly)

    return factory


class PostgreSQLRunnerTests(unittest.TestCase):
    def test_status_uses_v17_snapshot_before_migration_18(self):
        history = [
            AppliedMigration(
                migration.version,
                migration.description,
                "2026-07-18T12:00:00Z",
                migration.checksum,
                1,
            )
            for migration in MIGRATIONS[:17]
        ]
        state = FakePostgresState(schema=True, history=history)
        result = get_migration_status(
            environ=AUTHORIZED_ENV,
            adapter_factory=factory_for(state),
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["state"], "pending")
        self.assertEqual(result["pending"], [18])
        self.assertEqual(state.v17_validation_calls, 1)

    def test_status_is_readonly_and_does_not_create_history(self):
        state = FakePostgresState()
        result = get_migration_status(environ=AUTHORIZED_ENV, adapter_factory=factory_for(state))
        self.assertEqual(result["state"], "empty")
        self.assertEqual(state.history_create_calls, 0)
        self.assertEqual(state.readonly_writes, 0)
        self.assertEqual(state.close_calls, 1)

    def test_migrate_applies_records_locks_commits_and_closes(self):
        state = FakePostgresState()
        result = run_database_migrations(environ=AUTHORIZED_ENV, adapter_factory=factory_for(state))
        self.assertEqual(result["applied"], list(range(1, 19)))
        self.assertEqual(state.apply_calls, list(range(1, 19)))
        self.assertEqual(state.lock_calls, len(MIGRATIONS))
        self.assertEqual(state.commit_calls, len(MIGRATIONS))
        self.assertEqual(len(state.history), len(MIGRATIONS))
        self.assertEqual(
            [item.checksum for item in state.history],
            [item.checksum for item in MIGRATIONS],
        )
        self.assertEqual(state.close_calls, 2)

    def test_failure_rolls_back_and_closes_without_history(self):
        state = FakePostgresState()
        state.fail_apply = True
        with self.assertRaises(MigrationError):
            run_database_migrations(environ=AUTHORIZED_ENV, adapter_factory=factory_for(state))
        self.assertGreaterEqual(state.rollback_calls, 1)
        self.assertEqual(state.commit_calls, 0)
        self.assertEqual(state.history, [])
        self.assertEqual(state.close_calls, 2)

    def test_checksum_mismatch_blocks_before_apply(self):
        row = AppliedMigration(1, MIGRATIONS[0].description, "2026-07-18T12:00:00Z", "0" * 64, 1)
        state = FakePostgresState(schema=True, history=[row])
        with self.assertRaises(MigrationError) as context:
            run_database_migrations(environ=AUTHORIZED_ENV, adapter_factory=factory_for(state))
        self.assertEqual(context.exception.code, "checksum_mismatch")
        self.assertEqual(state.apply_calls, [])

    def test_future_version_blocks_before_apply(self):
        history = [
            AppliedMigration(
                migration.version,
                migration.description,
                "2026-07-18T12:00:00Z",
                migration.checksum,
                1,
            )
            for migration in MIGRATIONS
        ]
        history.append(AppliedMigration(19, "Future", "2026-07-18T12:00:00Z", "0" * 64, 1))
        state = FakePostgresState(schema=True, history=history)
        with self.assertRaises(MigrationError) as context:
            run_database_migrations(environ=AUTHORIZED_ENV, adapter_factory=factory_for(state))
        self.assertEqual(context.exception.code, "future_version")
        self.assertEqual(state.apply_calls, [])

    def test_baseline_validates_schema_and_only_records_history(self):
        state = FakePostgresState(schema=True)
        result = baseline_database(
            environ=AUTHORIZED_ENV,
            adapter_factory=factory_for(state),
            confirm_baseline=True,
        )
        self.assertFalse(result["already_baselined"])
        self.assertEqual(state.apply_calls, [])
        self.assertEqual(state.lock_calls, 1)
        self.assertEqual(len(state.history), 1)

    def test_baseline_rejects_invalid_schema(self):
        state = FakePostgresState(schema=False)
        with self.assertRaises(MigrationError):
            baseline_database(
                environ=AUTHORIZED_ENV,
                adapter_factory=factory_for(state),
                confirm_baseline=True,
            )
        self.assertEqual(state.history, [])


if __name__ == "__main__":
    unittest.main()
