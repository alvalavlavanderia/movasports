from __future__ import annotations

import importlib
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

from werkzeug.security import check_password_hash

from database_bootstrap.adapters import BootstrapSQLiteAdapter
from database_bootstrap.models import BootstrapError
from database_bootstrap.runner import (
    get_bootstrap_status,
    require_bootstrap_authorization,
    run_database_bootstrap,
    validate_bootstrap_credentials,
)
from database_bootstrap.validation import EMPTY_APP_STATE, _component_status
from database_migrations.registry import MIGRATIONS
from database_migrations.runner import run_database_migrations


class BootstrapSQLiteCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.temp.name) / "bootstrap.db")
        self.env = {
            "APP_ENV": "development",
            "MOVA_ALLOW_MIGRATIONS": "true",
            "MOVA_ALLOW_BOOTSTRAP": "true",
            "BOOTSTRAP_PASSWORD": "Strong-123",
        }

    def tearDown(self):
        self.temp.cleanup()

    def migrate(self):
        return run_database_migrations(
            environ=self.env,
            sqlite_path=self.db_path,
            create_database=True,
        )

    def bootstrap(self, **overrides):
        values = {
            "store_name": "Loja Matriz",
            "admin_name": "Administrador",
            "admin_login": "admin",
            "admin_password_env": "BOOTSTRAP_PASSWORD",
            "confirm_bootstrap": True,
            "environ": self.env,
            "sqlite_path": self.db_path,
        }
        values.update(overrides)
        return run_database_bootstrap(**values)

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def scalar(self, sql, params=()):
        with self.connect() as connection:
            return connection.execute(sql, params).fetchone()[0]


class ImportIsolationTests(BootstrapSQLiteCase):
    def test_import_package_does_not_open_database(self):
        import database_bootstrap

        with mock.patch("sqlite3.connect", side_effect=AssertionError("connection opened")):
            importlib.reload(database_bootstrap)

    def test_import_package_does_not_execute_sql(self):
        import database_bootstrap.runner

        source = Path(database_bootstrap.runner.__file__).read_text(encoding="utf-8")
        self.assertNotIn("run_database_bootstrap()", source)

    def test_server_does_not_import_bootstrap(self):
        source = Path("server.py").read_text(encoding="utf-8")
        self.assertNotIn("database_bootstrap", source)

    def test_wsgi_does_not_import_bootstrap(self):
        source = Path("wsgi.py").read_text(encoding="utf-8")
        self.assertNotIn("database_bootstrap", source)

    def test_no_http_bootstrap_endpoint(self):
        source = Path("server.py").read_text(encoding="utf-8")
        self.assertNotIn("/api/bootstrap", source)
        self.assertNotIn("/api/admin/bootstrap", source)

    def test_runner_has_no_forbidden_runtime_calls(self):
        source = Path("database_bootstrap/runner.py").read_text(encoding="utf-8")
        for forbidden in (
            "init_db(",
            "write_state(",
            "sync_business_tables(",
            "create_initial_admin_user(",
            "run_database_migrations(",
        ):
            self.assertNotIn(forbidden, source)

    def test_runner_has_no_ddl(self):
        sources = "\n".join(
            path.read_text(encoding="utf-8")
            for path in Path("database_bootstrap").glob("*.py")
        ).upper()
        for ddl in ("CREATE TABLE", "ALTER TABLE", "CREATE INDEX", "DROP TABLE"):
            self.assertNotIn(ddl, sources)


