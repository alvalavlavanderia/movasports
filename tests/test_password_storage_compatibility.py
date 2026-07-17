import gc
import io
import json
import logging
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest

from environment_config import EnvironmentConfig
import server


class CaptureHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.messages = []

    def emit(self, record):
        self.messages.append(self.format(record))


class PasswordStorageCompatibilityTest(unittest.TestCase):
    INITIAL_PASSWORD = "Initial-Test-Password-9"

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original = {
            "environment": server.ENVIRONMENT,
            "use_postgres": server.USE_POSTGRES,
            "database_url": server.DATABASE_URL,
            "db_path": server.DB_PATH,
            "admin_password": os.environ.get("MOVA_ADMIN_PASSWORD"),
        }
        server.ENVIRONMENT = EnvironmentConfig("development", "configured", False, True)
        server.USE_POSTGRES = False
        server.DATABASE_URL = ""
        server.DB_PATH = os.path.join(self.temp_dir.name, "passwords.db")
        os.environ["MOVA_ADMIN_PASSWORD"] = self.INITIAL_PASSWORD
        server.init_db()
        self.client = server.app.test_client()

    def tearDown(self):
        server.ENVIRONMENT = self.original["environment"]
        server.USE_POSTGRES = self.original["use_postgres"]
        server.DATABASE_URL = self.original["database_url"]
        server.DB_PATH = self.original["db_path"]
        if self.original["admin_password"] is None:
            os.environ.pop("MOVA_ADMIN_PASSWORD", None)
        else:
            os.environ["MOVA_ADMIN_PASSWORD"] = self.original["admin_password"]
        self.client = None
        gc.collect()
        self.temp_dir.cleanup()

    def authenticate_admin(self):
        with self.client.session_transaction() as session:
            session["user"] = {
                "id": "admin",
                "name": "Administrador",
                "login": "admin",
                "role": "admin",
                "active": True,
            }

    def raw_state(self):
        connection = sqlite3.connect(server.DB_PATH)
        try:
            row = connection.execute("SELECT data FROM app_state WHERE id = 1").fetchone()
            return json.loads(row[0])
        finally:
            connection.close()

    def user_hash(self, user_id="admin"):
        connection = sqlite3.connect(server.DB_PATH)
        try:
            row = connection.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,)).fetchone()
            return row[0] if row else None
        finally:
            connection.close()

    def set_raw_state(self, state):
        connection = sqlite3.connect(server.DB_PATH)
        try:
            connection.execute(
                "UPDATE app_state SET data = ?, updated_at = ? WHERE id = 1",
                (json.dumps(state, ensure_ascii=False), server.utc_now()),
            )
            connection.commit()
        finally:
            connection.close()

    def assert_no_credentials(self, value):
        if isinstance(value, dict):
            for key, item in value.items():
                self.assertNotIn(str(key).lower(), {"password", "password_hash"})
                self.assert_no_credentials(item)
        elif isinstance(value, list):
            for item in value:
                self.assert_no_credentials(item)

    def create_user(self, user_id="operator-1", password="Operator-Test-Password-8"):
        self.authenticate_admin()
        return self.client.post("/api/users", json={
            "id": user_id,
            "name": "Operador Teste",
            "login": user_id,
            "password": password,
            "role": "operator",
            "active": True,
        })

    def test_new_database_bootstraps_admin_hash_without_state_password(self):
        stored_hash = self.user_hash()
        self.assertTrue(server.password_hash_is_structurally_valid(stored_hash))
        self.assertTrue(server.password_matches(stored_hash, self.INITIAL_PASSWORD))
        self.assert_no_credentials(self.raw_state())

    def test_existing_login_preserves_exact_hash(self):
        before = self.user_hash()
        response = self.client.post("/api/login", json={"login": "admin", "password": self.INITIAL_PASSWORD})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(before, self.user_hash())
        self.assert_no_credentials(response.get_json())

    def test_create_user_hashes_password_without_state_or_log_exposure(self):
        password = "Create-Only-Password-7"
        handler = CaptureHandler()
        server.app.logger.addHandler(handler)
        try:
            response = self.create_user(password=password)
        finally:
            server.app.logger.removeHandler(handler)

        self.assertEqual(response.status_code, 201)
        stored_hash = self.user_hash("operator-1")
        self.assertTrue(server.password_matches(stored_hash, password))
        state_user = next(item for item in self.raw_state()["users"] if item["id"] == "operator-1")
        self.assert_no_credentials(state_user)
        self.assert_no_credentials(response.get_json())
        self.assertNotIn(password, " ".join(handler.messages))
        connection = sqlite3.connect(server.DB_PATH)
        try:
            details = " ".join(row[0] or "" for row in connection.execute(
                "SELECT details FROM audit_logs WHERE module = 'user'"
            ).fetchall())
        finally:
            connection.close()
        self.assertNotIn(password, details)

    def test_edit_without_password_or_with_profile_change_preserves_hash(self):
        self.assertEqual(self.create_user().status_code, 201)
        before = self.user_hash("operator-1")
        self.authenticate_admin()
        response = self.client.put("/api/users/operator-1", json={
            "name": "Nome Atualizado",
            "login": "operator-1",
            "role": "admin",
            "active": True,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(before, self.user_hash("operator-1"))
        self.assertEqual(response.get_json()["data"]["role"], "admin")
        self.assert_no_credentials(response.get_json())

    def test_explicit_password_change_updates_only_hash(self):
        before_state = self.raw_state()
        old_hash = self.user_hash()
        login = self.client.post("/api/login", json={"login": "admin", "password": self.INITIAL_PASSWORD})
        self.assertEqual(login.status_code, 200)
        new_password = "Changed-Test-Password-6"
        response = self.client.post("/api/me/password", json={
            "currentPassword": self.INITIAL_PASSWORD,
            "newPassword": new_password,
            "confirmPassword": new_password,
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(old_hash, self.user_hash())
        self.assertTrue(server.password_matches(self.user_hash(), new_password))
        self.assertEqual(before_state, self.raw_state())
        self.assert_no_credentials(response.get_json())

    def test_legacy_password_is_preserved_internally_but_never_returned(self):
        state = self.raw_state()
        state["users"][0]["password"] = "legacy-plain-secret"
        state["users"][0]["password_hash"] = "legacy-state-hash"
        self.set_raw_state(state)

        self.authenticate_admin()
        update = self.client.put("/api/users/admin", json={
            "name": "Administrador Atualizado",
            "login": "admin",
            "role": "admin",
            "active": True,
        })
        self.assertEqual(update.status_code, 200)
        raw_user = self.raw_state()["users"][0]
        self.assertEqual(raw_user["password"], "legacy-plain-secret")
        self.assertEqual(raw_user["password_hash"], "legacy-state-hash")

        state_response = self.client.get("/api/state").get_json()
        export_response = self.client.get("/api/export").get_json()
        self.assert_no_credentials(state_response)
        self.assert_no_credentials(export_response)
        serialized = json.dumps([state_response, export_response])
        self.assertNotIn("legacy-plain-secret", serialized)
        self.assertNotIn("legacy-state-hash", serialized)

    def test_generic_state_and_import_ignore_credentials_and_preserve_table_hash(self):
        original_hash = self.user_hash()
        state = self.raw_state()
        state["users"][0]["password"] = "existing-legacy-value"
        self.set_raw_state(state)
        self.authenticate_admin()

        put_response = self.client.put("/api/state", json={
            **server.default_state(),
            "users": [{
                "id": "admin",
                "login": "admin",
                "password": "injected-password",
                "password_hash": "injected-hash",
            }],
        })
        self.assertEqual(put_response.status_code, 200)
        self.assertEqual(original_hash, self.user_hash())
        self.assertEqual(self.raw_state()["users"][0]["password"], "existing-legacy-value")

        import_response = self.client.post("/api/import", json={
            "confirmation": "RESTAURAR",
            "payload": {
                "data": {
                    **server.default_state(),
                    "users": [{"id": "admin", "password": "imported-password"}],
                }
            },
        })
        self.assertEqual(import_response.status_code, 200)
        self.assertEqual(original_hash, self.user_hash())
        self.assertEqual(self.raw_state()["users"][0]["password"], "existing-legacy-value")

    def test_legacy_state_does_not_rebuild_empty_users_or_create_admin(self):
        legacy_path = os.path.join(self.temp_dir.name, "legacy.db")
        connection = sqlite3.connect(legacy_path)
        try:
            connection.execute(
                "CREATE TABLE app_state (id INTEGER PRIMARY KEY, data TEXT NOT NULL, updated_at TEXT NOT NULL)"
            )
            legacy_state = server.default_state()
            legacy_state["users"] = [{
                "id": "legacy-user",
                "name": "Usuario Legado",
                "login": "legacy-login",
                "password": "legacy-password",
                "role": "admin",
                "active": True,
            }]
            connection.execute(
                "INSERT INTO app_state (id, data, updated_at) VALUES (1, ?, ?)",
                (json.dumps(legacy_state), server.utc_now()),
            )
            connection.commit()
        finally:
            connection.close()

        server.DB_PATH = legacy_path
        with self.assertLogs(server.app.logger.name, logging.WARNING) as captured:
            server.init_db()
        connection = sqlite3.connect(legacy_path)
        try:
            total = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            raw = json.loads(connection.execute("SELECT data FROM app_state WHERE id = 1").fetchone()[0])
        finally:
            connection.close()
        self.assertEqual(total, 0)
        self.assertEqual(raw["users"][0]["password"], "legacy-password")
        logs = " ".join(captured.output)
        self.assertIn("Bootstrap de usuarios bloqueado", logs)
        self.assertNotIn("legacy-login", logs)
        self.assertNotIn("legacy-password", logs)

    def test_invalid_hash_blocks_login_without_repair_or_sensitive_log(self):
        connection = sqlite3.connect(server.DB_PATH)
        try:
            connection.execute("UPDATE users SET password_hash = 'invalid-hash' WHERE id = 'admin'")
            connection.commit()
        finally:
            connection.close()
        with self.assertLogs(server.app.logger.name, logging.WARNING) as captured:
            response = self.client.post("/api/login", json={
                "login": "admin",
                "password": "password-that-must-not-be-logged",
            })
        self.assertEqual(response.status_code, 401)
        self.assertEqual(self.user_hash(), "invalid-hash")
        logs = " ".join(captured.output)
        self.assertIn("password_hash valido", logs)
        self.assertNotIn("admin", logs)
        self.assertNotIn("invalid-hash", logs)
        self.assertNotIn("password-that-must-not-be-logged", logs)

    def test_all_user_and_session_responses_are_public(self):
        login = self.client.post("/api/login", json={"login": "admin", "password": self.INITIAL_PASSWORD})
        self.assertEqual(login.status_code, 200)
        responses = (
            login.get_json(),
            self.client.get("/api/session").get_json(),
            self.client.get("/api/users").get_json(),
            self.client.get("/api/state").get_json(),
            self.client.get("/api/export").get_json(),
        )
        for payload in responses:
            self.assert_no_credentials(payload)

    def test_frontend_requires_backend_and_never_persists_credentials(self):
        script = (Path(__file__).resolve().parents[1] / "script.js").read_text(encoding="utf-8")
        login_start = script.index("async function login")
        logout_start = script.index("async function logout", login_start)
        login_source = script[login_start:logout_start]

        self.assertIn("if (!BACKEND_ENABLED)", login_source)
        self.assertIn("showBackendRequiredMessage();", login_source)
        self.assertNotIn("db.users.find", login_source)
        self.assertNotIn("sessionStorage", script)
        self.assertNotIn('password: "1234"', script)
        self.assertIn("users: []", script)
        self.assertIn("users: Array.isArray(data.users) ? data.users.map(sanitizeUserForBrowser) : []", script)
        self.assertIn("db = browserSafeDb(db);", script)
        self.assertIn("O sistema precisa ser acessado pelo endereço oficial do servidor", script)
        self.assertIn("const loaded = JSON.parse(localStorage.getItem(STORAGE_KEY));", script)
        self.assertNotIn("localStorage.removeItem(STORAGE_KEY)", script)


if __name__ == "__main__":
    unittest.main()
