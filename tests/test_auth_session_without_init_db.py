import gc
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from contextlib import contextmanager
from datetime import datetime, timezone
from unittest import mock

from environment_config import EnvironmentConfig
import server


class TrackingSQLiteConnection:
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


class FakePostgresCursor:
    def __init__(self, row):
        self.row = row

    def fetchone(self):
        return self.row


class FakePostgresConnection:
    def __init__(self, row):
        self.conn = FakePostgresDriverConnection()
        self.row = row
        self.statements = []

    def execute(self, sql, params=()):
        self.statements.append((server.translate_postgres_sql(sql), tuple(params or ())))
        return FakePostgresCursor(self.row)


class AuthSessionWithoutInitDbTest(unittest.TestCase):
    PASSWORD = "Auth-Session-Test-9"

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
        server.DB_PATH = os.path.join(self.temp_dir.name, "auth-session.db")
        server.DATABASE_URL = ""
        server.USE_POSTGRES = False
        server.ENVIRONMENT = EnvironmentConfig("development", "configured", False, False)
        server.app.config["TESTING"] = True
        server.LOGIN_ATTEMPTS.clear()
        os.environ["MOVA_ADMIN_PASSWORD"] = self.PASSWORD
        server.init_db()
        with server.connect_db() as connection:
            connection.executemany(
                """
                INSERT INTO users (id, store_id, name, login, password_hash, role, active, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    (
                        "operator-auth",
                        "matriz",
                        "Operador",
                        "operator-auth",
                        server.generate_password_hash(self.PASSWORD),
                        "operator",
                        1,
                        server.utc_now(),
                    ),
                    (
                        "inactive-auth",
                        "matriz",
                        "Inativo",
                        "inactive-auth",
                        server.generate_password_hash(self.PASSWORD),
                        "operator",
                        0,
                        server.utc_now(),
                    ),
                ),
            )
        self.client = server.app.test_client()

    def tearDown(self):
        server.DB_PATH = self.original["db_path"]
        server.DATABASE_URL = self.original["database_url"]
        server.USE_POSTGRES = self.original["use_postgres"]
        server.ENVIRONMENT = self.original["environment"]
        server.app.config["TESTING"] = self.original["testing"]
        server.LOGIN_ATTEMPTS.clear()
        if self.original["admin_password"] is None:
            os.environ.pop("MOVA_ADMIN_PASSWORD", None)
        else:
            os.environ["MOVA_ADMIN_PASSWORD"] = self.original["admin_password"]
        self.client = None
        gc.collect()
        self.temp_dir.cleanup()

    @contextmanager
    def structural_sentinels(self):
        forbidden = AssertionError("Fluxo de autenticacao executou inicializacao estrutural.")
        with (
            mock.patch.object(server, "init_db", side_effect=forbidden),
            mock.patch.object(server, "sync_business_tables", side_effect=forbidden),
            mock.patch.object(server, "create_initial_admin_user", side_effect=forbidden),
            mock.patch.object(server, "write_state", side_effect=forbidden),
        ):
            yield

    def authenticate(self, user_id="admin", role="admin"):
        with self.client.session_transaction() as flask_session:
            flask_session["user"] = {
                "id": user_id,
                "name": "Administrador" if role == "admin" else "Operador",
                "login": user_id,
                "role": role,
                "active": True,
            }

    def session_user(self):
        with self.client.session_transaction() as flask_session:
            return flask_session.get("user")

    def update_user(self, user_id, **values):
        columns = {"name", "login", "role", "active"}
        assignments = [f"{key} = ?" for key in values if key in columns]
        params = [values[key] for key in values if key in columns]
        with sqlite3.connect(server.DB_PATH) as connection:
            connection.execute(
                f"UPDATE users SET {', '.join(assignments)} WHERE id = ?",
                (*params, user_id),
            )

    def delete_user(self, user_id):
        with sqlite3.connect(server.DB_PATH) as connection:
            connection.execute("DELETE FROM users WHERE id = ?", (user_id,))

    def assert_unavailable(self, response):
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.get_json(), {
            "ok": False,
            "error": "Serviço temporariamente indisponível.",
        })

    def test_login_valid_and_invalid_credentials_never_initialize_structure(self):
        with self.structural_sentinels():
            valid = self.client.post("/api/login", json={"login": "admin", "password": self.PASSWORD})
            self.client.post("/api/logout")
            missing = self.client.post("/api/login", json={"login": "missing", "password": self.PASSWORD})
            wrong = self.client.post("/api/login", json={"login": "admin", "password": "wrong"})
            inactive = self.client.post("/api/login", json={"login": "inactive-auth", "password": self.PASSWORD})

        self.assertEqual(valid.status_code, 200)
        self.assertEqual(set(valid.get_json()["user"]), {"id", "name", "login", "role", "active"})
        for response in (missing, wrong, inactive):
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.get_json(), {"ok": False, "error": "Usuário ou senha inválidos."})
        with sqlite3.connect(server.DB_PATH) as connection:
            audit_count = connection.execute(
                "SELECT COUNT(*) FROM audit_logs WHERE action IN ('login', 'logout')"
            ).fetchone()[0]
        self.assertEqual(audit_count, 2)

    def test_login_payload_and_rate_limit_contracts_are_preserved(self):
        with self.structural_sentinels():
            incomplete = self.client.post("/api/login", json={"login": "admin"})
            with server.app.test_request_context(
                "/api/login",
                method="POST",
                environ_base={"REMOTE_ADDR": "127.0.0.1"},
            ):
                key = server.client_rate_key("admin")
            server.LOGIN_ATTEMPTS[key] = [datetime.now(timezone.utc)] * server.LOGIN_ATTEMPT_LIMIT
            limited = self.client.post("/api/login", json={"login": "admin", "password": self.PASSWORD})

        self.assertEqual(incomplete.status_code, 400)
        self.assertEqual(incomplete.get_json()["error"], "Informe usuário e senha.")
        self.assertEqual(limited.status_code, 429)
        self.assertIn("Muitas tentativas", limited.get_json()["error"])

    def test_session_and_protected_api_use_only_authentication_read(self):
        self.authenticate()
        with self.structural_sentinels():
            current = self.client.get("/api/session")
            protected = self.client.post("/api/cash-movements", json=[])

        self.assertEqual(current.status_code, 200)
        self.assertEqual(current.get_json()["user"]["id"], "admin")
        self.assertIn("dataImportReset", current.get_json()["capabilities"])
        self.assertEqual(protected.status_code, 400)

    def test_requests_without_session_do_not_open_authentication_database(self):
        with (
            self.structural_sentinels(),
            mock.patch.object(
                server,
                "_open_auth_read_connection",
                side_effect=AssertionError("Banco acessado sem sessao."),
            ),
        ):
            current = self.client.get("/api/session")
            protected = self.client.post("/api/cash-movements", json=[])
            logout = self.client.post("/api/logout")

        self.assertEqual(current.status_code, 200)
        self.assertIsNone(current.get_json()["user"])
        self.assertEqual(protected.status_code, 401)
        self.assertEqual(protected.get_json(), {"ok": False, "error": "Login obrigatório."})
        self.assertEqual(logout.status_code, 200)

    def test_removed_and_inactive_users_clear_session_in_protected_api(self):
        for user_id, mutate in (
            ("operator-auth", lambda: self.delete_user("operator-auth")),
            ("admin", lambda: self.update_user("admin", active=0)),
        ):
            with self.subTest(user_id=user_id):
                if user_id == "operator-auth":
                    self.authenticate(user_id, "operator")
                else:
                    self.authenticate()
                mutate()
                with self.structural_sentinels():
                    response = self.client.post("/api/cash-movements", json=[])
                self.assertEqual(response.status_code, 401)
                self.assertEqual(response.get_json(), {
                    "ok": False,
                    "error": "Sessao expirada. Faca login novamente.",
                })
                self.assertIsNone(self.session_user())

    def test_name_login_and_role_changes_replace_session_snapshot(self):
        self.authenticate()
        self.update_user("admin", name="Nome Atualizado", login="login-atualizado", role="operator")

        with self.structural_sentinels():
            response = self.client.get("/api/session")

        self.assertEqual(response.status_code, 200)
        expected = {
            "id": "admin",
            "name": "Nome Atualizado",
            "login": "login-atualizado",
            "role": "operator",
            "active": True,
        }
        self.assertEqual(response.get_json()["user"], expected)
        self.assertEqual(self.session_user(), expected)
        self.assertNotIn("password", self.session_user())
        self.assertNotIn("password_hash", self.session_user())

    def test_session_returns_null_for_removed_and_inactive_users(self):
        for user_id, role, mutate in (
            ("operator-auth", "operator", lambda: self.delete_user("operator-auth")),
            ("admin", "admin", lambda: self.update_user("admin", active=0)),
        ):
            with self.subTest(user_id=user_id):
                self.authenticate(user_id, role)
                mutate()
                with self.structural_sentinels():
                    response = self.client.get("/api/session")
                self.assertEqual(response.status_code, 200)
                self.assertIsNone(response.get_json()["user"])
                self.assertIsNone(self.session_user())

    def test_operational_failure_returns_503_without_clearing_existing_session(self):
        with (
            self.structural_sentinels(),
            mock.patch.object(
                server,
                "fetch_auth_user_by_login",
                side_effect=server.AuthenticationDatabaseUnavailable(),
            ),
        ):
            login = self.client.post("/api/login", json={"login": "admin", "password": self.PASSWORD})
        self.assert_unavailable(login)
        self.assertIsNone(self.session_user())

        for path in ("/api/session", "/api/cash-movements"):
            with self.subTest(path=path):
                self.authenticate()
                with (
                    self.structural_sentinels(),
                    mock.patch.object(
                        server,
                        "fetch_auth_user_by_id",
                        side_effect=server.AuthenticationDatabaseUnavailable(),
                    ),
                ):
                    response = self.client.get(path) if path == "/api/session" else self.client.post(path, json=[])
                self.assert_unavailable(response)
                self.assertEqual(self.session_user()["id"], "admin")

    def test_missing_users_table_returns_503_without_creating_schema(self):
        missing_path = os.path.join(self.temp_dir.name, "missing-users.db")
        with sqlite3.connect(missing_path) as connection:
            connection.execute("CREATE TABLE unrelated (id TEXT PRIMARY KEY)")
        server.DB_PATH = missing_path

        with self.structural_sentinels():
            response = self.client.post("/api/login", json={"login": "admin", "password": self.PASSWORD})

        self.assert_unavailable(response)
        with sqlite3.connect(missing_path) as connection:
            tables = {
                row[0]
                for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
            }
        self.assertEqual(tables, {"unrelated"})

    def test_missing_sqlite_database_returns_503_without_creating_file(self):
        missing_path = os.path.join(self.temp_dir.name, "database-does-not-exist.db")
        server.DB_PATH = missing_path

        with self.structural_sentinels():
            response = self.client.post("/api/login", json={"login": "admin", "password": self.PASSWORD})

        self.assert_unavailable(response)
        self.assertFalse(Path(missing_path).exists())

    def test_empty_users_table_returns_credential_error_without_bootstrap(self):
        with sqlite3.connect(server.DB_PATH) as connection:
            connection.execute("DELETE FROM users")

        with self.structural_sentinels():
            response = self.client.post("/api/login", json={"login": "admin", "password": self.PASSWORD})

        self.assertEqual(response.status_code, 401)
        with sqlite3.connect(server.DB_PATH) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM users").fetchone()[0], 0)

    def test_operator_permissions_and_capabilities_are_preserved(self):
        self.authenticate("operator-auth", "operator")
        with self.structural_sentinels():
            allowed = self.client.post("/api/payables", json=[])
            denied = self.client.get("/api/backups")
            current = self.client.get("/api/session")

        self.assertEqual(allowed.status_code, 400)
        self.assertEqual(denied.status_code, 403)
        self.assertEqual(denied.get_json(), {
            "ok": False,
            "error": "Apenas administrador pode realizar esta ação.",
        })
        self.assertFalse(current.get_json()["capabilities"]["dataImportReset"])

    def test_logout_preserves_contract_audit_and_never_calls_init_db(self):
        self.authenticate()
        with self.structural_sentinels():
            response = self.client.post("/api/logout")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "ok": True,
            "capabilities": {"dataImportReset": False},
        })
        self.assertIsNone(self.session_user())
        with sqlite3.connect(server.DB_PATH) as connection:
            audit_count = connection.execute(
                "SELECT COUNT(*) FROM audit_logs WHERE action = 'logout'"
            ).fetchone()[0]
        self.assertEqual(audit_count, 1)

    def test_sqlite_helper_is_read_only_and_closes_connection_explicitly(self):
        statements = []
        trackers = []
        original_connect = sqlite3.connect

        def tracking_connect(*args, **kwargs):
            tracker = TrackingSQLiteConnection(original_connect(*args, **kwargs), statements)
            trackers.append(tracker)
            return tracker

        with mock.patch.object(server.sqlite3, "connect", side_effect=tracking_connect):
            row = server.fetch_auth_user_by_login("admin")

        self.assertEqual(row["id"], "admin")
        self.assertEqual(len(trackers), 1)
        self.assertTrue(trackers[0].closed)
        self.assertTrue(statements)
        for sql, _params in statements:
            command = sql.split(None, 1)[0].upper()
            self.assertEqual(command, "SELECT")
            self.assertNotIn("PRAGMA JOURNAL_MODE", sql.upper())

    def test_postgres_helper_uses_translated_select_and_rolls_back_before_close(self):
        row = {
            "id": "admin",
            "name": "Administrador",
            "login": "admin",
            "password_hash": "not-used",
            "role": "admin",
            "active": 1,
        }
        fake = FakePostgresConnection(row)
        with (
            mock.patch.object(server, "USE_POSTGRES", True),
            mock.patch.object(server, "DATABASE_URL", "postgresql://not-used"),
            mock.patch.object(server, "PgConnection", return_value=fake),
        ):
            result = server.fetch_auth_user_by_login("admin")

        self.assertEqual(result, row)
        self.assertEqual(len(fake.statements), 1)
        self.assertIn("%s", fake.statements[0][0])
        self.assertEqual(fake.statements[0][1], ("matriz", "admin"))
        self.assertTrue(fake.conn.readonly)
        self.assertFalse(fake.conn.autocommit)
        self.assertTrue(fake.conn.rolled_back)
        self.assertTrue(fake.conn.closed)

    def test_postgres_operational_error_is_converted_to_generic_503(self):
        class SimulatedPostgresOperationalError(Exception):
            pass

        fake = FakePostgresConnection(None)
        fake.execute = mock.Mock(side_effect=SimulatedPostgresOperationalError("sensitive-driver-detail"))
        with (
            mock.patch.object(server, "USE_POSTGRES", True),
            mock.patch.object(server, "DATABASE_URL", "postgresql://not-used"),
            mock.patch.object(server, "PgConnection", return_value=fake),
            mock.patch.object(
                server,
                "_is_auth_database_error",
                side_effect=lambda error: isinstance(error, SimulatedPostgresOperationalError),
            ),
            self.structural_sentinels(),
        ):
            response = self.client.post("/api/login", json={"login": "admin", "password": self.PASSWORD})

        self.assert_unavailable(response)
        self.assertTrue(fake.conn.rolled_back)
        self.assertTrue(fake.conn.closed)


if __name__ == "__main__":
    unittest.main()