class RuntimeIsolationTests(BootstrapSQLiteCase):
    def setUp(self):
        super().setUp()
        self.migrate()
        self.bootstrap()

    def runtime_probe(self, action):
        environment = os.environ.copy()
        environment.pop("DATABASE_URL", None)
        environment.pop("MOVA_ADMIN_PASSWORD", None)
        environment.update({
            "APP_ENV": "development",
            "MOVA_DB": self.db_path,
            "BOOTSTRAP_PASSWORD": self.env["BOOTSTRAP_PASSWORD"],
        })
        probe = """
import os
import sys
import database_bootstrap.runner as bootstrap_runner

def forbidden_bootstrap(*args, **kwargs):
    raise AssertionError("runtime attempted explicit bootstrap")

bootstrap_runner.run_database_bootstrap = forbidden_bootstrap
import server

action = sys.argv[1]
if action == "health":
    response = server.app.test_client().get("/api/health")
    assert response.status_code == 200
elif action == "readiness":
    response = server.app.test_client().get("/api/readiness")
    assert response.status_code == 200
elif action == "login":
    response = server.app.test_client().post(
        "/api/login",
        json={"login": "admin", "password": os.environ["BOOTSTRAP_PASSWORD"]},
    )
    assert response.status_code == 200
elif action == "normal":
    server.init_db()
elif action != "import":
    raise AssertionError("unknown runtime probe")
"""
        result = subprocess.run(
            [sys.executable, "-B", "-c", probe, action],
            cwd=Path.cwd(),
            env=environment,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_import_server_does_not_execute_bootstrap(self):
        self.runtime_probe("import")

    def test_health_does_not_execute_bootstrap(self):
        self.runtime_probe("health")

    def test_readiness_does_not_execute_bootstrap(self):
        self.runtime_probe("readiness")

    def test_login_does_not_execute_bootstrap(self):
        self.runtime_probe("login")

    def test_normal_application_execution_does_not_execute_bootstrap(self):
        self.runtime_probe("normal")


class BootstrapStatusTests(BootstrapSQLiteCase):
    def test_missing_database_is_reported_without_creation(self):
        status = get_bootstrap_status(environ=self.env, sqlite_path=self.db_path)
        self.assertEqual(status.state, "DATABASE_MISSING")
        self.assertFalse(Path(self.db_path).exists())

    def test_empty_database_does_not_receive_ddl(self):
        Path(self.db_path).touch()
        status = get_bootstrap_status(environ=self.env, sqlite_path=self.db_path)
        self.assertEqual(status.state, "SCHEMA_MIGRATIONS_MISSING")
        with self.connect() as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM sqlite_master").fetchone()[0], 0)

    def test_missing_history_is_reported(self):
        self.migrate()
        with self.connect() as connection:
            connection.execute("DROP TABLE schema_migrations")
        status = get_bootstrap_status(environ=self.env, sqlite_path=self.db_path)
        self.assertEqual(status.state, "SCHEMA_MIGRATIONS_MISSING")

    def test_checksum_mismatch_is_reported(self):
        self.migrate()
        with self.connect() as connection:
            connection.execute("UPDATE schema_migrations SET checksum = ?", ("0" * 64,))
        status = get_bootstrap_status(environ=self.env, sqlite_path=self.db_path)
        self.assertEqual(status.state, "MIGRATION_HISTORY_INVALID")

    def test_future_version_is_reported(self):
        self.migrate()
        with self.connect() as connection:
            migration = MIGRATIONS[-1]
            connection.execute(
                "INSERT INTO schema_migrations VALUES (?, ?, ?, ?, ?)",
                (
                    migration.version + 1,
                    "Future",
                    "2026-01-01T00:00:00Z",
                    "0" * 64,
                    0,
                ),
            )
        status = get_bootstrap_status(environ=self.env, sqlite_path=self.db_path)
        self.assertEqual(status.state, "SCHEMA_FUTURE")

    def test_version_gap_is_reported(self):
        self.migrate()
        with self.connect() as connection:
            connection.execute("DELETE FROM schema_migrations WHERE version = 2")
        status = get_bootstrap_status(environ=self.env, sqlite_path=self.db_path)
        self.assertEqual(status.state, "MIGRATION_HISTORY_INVALID")

    def test_invalid_schema_is_reported(self):
        self.migrate()
        with self.connect() as connection:
            connection.execute("DROP INDEX idx_payables_status")
        status = get_bootstrap_status(environ=self.env, sqlite_path=self.db_path)
        self.assertEqual(status.state, "SCHEMA_INVALID")

    def test_not_started_components(self):
        self.migrate()
        status = get_bootstrap_status(environ=self.env, sqlite_path=self.db_path)
        self.assertEqual(status.state, "BOOTSTRAP_NOT_STARTED")
        self.assertEqual(status.store, "STORE_MISSING")
        self.assertEqual(status.app_state, "APP_STATE_MISSING")
        self.assertEqual(status.admin, "ADMIN_MISSING")

    def test_partial_bootstrap_is_reported(self):
        self.migrate()
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO stores (id, name, created_at) VALUES (?, ?, ?)",
                ("matriz", "Existente", "2026-01-01T00:00:00Z"),
            )
        status = get_bootstrap_status(environ=self.env, sqlite_path=self.db_path)
        self.assertEqual(status.state, "BOOTSTRAP_PARTIAL")
        self.assertEqual(status.store, "STORE_PRESENT")

    def test_complete_bootstrap_is_reported(self):
        self.migrate()
        self.bootstrap()
        status = get_bootstrap_status(environ=self.env, sqlite_path=self.db_path)
        self.assertTrue(status.ok)
        self.assertEqual(status.state, "BOOTSTRAP_COMPLETE")

    def test_invalid_app_state_is_reported(self):
        self.migrate()
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO app_state (id, data, updated_at) VALUES (1, ?, ?)",
                ("not-json", "2026-01-01T00:00:00Z"),
            )
        status = get_bootstrap_status(environ=self.env, sqlite_path=self.db_path)
        self.assertEqual(status.app_state, "APP_STATE_INVALID")
        self.assertFalse(status.ok)

    def test_inactive_admin_is_reported(self):
        self.migrate()
        self.bootstrap()
        with self.connect() as connection:
            connection.execute("UPDATE users SET active = 0 WHERE id = 'admin'")
        status = get_bootstrap_status(environ=self.env, sqlite_path=self.db_path)
        self.assertEqual(status.admin, "ADMIN_INACTIVE")

    def test_status_closes_sqlite_connection(self):
        self.migrate()
        get_bootstrap_status(environ=self.env, sqlite_path=self.db_path)
        renamed = Path(self.temp.name) / "renamed.db"
        Path(self.db_path).rename(renamed)
        self.assertTrue(renamed.exists())


