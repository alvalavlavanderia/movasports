import gc
import io
import json
import logging
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest import mock

from environment_config import EnvironmentConfig, load_environment_config
import server


class FailOnReadStream(io.BytesIO):
    def read(self, *args, **kwargs):
        raise AssertionError("O arquivo bloqueado nao pode ser lido.")

    def readinto(self, *args, **kwargs):
        raise AssertionError("O arquivo bloqueado nao pode ser lido.")


class DataOperationPermissionTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_environment = server.ENVIRONMENT
        self.original_use_postgres = server.USE_POSTGRES
        self.original_database_url = server.DATABASE_URL
        self.original_db_path = server.DB_PATH
        server.USE_POSTGRES = False
        server.DATABASE_URL = ""
        server.DB_PATH = os.path.join(self.temp_dir.name, "permissions.db")
        server.ENVIRONMENT = self.environment("development", False)
        server.init_db()
        with server.connect_db() as conn:
            conn.executemany(
                """
                INSERT INTO users (id, store_id, name, login, password_hash, role, active, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    (
                        "admin",
                        "matriz",
                        "Administrador",
                        "admin",
                        "not-used",
                        "admin",
                        1,
                        server.utc_now(),
                    ),
                    (
                        "operator-test",
                        "matriz",
                        "Operador Teste",
                        "operator-test",
                        "not-used",
                        "operator",
                        1,
                        server.utc_now(),
                    ),
                ),
            )
        self.client = server.app.test_client()

    def tearDown(self):
        server.ENVIRONMENT = self.original_environment
        server.USE_POSTGRES = self.original_use_postgres
        server.DATABASE_URL = self.original_database_url
        server.DB_PATH = self.original_db_path
        self.client = None
        gc.collect()
        self.temp_dir.cleanup()

    @staticmethod
    def environment(name, allowed):
        status = "configured" if name else "missing"
        return EnvironmentConfig(name, status, False, allowed)

    def authenticate(self, role="admin"):
        user = {
            "id": "admin" if role == "admin" else "operator-test",
            "name": "Administrador" if role == "admin" else "Operador Teste",
            "login": "admin" if role == "admin" else "operator-test",
            "role": role,
            "active": True,
        }
        with self.client.session_transaction() as session:
            session["user"] = user

    def database_dump(self):
        with sqlite3.connect(server.DB_PATH) as conn:
            return "\n".join(conn.iterdump())

    def assert_safe_error(self, response, status):
        self.assertEqual(response.status_code, status)
        payload = response.get_json()
        self.assertEqual(set(payload), {"ok", "error"})
        serialized = json.dumps(payload).lower()
        for forbidden in (
            "app_env",
            "mova_allow_data_import_reset",
            "database_url",
            "postgresql://",
            "secret",
            "token",
        ):
            self.assertNotIn(forbidden, serialized)

    def test_unauthenticated_and_operator_keep_existing_error_contract(self):
        before = self.database_dump()
        unauthenticated = self.client.post("/api/reset", json={"confirmation": "ZERAR"})
        self.assert_safe_error(unauthenticated, 401)
        self.assertEqual(unauthenticated.get_json()["error"], "Login obrigatório.")

        self.authenticate("operator")
        operator = self.client.post("/api/reset", json={"confirmation": "ZERAR"})
        self.assert_safe_error(operator, 403)
        self.assertEqual(operator.get_json()["error"], "Apenas administrador pode realizar esta ação.")
        self.assertEqual(before, self.database_dump())

    def test_blocked_matrix_never_changes_data(self):
        cases = (
            ("development", False),
            ("production", False),
            ("production", True),
            (None, False),
        )
        for environment, allowed in cases:
            with self.subTest(environment=environment, allowed=allowed):
                server.ENVIRONMENT = self.environment(environment, allowed)
                self.authenticate("admin")
                before = self.database_dump()
                response = self.client.post("/api/reset", json={"confirmation": "ZERAR"})
                self.assert_safe_error(response, 403)
                self.assertEqual(before, self.database_dump())

        server.ENVIRONMENT = EnvironmentConfig(None, "invalid", False, False)
        self.authenticate("admin")
        before = self.database_dump()
        response = self.client.post("/api/reset", json={"confirmation": "ZERAR"})
        self.assert_safe_error(response, 403)
        self.assertEqual(before, self.database_dump())

    def test_block_occurs_before_payload_file_or_database_access(self):
        server.ENVIRONMENT = self.environment("development", False)
        self.authenticate("admin")
        stream = FailOnReadStream(b"--boundary\r\nsecret-content\r\n--boundary--\r\n")
        with (
            mock.patch.object(server, "init_db") as init_db,
            mock.patch.object(server, "connect_db") as connect_db,
            mock.patch.object(server, "read_state") as read_state,
            mock.patch.object(server, "write_state") as write_state,
            mock.patch.object(server, "reset_business_data") as reset_business_data,
            mock.patch.object(server, "record_audit") as record_audit,
            mock.patch("flask.wrappers.Request.get_json", side_effect=AssertionError("Payload lido")) as get_json,
        ):
            import_response = self.client.open(
                "/api/import",
                method="POST",
                input_stream=stream,
                content_type="multipart/form-data; boundary=boundary",
                content_length=stream.getbuffer().nbytes,
            )
            reset_response = self.client.post("/api/reset", data=b"sensitive-confirmation")

        self.assertEqual(import_response.status_code, 403)
        self.assertEqual(reset_response.status_code, 403)
        init_db.assert_not_called()
        connect_db.assert_not_called()
        read_state.assert_not_called()
        write_state.assert_not_called()
        reset_business_data.assert_not_called()
        record_audit.assert_not_called()
        get_json.assert_not_called()

    def test_blocked_log_contains_only_safe_operation_and_reason(self):
        server.ENVIRONMENT = self.environment("development", False)
        self.authenticate("admin")
        sensitive_values = (
            "private-file-name.json",
            "RESTAURAR-SENSITIVE",
            "customer-id-sensitive",
            "login-sensitive",
            "password-sensitive",
            "token-sensitive",
        )
        with self.assertLogs(server.app.logger.name, logging.WARNING) as captured:
            response = self.client.post(
                "/api/import",
                data={
                    "confirmation": sensitive_values[1],
                    "file": (io.BytesIO(" ".join(sensitive_values).encode()), sensitive_values[0]),
                },
            )

        self.assertEqual(response.status_code, 403)
        logs = " ".join(captured.output)
        self.assertIn("operation=import", logs)
        self.assertIn("reason=capability_disabled", logs)
        for sensitive in sensitive_values:
            self.assertNotIn(sensitive, logs)

    def test_admin_is_allowed_only_in_development_or_staging_with_flag(self):
        server.ENVIRONMENT = self.environment("development", True)
        self.authenticate("admin")
        development = self.client.post("/api/reset", json={"confirmation": "ZERAR"})
        self.assertEqual(development.status_code, 200)

        server.ENVIRONMENT = self.environment("staging", True)
        self.authenticate("admin")
        staging = self.client.post(
            "/api/import",
            json={"confirmation": "RESTAURAR", "payload": {}},
        )
        self.assertEqual(staging.status_code, 200)

    def test_session_capability_follows_real_user_and_is_cleared(self):
        server.ENVIRONMENT = self.environment("development", True)
        without_session = self.client.get("/api/session").get_json()
        self.assertFalse(without_session["capabilities"]["dataImportReset"])

        self.authenticate("admin")
        admin = self.client.get("/api/session").get_json()
        self.assertTrue(admin["capabilities"]["dataImportReset"])
        self.assertEqual(set(admin["capabilities"]), {"dataImportReset"})

        logout = self.client.post("/api/logout").get_json()
        self.assertFalse(logout["capabilities"]["dataImportReset"])
        after_logout = self.client.get("/api/session").get_json()
        self.assertFalse(after_logout["capabilities"]["dataImportReset"])

        self.authenticate("operator")
        operator = self.client.get("/api/session").get_json()
        self.assertFalse(operator["capabilities"]["dataImportReset"])

    def test_production_rejects_unexpected_flag_text_strictly(self):
        config = load_environment_config(
            {
                "APP_ENV": "production",
                "MOVA_ALLOW_DATA_IMPORT_RESET": "unexpected-enabled-value",
            },
            mock.Mock(spec=logging.Logger),
        )
        self.assertFalse(config.allow_data_import_reset)
        server.ENVIRONMENT = config
        self.authenticate("admin")
        response = self.client.post("/api/reset", json={"confirmation": "ZERAR"})
        self.assertEqual(response.status_code, 403)

    def test_documented_flag_values_are_parsed_strictly(self):
        for value in ("1", "true", "yes", "on"):
            with self.subTest(value=value):
                config = load_environment_config({
                    "APP_ENV": "development",
                    "MOVA_ALLOW_DATA_IMPORT_RESET": value,
                })
                self.assertTrue(config.allow_data_import_reset)
        for value in ("", "0", "false", "no", "off", "unexpected"):
            with self.subTest(value=value):
                config = load_environment_config({
                    "APP_ENV": "development",
                    "MOVA_ALLOW_DATA_IMPORT_RESET": value,
                }, mock.Mock(spec=logging.Logger))
                self.assertFalse(config.allow_data_import_reset)

    def test_frontend_hides_only_destructive_panels_and_clears_capability(self):
        root = Path(__file__).resolve().parents[1]
        html = (root / "index.html").read_text(encoding="utf-8")
        script = (root / "script.js").read_text(encoding="utf-8")

        self.assertIn('id="importDataPanel"', html)
        self.assertIn('id="resetDataPanel"', html)
        self.assertIn("if (els.importDataPanel) els.importDataPanel.hidden = !allowDataOperations", script)
        self.assertIn("if (els.resetDataPanel) els.resetDataPanel.hidden = !allowDataOperations", script)
        self.assertIn("dataImportReset: capabilities?.dataImportReset === true", script)
        self.assertIn("if (!BACKEND_ENABLED || !canImportOrResetData()) return", script)
        for function_name in ("login", "logout", "syncSessionFromServer", "handleUnauthorized"):
            marker = f"function {function_name}"
            start = script.index(marker)
            ends = [
                position for position in (
                    script.find("\nfunction ", start + len(marker)),
                    script.find("\nasync function ", start + len(marker)),
                ) if position >= 0
            ]
            end = min(ends) if ends else len(script)
            function_source = script[start:end if end >= 0 else len(script)]
            self.assertIn("clearSessionCapabilities();", function_source)
        self.assertNotIn("els.exportDataButton.hidden", script)
        self.assertNotIn("els.createBackupButton.hidden", script)


if __name__ == "__main__":
    unittest.main()
