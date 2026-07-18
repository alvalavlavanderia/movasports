import gc
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from contextlib import contextmanager
from unittest import mock

from environment_config import EnvironmentConfig
import server


class TrackingReadinessConnection:
    def __init__(self, connection, statements):
        self.connection = connection
        self.statements = statements
        self.closed = False

    @property
    def row_factory(self):
        return self.connection.row_factory

    @row_factory.setter
    def row_factory(self, value):
        self.connection.row_factory = value

    def execute(self, sql, params=()):
        self.statements.append((sql.strip(), tuple(params or ())))
        return self.connection.execute(sql, params or ())

    def close(self):
        self.closed = True
        self.connection.close()


class FakeCursor:
    def __init__(self, rows):
        self.rows = rows

    def fetchall(self):
        return list(self.rows)


class FakePostgresDriverConnection:
    def __init__(self):
        self.readonly = None
        self.autocommit = None
        self.rolled_back = False
        self.closed = False

    def set_session(self, readonly, autocommit):
        self.readonly = readonly
        self.autocommit = autocommit

    def rollback(self):
        self.rolled_back = True

    def close(self):
        self.closed = True


class FakePostgresReadinessConnection:
    def __init__(self, missing_table=None, version=None):
        self.conn = FakePostgresDriverConnection()
        self.missing_table = missing_table
        self.version = version
        self.statements = []

    def execute(self, sql, params=()):
        normalized = " ".join(sql.split()).lower()
        self.statements.append((normalized, tuple(params or ())))
        tables = set(server.REQUIRED_SCHEMA_TABLES)
        if self.missing_table:
            tables.discard(self.missing_table)
        if self.version is not None:
            tables.add("schema_migrations")
        if "information_schema.tables" in normalized:
            return FakeCursor([{"table_name": table} for table in sorted(tables)])
        if "information_schema.columns" in normalized:
            rows = []
            for table in sorted(tables):
                required = set(server.REQUIRED_SCHEMA_COLUMNS.get(table, {"version"}))
                for column in sorted(required):
                    rows.append({"table_name": table, "column_name": column})
            return FakeCursor(rows)
        if "from pg_indexes" in normalized:
            rows = []
            for name, (table, columns, unique) in server.REQUIRED_SCHEMA_INDEXES.items():
                definition = (
                    f"CREATE {'UNIQUE ' if unique else ''}INDEX {name} "
                    f"ON public.{table} USING btree ({', '.join(columns)})"
                )
                rows.append({"tablename": table, "indexname": name, "indexdef": definition})
            return FakeCursor(rows)
        if "select version from schema_migrations" in normalized:
            return FakeCursor([{"version": self.version}])
        raise AssertionError(f"Consulta PostgreSQL inesperada: {normalized}")