class ExistingAdministratorHashTests(unittest.TestCase):
    def admin_status(self, password_hash=...):
        adapter = mock.Mock()
        adapter.fetch_stores.return_value = [{
            "id": "matriz",
            "name": "Matriz",
            "created_at": "2026-01-01T00:00:00Z",
        }]
        adapter.fetch_app_states.return_value = [{
            "id": 1,
            "data": json.dumps(EMPTY_APP_STATE),
            "updated_at": "2026-01-01T00:00:00Z",
        }]
        admin = {
            "id": "admin",
            "store_id": "matriz",
            "name": "Administrador",
            "login": "admin",
            "role": "admin",
            "active": True,
            "updated_at": "2026-01-01T00:00:00Z",
        }
        if password_hash is not ...:
            admin["password_hash"] = password_hash
        adapter.fetch_users.return_value = [admin]
        overall, _, _, admin_state, errors = _component_status(adapter)
        return overall, admin_state, errors

    def assert_invalid_hash(self, value=...):
        overall, admin_state, errors = self.admin_status(value)
        self.assertEqual(overall, "ADMIN_PASSWORD_HASH_INVALID")
        self.assertEqual(admin_state, "ADMIN_PASSWORD_HASH_INVALID")
        self.assertIn("ADMIN_PASSWORD_HASH_INVALID", errors)
        self.assertNotEqual(overall, "BOOTSTRAP_COMPLETE")

    def test_existing_admin_without_password_hash_is_inconsistent(self):
        self.assert_invalid_hash()

    def test_existing_admin_with_null_password_hash_is_inconsistent(self):
        self.assert_invalid_hash(None)

    def test_existing_admin_with_empty_password_hash_is_inconsistent(self):
        self.assert_invalid_hash("")

    def test_existing_admin_with_spaces_only_password_hash_is_inconsistent(self):
        self.assert_invalid_hash("        ")

    def test_existing_admin_with_clearly_invalid_password_hash_is_inconsistent(self):
        self.assert_invalid_hash("clearly-invalid")


