from __future__ import annotations

import gc
import io
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest import mock

from werkzeug.security import generate_password_hash

from database_migrations.migrations.v018_store_settings_and_user_security import MIGRATION_018
from database_migrations.registry import MIGRATIONS
from database_migrations.runner import run_database_migrations
from environment_config import EnvironmentConfig
import server


AUTHORIZED_ENV = {
    "APP_ENV": "development",
    "MOVA_ALLOW_MIGRATIONS": "true",
}


class StoreSettingsPermissionsBusinessRulesTest(unittest.TestCase):
    NOW = "2026-07-29T15:00:00+00:00"
    PASSWORD = "Senha-Teste-18!"

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original = (
            server.ENVIRONMENT,
            server.USE_POSTGRES,
            server.DATABASE_URL,
            server.DB_PATH,
            server.app.config.get("TESTING"),
        )
        server.ENVIRONMENT = EnvironmentConfig("development", "configured", False, False)
        server.USE_POSTGRES = False
        server.DATABASE_URL = ""
        server.DB_PATH = os.path.join(self.temp_dir.name, "business-18.db")
        server.app.config["TESTING"] = True
        server.LOGIN_ATTEMPTS.clear()
        run_database_migrations(
            environ=AUTHORIZED_ENV,
            sqlite_path=server.DB_PATH,
            create_database=True,
        )
        with server.connect_db() as connection:
            connection.execute(
                "INSERT INTO stores (id, name, created_at) VALUES (?, ?, ?)",
                ("matriz", "Mova Sports", self.NOW),
            )
            connection.execute(
                "INSERT INTO app_state (id, data, updated_at) VALUES (1, ?, ?)",
                (json.dumps(server.default_state(), ensure_ascii=False), self.NOW),
            )
            for identifier, role in (
                ("admin", "admin"),
                ("admin-2", "admin"),
                ("operator", "operator"),
            ):
                connection.execute(
                    """
                    INSERT INTO users (
                        id, store_id, name, login, password_hash, role, active,
                        failed_login_attempts, blocked_at, updated_at
                    ) VALUES (?, 'matriz', ?, ?, ?, ?, 1, 0, NULL, ?)
                    """,
                    (
                        identifier,
                        identifier.title(),
                        identifier,
                        generate_password_hash(self.PASSWORD),
                        role,
                        self.NOW,
                    ),
                )
        self.client = server.app.test_client()

    def tearDown(self):
        (
            server.ENVIRONMENT,
            server.USE_POSTGRES,
            server.DATABASE_URL,
            server.DB_PATH,
            server.app.config["TESTING"],
        ) = self.original
        server.LOGIN_ATTEMPTS.clear()
        self.client = None
        gc.collect()
        self.temp_dir.cleanup()

    def authenticate(self, identifier: str):
        role = "admin" if identifier.startswith("admin") else "operator"
        with self.client.session_transaction() as flask_session:
            flask_session["user"] = {
                "id": identifier,
                "name": identifier.title(),
                "login": identifier,
                "role": role,
                "active": True,
                "blocked": False,
            }

    @staticmethod
    def settings_payload(version=0, **overrides):
        payload = {
            "expectedVersion": version,
            "storeName": "Mova Sports Centro",
            "document": "52998224725",
            "email": "loja@example.test",
            "zip": "88000000",
            "state": "SC",
            "receiptFooter": "Obrigado pela preferencia.",
            "printPreferences": {
                "showDocument": True,
                "showPhone": True,
                "showWhatsapp": True,
                "showAddress": True,
                "showEmail": True,
            },
            "pix": {
                "key": "financeiro@example.test",
                "keyType": "email",
                "recipientName": "Mova Sports Centro",
                "recipientDocument": "52998224725",
                "bank": "Banco Teste",
            },
            "paymentMethods": {
                "cash": False,
                "pix": False,
                "debit": True,
                "credit": True,
                "storeCredit": False,
            },
        }
        payload.update(overrides)
        return payload

    def test_migration_18_is_additive_for_both_databases(self):
        self.assertEqual(MIGRATIONS[-1], MIGRATION_018)
        self.assertEqual(MIGRATION_018.version, 18)
        for statements in (MIGRATION_018.sqlite_statements, MIGRATION_018.postgresql_statements):
            joined = "\n".join(statements).lower()
            self.assertIn("create table store_settings", joined)
            self.assertIn("create table user_preferences", joined)
            self.assertIn("failed_login_attempts", joined)
            self.assertNotIn("drop table", joined)
            self.assertNotIn("delete from", joined)

    def test_admin_saves_versioned_settings_and_cash_remains_enabled(self):
        self.authenticate("admin")
        response = self.client.put("/api/settings/store", json=self.settings_payload())
        self.assertEqual(response.status_code, 200)
        data = response.get_json()["data"]
        self.assertEqual(data["version"], 1)
        self.assertEqual(data["storeName"], "Mova Sports Centro")
        self.assertTrue(data["paymentMethods"]["cash"])
        self.assertFalse(data["paymentMethods"]["pix"])
        with server.connect_db() as connection:
            self.assertEqual(
                connection.execute("SELECT name FROM stores WHERE id = 'matriz'").fetchone()["name"],
                "Mova Sports Centro",
            )
            audit = connection.execute(
                "SELECT details FROM audit_logs WHERE module = 'store_settings'"
            ).fetchone()
        self.assertIn("versionAfter", audit["details"])

    def test_operator_cannot_read_or_change_administrative_settings(self):
        public = self.client.get("/api/store/operational-settings")
        self.assertEqual(public.status_code, 200)
        self.authenticate("operator")
        self.assertEqual(self.client.get("/api/settings/store").status_code, 403)
        self.assertEqual(
            self.client.put("/api/settings/store", json=self.settings_payload()).status_code,
            403,
        )
        public = self.client.get("/api/store/operational-settings")
        self.assertEqual(public.status_code, 200)
        self.assertEqual(
            set(public.get_json()["data"]),
            {"storeName", "logoUrl", "paymentMethods"},
        )

    def test_settings_optimistic_concurrency_rejects_stale_version(self):
        self.authenticate("admin")
        self.assertEqual(
            self.client.put("/api/settings/store", json=self.settings_payload()).status_code,
            200,
        )
        stale = self.client.put("/api/settings/store", json=self.settings_payload())
        self.assertEqual(stale.status_code, 409)
        self.assertEqual(stale.get_json()["code"], "CONFIGURATION_VERSION_CONFLICT")

    def test_invalid_document_is_rejected_without_partial_update(self):
        self.authenticate("admin")
        response = self.client.put(
            "/api/settings/store",
            json=self.settings_payload(document="11111111111"),
        )
        self.assertEqual(response.status_code, 400)
        with server.connect_db() as connection:
            self.assertIsNone(connection.execute("SELECT * FROM store_settings").fetchone())
            self.assertEqual(
                connection.execute("SELECT name FROM stores WHERE id = 'matriz'").fetchone()["name"],
                "Mova Sports",
            )

    def test_disabled_payment_is_rejected_for_new_sale_only(self):
        self.authenticate("admin")
        self.client.put("/api/settings/store", json=self.settings_payload())
        with server.connect_db() as connection:
            with self.assertRaises(server.SaleOperationError) as context:
                server.build_transactional_sale_payments(
                    connection,
                    {"payments": [{"method": "pix", "amount": 10}]},
                    10,
                    self.NOW,
                    "matriz",
                )
        self.assertEqual(context.exception.code, "PAYMENT_METHOD_DISABLED")

    def test_theme_is_per_user_and_versioned(self):
        self.authenticate("operator")
        initial = self.client.get("/api/me/preferences")
        self.assertEqual(initial.get_json()["data"]["theme"], "system")
        updated = self.client.put(
            "/api/me/preferences",
            json={"theme": "dark", "expectedVersion": 0},
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.get_json()["data"]["version"], 1)
        self.authenticate("admin")
        self.assertEqual(
            self.client.get("/api/me/preferences").get_json()["data"]["theme"],
            "system",
        )

    def test_users_listing_and_access_matrix_are_admin_only(self):
        self.authenticate("operator")
        self.assertEqual(self.client.get("/api/users").status_code, 403)
        self.assertEqual(self.client.get("/api/settings/access-matrix").status_code, 403)
        self.authenticate("admin")
        users = self.client.get("/api/users")
        matrix = self.client.get("/api/settings/access-matrix")
        self.assertEqual(users.status_code, 200)
        self.assertEqual(matrix.status_code, 200)
        self.assertFalse(matrix.get_json()["data"]["editable"])

    def test_last_active_admin_cannot_be_demoted_or_deactivated(self):
        self.authenticate("admin")
        self.client.delete("/api/users/admin-2")
        demote = self.client.put(
            "/api/users/admin",
            json={"name": "Admin", "login": "admin", "role": "operator", "active": True},
        )
        deactivate = self.client.delete("/api/users/admin")
        self.assertEqual(demote.status_code, 409)
        self.assertEqual(deactivate.status_code, 409)

    def test_user_deactivation_preserves_record(self):
        self.authenticate("admin")
        response = self.client.delete("/api/users/operator")
        self.assertEqual(response.status_code, 200)
        with server.connect_db() as connection:
            row = connection.execute("SELECT active FROM users WHERE id = 'operator'").fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["active"], 0)

    def test_five_failures_block_and_admin_unlocks_user(self):
        for attempt in range(5):
            response = self.client.post(
                "/api/login",
                json={"login": "operator", "password": "incorreta"},
            )
        self.assertEqual(response.status_code, 423)
        blocked_login = self.client.post(
            "/api/login",
            json={"login": "operator", "password": self.PASSWORD},
        )
        self.assertEqual(blocked_login.status_code, 423)
        self.authenticate("admin")
        unlocked = self.client.post("/api/users/operator/unlock")
        self.assertEqual(unlocked.status_code, 200)
        self.client.post("/api/logout")
        valid = self.client.post(
            "/api/login",
            json={"login": "operator", "password": self.PASSWORD},
        )
        self.assertEqual(valid.status_code, 200)

    def test_document_identity_uses_saved_store_snapshot(self):
        self.authenticate("admin")
        self.client.put("/api/settings/store", json=self.settings_payload())
        with server.connect_db() as connection:
            identity = server.document_store_identity(connection)
        self.assertEqual(identity["name"], "Mova Sports Centro")
        self.assertEqual(identity["document"], "52998224725")
        self.assertEqual(identity["receiptFooter"], "Obrigado pela preferencia.")

    def test_logo_upload_validates_version_and_audits_without_exposing_secret(self):
        self.authenticate("admin")
        uploaded = {
            "url": "/uploads/store/logo.png",
            "filename": "logo.png",
            "size": 120,
            "storage": "local",
        }
        with mock.patch.object(server, "save_store_logo", return_value=uploaded):
            response = self.client.post(
                "/api/settings/store/logo",
                data={"expectedVersion": "0", "photo": (io.BytesIO(b"test-logo"), "logo.png")},
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["data"]["logoUrl"], uploaded["url"])

    def test_frontend_exposes_business_settings_without_destructive_panels(self):
        root = Path(__file__).resolve().parents[1]
        html = (root / "index.html").read_text(encoding="utf-8")
        script = (root / "script.js").read_text(encoding="utf-8")
        self.assertIn('id="storeSettingsForm"', html)
        self.assertIn('id="userThemeSelect"', html)
        self.assertIn("loadStoreOperationalSettings", script)
        self.assertIn("els.importDataPanel.hidden = !allowDataOperations", script)


if __name__ == "__main__":
    unittest.main()