class DatabaseReadinessTest(unittest.TestCase):
    ADMIN_PASSWORD = "Readiness-Test-9"

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original = {
            "db_path": server.DB_PATH,
            "database_url": server.DATABASE_URL,
            "use_postgres": server.USE_POSTGRES,
            "environment": server.ENVIRONMENT,
            "testing": server.app.config.get("TESTING"),
            "admin_password": os.environ.get("MOVA_ADMIN_PASSWORD"),
        }
        server.DB_PATH = os.path.join(self.temp_dir.name, "readiness.db")
        server.DATABASE_URL = ""
        server.USE_POSTGRES = False
        server.ENVIRONMENT = EnvironmentConfig("development", "configured", False, False)
        server.app.config["TESTING"] = True
        os.environ["MOVA_ADMIN_PASSWORD"] = self.ADMIN_PASSWORD
        self.client = server.app.test_client()

    def tearDown(self):
        server.DB_PATH = self.original["db_path"]
        server.DATABASE_URL = self.original["database_url"]
        server.USE_POSTGRES = self.original["use_postgres"]
        server.ENVIRONMENT = self.original["environment"]
        server.app.config["TESTING"] = self.original["testing"]
        if self.original["admin_password"] is None:
            os.environ.pop("MOVA_ADMIN_PASSWORD", None)
        else:
            os.environ["MOVA_ADMIN_PASSWORD"] = self.original["admin_password"]
        self.client = None
        gc.collect()
        self.temp_dir.cleanup()

    def prepare_legacy_schema(self):
        server.init_db()
        gc.collect()

    @contextmanager
    def structural_sentinels(self):
        forbidden = AssertionError("Readiness executou rotina estrutural.")
        with (
            mock.patch.object(server, "init_db", side_effect=forbidden),
            mock.patch.object(server, "write_state", side_effect=forbidden),
            mock.patch.object(server, "sync_business_tables", side_effect=forbidden),
            mock.patch.object(server, "create_initial_admin_user", side_effect=forbidden),
            mock.patch.object(server, "refresh_session_user", side_effect=forbidden),
            mock.patch.object(server, "_open_auth_read_connection", side_effect=forbidden),
            mock.patch.object(server, "record_audit", side_effect=forbidden),
        ):
            yield

    def assert_ready(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"ok": True, "status": "ready"})

    def assert_not_ready(self, response):
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.get_json(), {
            "ok": False,
            "status": "not_ready",
            "error": "Serviço temporariamente indisponível.",
        })

    def add_schema_versions(self, versions, column="version INTEGER NOT NULL"):
        with sqlite3.connect(server.DB_PATH) as connection:
            connection.execute(
                f"CREATE TABLE schema_migrations ({column}, applied_at TEXT NOT NULL)"
            )
            for version in versions:
                connection.execute(
                    "INSERT INTO schema_migrations (version, applied_at) VALUES (?, ?)",
                    (version, server.utc_now()),
                )

    def test_health_remains_liveness_without_database_access(self):
        missing_path = os.path.join(self.temp_dir.name, "health-missing.db")
        server.DB_PATH = missing_path
        with (
            self.structural_sentinels(),
            mock.patch.object(
                server,
                "check_database_readiness",
                side_effect=AssertionError("Health tentou acessar readiness."),
            ),
        ):
            response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["ok"])
        self.assertFalse(os.path.exists(missing_path))

    def test_readiness_is_public_and_does_not_touch_session_or_structural_helpers(self):
        self.prepare_legacy_schema()
        session_user = {"id": "stale", "name": "Stale", "login": "stale", "role": "admin"}
        with self.client.session_transaction() as flask_session:
            flask_session["user"] = session_user
        with self.structural_sentinels(), self.assertLogs(server.app.logger, level="WARNING"):
            response = self.client.get("/api/readiness")
        self.assert_ready(response)
        with self.client.session_transaction() as flask_session:
            self.assertEqual(flask_session.get("user"), session_user)

    def test_missing_and_empty_sqlite_database_return_generic_503_without_creation(self):
        missing_path = os.path.join(self.temp_dir.name, "missing.db")
        server.DB_PATH = missing_path
        missing = self.client.get("/api/readiness")
        self.assert_not_ready(missing)
        self.assertFalse(os.path.exists(missing_path))

        empty_path = os.path.join(self.temp_dir.name, "empty.db")
        Path(empty_path).touch()
        server.DB_PATH = empty_path
        empty = self.client.get("/api/readiness")
        self.assert_not_ready(empty)
        self.assertEqual(os.path.getsize(empty_path), 0)

    def test_partial_schema_and_required_tables_return_503(self):
        with sqlite3.connect(server.DB_PATH) as connection:
            connection.execute("CREATE TABLE users (id TEXT PRIMARY KEY)")
        self.assert_not_ready(self.client.get("/api/readiness"))

        for missing_table in ("users", "payables"):
            server.DB_PATH = os.path.join(self.temp_dir.name, f"missing-{missing_table}.db")
            self.prepare_legacy_schema()
            with sqlite3.connect(server.DB_PATH) as connection:
                connection.execute(f'DROP TABLE "{missing_table}"')
            self.assert_not_ready(self.client.get("/api/readiness"))

    def test_legacy_schema_is_ready_and_emits_warning(self):
        self.prepare_legacy_schema()
        with self.structural_sentinels(), self.assertLogs(server.app.logger, level="WARNING") as logs:
            response = self.client.get("/api/readiness")
        self.assert_ready(response)
        self.assertTrue(any("schema legado" in message for message in logs.output))

    def test_missing_discount_and_required_unique_index_return_503(self):
        self.prepare_legacy_schema()
        with sqlite3.connect(server.DB_PATH) as connection:
            connection.execute("ALTER TABLE payables RENAME TO payables_with_discount")
            connection.execute(
                "CREATE TABLE payables (id TEXT PRIMARY KEY, store_id TEXT NOT NULL)"
            )
        self.assert_not_ready(self.client.get("/api/readiness"))

        for index_name in server.REQUIRED_SCHEMA_INDEXES:
            with self.subTest(index=index_name):
                server.DB_PATH = os.path.join(self.temp_dir.name, f"missing-{index_name}.db")
                self.prepare_legacy_schema()
                with sqlite3.connect(server.DB_PATH) as connection:
                    connection.execute(f'DROP INDEX "{index_name}"')
                self.assert_not_ready(self.client.get("/api/readiness"))

    def test_versioned_schema_accepts_current_and_maximum_version(self):
        self.prepare_legacy_schema()
        self.add_schema_versions([1, server.REQUIRED_SCHEMA_VERSION])
        self.assert_ready(self.client.get("/api/readiness"))

    def test_outdated_future_empty_and_invalid_versions_return_503(self):
        cases = [
            ("future", [server.REQUIRED_SCHEMA_VERSION + 1], "version INTEGER NOT NULL"),
            ("empty", [], "version INTEGER NOT NULL"),
            ("text", ["invalida"], "version TEXT NOT NULL"),
            ("negative", [-1], "version INTEGER NOT NULL"),
        ]
        for name, versions, column in cases:
            with self.subTest(name=name):
                server.DB_PATH = os.path.join(self.temp_dir.name, f"version-{name}.db")
                self.prepare_legacy_schema()
                self.add_schema_versions(versions, column)
                self.assert_not_ready(self.client.get("/api/readiness"))

        server.DB_PATH = os.path.join(self.temp_dir.name, "version-outdated.db")
        self.prepare_legacy_schema()
        self.add_schema_versions([server.REQUIRED_SCHEMA_VERSION])
        with mock.patch.object(server, "REQUIRED_SCHEMA_VERSION", 2):
            self.assert_not_ready(self.client.get("/api/readiness"))

    def test_version_table_without_version_column_returns_503(self):
        self.prepare_legacy_schema()
        with sqlite3.connect(server.DB_PATH) as connection:
            connection.execute(
                "CREATE TABLE schema_migrations (revision INTEGER, applied_at TEXT NOT NULL)"
            )
        self.assert_not_ready(self.client.get("/api/readiness"))

    def test_external_error_returns_generic_503_without_internal_details(self):
        secret = "postgresql://private-user:private-password@private-host/database"
        with mock.patch.object(
            server,
            "_open_readiness_connection",
            side_effect=sqlite3.OperationalError(secret),
        ):
            response = self.client.get("/api/readiness")
        self.assert_not_ready(response)
        body = response.get_data(as_text=True)
        self.assertNotIn("private", body)
        self.assertNotIn("users", body)
        self.assertNotIn("sqlite", body.lower())

    def test_sqlite_inspection_is_read_only_and_closes_explicitly(self):
        self.prepare_legacy_schema()
        statements = []
        opened = []
        original_connect = sqlite3.connect

        def tracked_connect(*args, **kwargs):
            wrapped = TrackingReadinessConnection(original_connect(*args, **kwargs), statements)
            opened.append(wrapped)
            return wrapped

        with mock.patch.object(server.sqlite3, "connect", side_effect=tracked_connect):
            response = self.client.get("/api/readiness")
        self.assert_ready(response)
        self.assertEqual(len(opened), 1)
        self.assertTrue(opened[0].closed)
        for sql, _ in statements:
            command = sql.split(None, 1)[0].upper()
            self.assertIn(command, {"SELECT", "PRAGMA"})
            self.assertNotIn("JOURNAL_MODE", sql.upper())

    def test_postgresql_valid_schema_is_read_only_and_closes(self):
        fake = FakePostgresReadinessConnection(version=server.REQUIRED_SCHEMA_VERSION)
        server.USE_POSTGRES = True
        server.DATABASE_URL = "postgresql://not-used"
        with mock.patch.object(server, "PgConnection", return_value=fake):
            response = self.client.get("/api/readiness")
        self.assert_ready(response)
        self.assertTrue(fake.conn.readonly)
        self.assertFalse(fake.conn.autocommit)
        self.assertTrue(fake.conn.rolled_back)
        self.assertTrue(fake.conn.closed)
        self.assertTrue(all(statement.startswith("select") for statement, _ in fake.statements))

    def test_postgresql_missing_schema_and_connection_error_return_503(self):
        server.USE_POSTGRES = True
        server.DATABASE_URL = "postgresql://not-used"
        missing = FakePostgresReadinessConnection(missing_table="users")
        with mock.patch.object(server, "PgConnection", return_value=missing):
            self.assert_not_ready(self.client.get("/api/readiness"))
        self.assertTrue(missing.conn.rolled_back)
        self.assertTrue(missing.conn.closed)

        with mock.patch.object(server, "PgConnection", side_effect=ImportError("driver unavailable")):
            self.assert_not_ready(self.client.get("/api/readiness"))


if __name__ == "__main__":
    unittest.main()