class BootstrapAuthorizationTests(BootstrapSQLiteCase):
    def test_missing_confirmation_is_blocked(self):
        with self.assertRaisesRegex(BootstrapError, "confirmacao"):
            require_bootstrap_authorization(self.env, confirm_bootstrap=False, confirm_production=False)

    def test_missing_flag_is_blocked(self):
        env = {"APP_ENV": "development"}
        with self.assertRaises(BootstrapError) as context:
            require_bootstrap_authorization(env, confirm_bootstrap=True, confirm_production=False)
        self.assertEqual(context.exception.code, "bootstrap_not_allowed")

    def test_false_values_are_blocked(self):
        for value in ("", "0", "false", "no", "off"):
            with self.subTest(value=value), self.assertRaises(BootstrapError):
                require_bootstrap_authorization(
                    {"APP_ENV": "development", "MOVA_ALLOW_BOOTSTRAP": value},
                    confirm_bootstrap=True,
                    confirm_production=False,
                )

    def test_unknown_flag_is_blocked(self):
        with self.assertRaises(BootstrapError):
            require_bootstrap_authorization(
                {"APP_ENV": "development", "MOVA_ALLOW_BOOTSTRAP": "maybe"},
                confirm_bootstrap=True,
                confirm_production=False,
            )

    def test_true_values_are_accepted(self):
        for value in ("1", "true", "yes", "on", " TRUE "):
            with self.subTest(value=value):
                result = require_bootstrap_authorization(
                    {"APP_ENV": "development", "MOVA_ALLOW_BOOTSTRAP": value},
                    confirm_bootstrap=True,
                    confirm_production=False,
                )
                self.assertEqual(result, "development")

    def test_invalid_environment_is_blocked(self):
        with self.assertRaises(BootstrapError) as context:
            require_bootstrap_authorization(
                {"APP_ENV": "unknown", "MOVA_ALLOW_BOOTSTRAP": "true"},
                confirm_bootstrap=True,
                confirm_production=True,
            )
        self.assertEqual(context.exception.code, "environment_not_configured")

    def test_production_requires_additional_confirmation(self):
        env = {"APP_ENV": "production", "MOVA_ALLOW_BOOTSTRAP": "true"}
        with self.assertRaises(BootstrapError) as context:
            require_bootstrap_authorization(env, confirm_bootstrap=True, confirm_production=False)
        self.assertEqual(context.exception.code, "production_confirmation_required")

    def test_production_with_all_confirmations_is_accepted(self):
        env = {"APP_ENV": "production", "MOVA_ALLOW_BOOTSTRAP": "true"}
        self.assertEqual(
            require_bootstrap_authorization(env, confirm_bootstrap=True, confirm_production=True),
            "production",
        )

    def test_migration_flag_does_not_authorize_bootstrap(self):
        env = {"APP_ENV": "development", "MOVA_ALLOW_MIGRATIONS": "true"}
        with self.assertRaises(BootstrapError):
            require_bootstrap_authorization(env, confirm_bootstrap=True, confirm_production=False)

    def test_status_does_not_require_write_authorization(self):
        self.migrate()
        env = {"APP_ENV": "development", "MOVA_DB": self.db_path}
        self.assertEqual(get_bootstrap_status(environ=env).state, "BOOTSTRAP_NOT_STARTED")


class BootstrapCredentialTests(BootstrapSQLiteCase):
    def validate(self, **changes):
        values = {
            "store_name": "Matriz",
            "admin_name": "Administrador",
            "admin_login": "admin",
            "password_env": "BOOTSTRAP_PASSWORD",
            "environ": self.env,
        }
        values.update(changes)
        return validate_bootstrap_credentials(**values)

    def test_store_name_is_required(self):
        with self.assertRaises(BootstrapError):
            self.validate(store_name=" ")

    def test_admin_name_is_required(self):
        with self.assertRaises(BootstrapError):
            self.validate(admin_name="")

    def test_admin_login_is_required(self):
        with self.assertRaises(BootstrapError):
            self.validate(admin_login="")

    def test_password_environment_name_is_required(self):
        with self.assertRaises(BootstrapError):
            self.validate(password_env="")

    def test_password_environment_name_is_validated(self):
        with self.assertRaises(BootstrapError):
            self.validate(password_env="BAD-NAME")

    def test_password_environment_must_exist(self):
        with self.assertRaises(BootstrapError) as context:
            self.validate(password_env="MISSING_PASSWORD")
        self.assertEqual(context.exception.code, "password_missing")

    def test_password_must_have_eight_characters(self):
        env = {**self.env, "SHORT": "a1-234"}
        with self.assertRaises(BootstrapError):
            self.validate(password_env="SHORT", environ=env)

    def test_password_cannot_contain_only_spaces(self):
        env = {**self.env, "SPACES": "        "}
        with self.assertRaises(BootstrapError) as context:
            self.validate(password_env="SPACES", environ=env)
        self.assertEqual(context.exception.code, "password_missing")

    def test_password_length_ignores_outer_spaces(self):
        env = {**self.env, "PADDED_SHORT": "  123456  "}
        with self.assertRaises(BootstrapError) as context:
            self.validate(password_env="PADDED_SHORT", environ=env)
        self.assertEqual(context.exception.code, "password_too_short")

    def test_password_with_outer_spaces_is_preserved(self):
        password = "  Strong-123  "
        env = {**self.env, "PADDED": password}
        self.assertEqual(self.validate(password_env="PADDED", environ=env), password)

    def test_password_cannot_match_login(self):
        env = {**self.env, "SAME": "administrator"}
        with self.assertRaises(BootstrapError):
            self.validate(admin_login="Administrator", password_env="SAME", environ=env)

    def test_valid_password_is_returned_only_internally(self):
        self.assertEqual(self.validate(), "Strong-123")


class BootstrapRunTests(BootstrapSQLiteCase):
    def setUp(self):
        super().setUp()
        self.migrate()

    def test_run_creates_all_components(self):
        result = self.bootstrap()
        self.assertTrue(result.store_created)
        self.assertTrue(result.app_state_created)
        self.assertTrue(result.admin_created)
        self.assertFalse(result.already_complete)
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM customers WHERE is_default = 1"), 1)

    def test_store_contract_is_preserved(self):
        self.bootstrap(store_name="Matriz Principal")
        with self.connect() as connection:
            row = connection.execute("SELECT id, name, created_at FROM stores").fetchone()
        self.assertEqual(row["id"], "matriz")
        self.assertEqual(row["name"], "Matriz Principal")
        self.assertTrue(str(row["created_at"]).endswith("Z"))

    def test_app_state_is_minimal_and_deterministic(self):
        self.bootstrap()
        with self.connect() as connection:
            row = connection.execute("SELECT id, data FROM app_state").fetchone()
        self.assertEqual(row["id"], 1)
        self.assertEqual(json.loads(row["data"]), EMPTY_APP_STATE)

    def test_app_state_has_no_credentials(self):
        self.bootstrap()
        with self.connect() as connection:
            raw = connection.execute("SELECT data FROM app_state").fetchone()[0]
        self.assertNotIn("password", raw.lower())
        self.assertNotIn("hash", raw.lower())

    def test_admin_contract_and_hash(self):
        self.bootstrap(admin_name="Primeiro Admin", admin_login="gestor")
        with self.connect() as connection:
            row = connection.execute("SELECT * FROM users").fetchone()
        self.assertEqual(row["id"], "admin")
        self.assertEqual(row["store_id"], "matriz")
        self.assertEqual(row["role"], "admin")
        self.assertEqual(row["active"], 1)
        self.assertEqual(row["name"], "Primeiro Admin")
        self.assertEqual(row["login"], "gestor")
        self.assertNotEqual(row["password_hash"], self.env["BOOTSTRAP_PASSWORD"])
        self.assertTrue(check_password_hash(row["password_hash"], self.env["BOOTSTRAP_PASSWORD"]))

    def test_plaintext_password_is_not_stored_anywhere(self):
        self.bootstrap()
        password = self.env["BOOTSTRAP_PASSWORD"]
        with self.connect() as connection:
            rows = connection.iterdump()
            dump = "\n".join(rows)
        self.assertNotIn(password, dump)

    def test_no_demo_or_business_seed_is_created(self):
        self.bootstrap()
        allowed = {
            "stores",
            "app_state",
            "users",
            "customers",
            "expense_categories",
            "schema_migrations",
        }
        with self.connect() as connection:
            tables = [
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
            ]
            counts = {
                table: connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
                for table in tables
            }
        self.assertFalse({table: count for table, count in counts.items() if table not in allowed and count})
        self.assertEqual(counts["customers"], 1)
        self.assertEqual(counts["expense_categories"], 15)

    def test_default_customer_is_protected_business_identity(self):
        self.bootstrap()
        with self.connect() as connection:
            row = connection.execute(
                """
                SELECT id, store_id, code, name, cpf, credit_limit, status, is_default
                FROM customers
                """
            ).fetchone()
        self.assertEqual(row["id"], "matriz:customer:default")
        self.assertEqual(row["store_id"], "matriz")
        self.assertEqual(row["code"], "PADRAO")
        self.assertEqual(row["name"], "Cliente padrao")
        self.assertEqual(row["cpf"], "")
        self.assertEqual(row["credit_limit"], 0)
        self.assertEqual(row["status"], "active")
        self.assertEqual(row["is_default"], 1)

    def test_migration_history_is_not_changed(self):
        before = self.scalar("SELECT COUNT(*) FROM schema_migrations")
        self.bootstrap()
        after = self.scalar("SELECT COUNT(*) FROM schema_migrations")
        self.assertEqual(before, after)

    def test_schema_sql_is_not_changed(self):
        with self.connect() as connection:
            before = connection.execute(
                "SELECT type, name, sql FROM sqlite_master ORDER BY type, name"
            ).fetchall()
        self.bootstrap()
        with self.connect() as connection:
            after = connection.execute(
                "SELECT type, name, sql FROM sqlite_master ORDER BY type, name"
            ).fetchall()
        self.assertEqual([tuple(row) for row in before], [tuple(row) for row in after])

    def test_second_run_is_idempotent(self):
        first = self.bootstrap()
        with self.connect() as connection:
            original = connection.execute(
                "SELECT s.name, u.name, u.login, u.password_hash FROM stores s JOIN users u ON u.store_id=s.id"
            ).fetchone()
        second = self.bootstrap(store_name="Nao Renomear", admin_name="Nao Alterar", admin_login="outro")
        with self.connect() as connection:
            current = connection.execute(
                "SELECT s.name, u.name, u.login, u.password_hash FROM stores s JOIN users u ON u.store_id=s.id"
            ).fetchone()
        self.assertFalse(first.already_complete)
        self.assertTrue(second.already_complete)
        self.assertEqual(tuple(original), tuple(current))
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM stores"), 1)
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM app_state"), 1)
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM users"), 1)

    def test_valid_bootstrap_remains_idempotent_with_hash_validation(self):
        first = self.bootstrap()
        original_hash = self.scalar("SELECT password_hash FROM users WHERE id = 'admin'")
        second = self.bootstrap()
        self.assertFalse(first.already_complete)
        self.assertTrue(second.already_complete)
        self.assertEqual(
            self.scalar("SELECT password_hash FROM users WHERE id = 'admin'"),
            original_hash,
        )

    def test_password_outer_spaces_are_preserved_in_hash(self):
        password = "  Strong-123  "
        environment = {**self.env, "PADDED_PASSWORD": password}
        result = self.bootstrap(
            environ=environment,
            admin_password_env="PADDED_PASSWORD",
        )
        stored_hash = self.scalar("SELECT password_hash FROM users WHERE id = 'admin'")
        self.assertTrue(result.admin_created)
        self.assertTrue(check_password_hash(stored_hash, password))
        self.assertFalse(check_password_hash(stored_hash, password.strip()))

    def test_partial_store_only_creates_missing_components(self):
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO stores VALUES (?, ?, ?)",
                ("matriz", "Existente", "2026-01-01T00:00:00Z"),
            )
        result = self.bootstrap(store_name="Ignorado")
        self.assertFalse(result.store_created)
        self.assertTrue(result.app_state_created)
        self.assertTrue(result.admin_created)
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM stores"), 1)

    def test_partial_store_and_state_only_create_admin(self):
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO stores VALUES (?, ?, ?)",
                ("matriz", "Existente", "2026-01-01T00:00:00Z"),
            )
            connection.execute(
                "INSERT INTO app_state VALUES (1, ?, ?)",
                (json.dumps({"existing": True}), "2026-01-01T00:00:00Z"),
            )
        result = self.bootstrap()
        self.assertFalse(result.store_created)
        self.assertFalse(result.app_state_created)
        self.assertTrue(result.admin_created)
        with self.connect() as connection:
            self.assertEqual(json.loads(connection.execute("SELECT data FROM app_state").fetchone()[0]), {"existing": True})

    def test_other_store_blocks_creation_of_matrix(self):
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO stores VALUES (?, ?, ?)",
                ("other", "Outra", "2026-01-01T00:00:00Z"),
            )
        with self.assertRaises(BootstrapError):
            self.bootstrap()
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM stores"), 1)
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM app_state"), 0)

    def test_operator_with_requested_login_is_not_promoted(self):
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO stores VALUES (?, ?, ?)",
                ("matriz", "Matriz", "2026-01-01T00:00:00Z"),
            )
            connection.execute(
                """
                INSERT INTO users (
                    id, store_id, name, login, password_hash, role, active, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                ("operator", "matriz", "Operador", "admin", "hash", "operator", 1, "2026-01-01T00:00:00Z"),
            )
        with self.assertRaises(BootstrapError) as context:
            self.bootstrap()
        self.assertEqual(context.exception.code, "admin_login_conflict")
        self.assertEqual(self.scalar("SELECT role FROM users WHERE id='operator'"), "operator")
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM app_state"), 0)

    def test_inactive_admin_is_not_reactivated(self):
        self.bootstrap()
        with self.connect() as connection:
            connection.execute("UPDATE users SET active=0 WHERE id='admin'")
        with self.assertRaises(BootstrapError):
            self.bootstrap()
        self.assertEqual(self.scalar("SELECT active FROM users WHERE id='admin'"), 0)

    def test_missing_database_is_refused(self):
        other = str(Path(self.temp.name) / "missing.db")
        with self.assertRaises(BootstrapError) as context:
            self.bootstrap(sqlite_path=other)
        self.assertEqual(context.exception.code, "database_missing")
        self.assertFalse(Path(other).exists())

    def test_invalid_schema_is_refused_without_repair(self):
        with self.connect() as connection:
            connection.execute("DROP INDEX idx_payables_status")
        with self.assertRaises(BootstrapError):
            self.bootstrap()
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM stores"), 0)

    def test_app_state_failure_rolls_back_store(self):
        with mock.patch.object(BootstrapSQLiteAdapter, "insert_app_state", side_effect=RuntimeError("failure")):
            with self.assertRaises(BootstrapError):
                self.bootstrap()
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM stores"), 0)
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM app_state"), 0)

    def test_admin_failure_rolls_back_store_and_state(self):
        with mock.patch.object(BootstrapSQLiteAdapter, "insert_admin", side_effect=RuntimeError("failure")):
            with self.assertRaises(BootstrapError):
                self.bootstrap()
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM stores"), 0)
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM app_state"), 0)
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM users"), 0)

    def test_adapter_is_closed_after_success(self):
        adapters = []

        def factory(target, *, readonly):
            from database_bootstrap.adapters import open_bootstrap_adapter

            adapter = open_bootstrap_adapter(target, readonly=readonly)
            adapters.append(adapter)
            return adapter

        self.bootstrap(adapter_factory=factory)
        self.assertTrue(adapters[0].closed)

    def test_adapter_is_closed_after_failure(self):
        adapters = []

        def factory(target, *, readonly):
            from database_bootstrap.adapters import open_bootstrap_adapter

            adapter = open_bootstrap_adapter(target, readonly=readonly)
            adapters.append(adapter)
            adapter.insert_admin = mock.Mock(side_effect=RuntimeError("failure"))
            return adapter

        with self.assertRaises(BootstrapError):
            self.bootstrap(adapter_factory=factory)
        self.assertTrue(adapters[0].closed)

    def test_result_does_not_expose_credentials(self):
        payload = json.dumps(self.bootstrap().to_dict())
        self.assertNotIn(self.env["BOOTSTRAP_PASSWORD"], payload)
        self.assertNotIn("password_hash", payload)

    def test_login_works_after_bootstrap(self):
        self.bootstrap()
        import server

        original_connect = server.connect_db

        @contextmanager
        def closed_connect():
            connection = original_connect()
            try:
                with connection:
                    yield connection
            finally:
                connection.close()

        with (
            mock.patch.object(server, "DB_PATH", self.db_path),
            mock.patch.object(server, "USE_POSTGRES", False),
            mock.patch.object(server, "connect_db", closed_connect),
        ):
            client = server.app.test_client()
            response = client.post("/api/login", json={"login": "admin", "password": "Strong-123"})
            self.assertEqual(response.status_code, 200)
            session_response = client.get("/api/session")
            self.assertEqual(session_response.status_code, 200)
            self.assertEqual(session_response.get_json()["user"]["role"], "admin")

    def test_wrong_password_is_rejected_after_bootstrap(self):
        self.bootstrap()
        import server

        original_connect = server.connect_db

        @contextmanager
        def closed_connect():
            connection = original_connect()
            try:
                with connection:
                    yield connection
            finally:
                connection.close()

        with (
            mock.patch.object(server, "DB_PATH", self.db_path),
            mock.patch.object(server, "USE_POSTGRES", False),
            mock.patch.object(server, "connect_db", closed_connect),
        ):
            response = server.app.test_client().post(
                "/api/login", json={"login": "admin", "password": "Wrong-123"}
            )
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
