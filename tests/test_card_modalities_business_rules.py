from __future__ import annotations

import gc
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from flask import session

from database_migrations.migrations.v008_card_modalities import MIGRATION_008
from database_migrations.migrations.v009_card_modality_history import MIGRATION_009
from database_migrations.registry import MIGRATIONS
from database_migrations.runner import run_database_migrations
from environment_config import EnvironmentConfig
import server


AUTHORIZED_ENV = {
    "APP_ENV": "development",
    "MOVA_ALLOW_MIGRATIONS": "true",
}


class _PostgresPathOnSQLite:
    def __init__(self, path: str):
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.statements: list[str] = []

    def execute(self, sql, params=()):
        self.statements.append(sql)
        return self.connection.execute(sql.replace(" FOR UPDATE", ""), params)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        if exc_type:
            self.connection.rollback()
        else:
            self.connection.commit()
        self.connection.close()


class CardModalitiesBusinessRulesTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original = (
            server.ENVIRONMENT,
            server.USE_POSTGRES,
            server.DATABASE_URL,
            server.DB_PATH,
        )
        server.ENVIRONMENT = EnvironmentConfig(
            "development", "configured", False, False
        )
        server.USE_POSTGRES = False
        server.DATABASE_URL = ""
        server.DB_PATH = os.path.join(self.temp_dir.name, "card-modalities.db")
        run_database_migrations(
            environ=AUTHORIZED_ENV,
            sqlite_path=server.DB_PATH,
            create_database=True,
        )
        with server.connect_db() as connection:
            connection.execute(
                "INSERT INTO stores (id, name, created_at) VALUES (?, ?, ?)",
                ("matriz", "Matriz", "2026-07-25T10:00:00+00:00"),
            )
            for identifier, role in (("operator", "operator"), ("admin", "admin")):
                connection.execute(
                    """
                    INSERT INTO users (
                        id, store_id, name, login, password_hash,
                        role, active, updated_at
                    )
                    VALUES (?, 'matriz', ?, ?, 'not-used', ?, 1, ?)
                    """,
                    (
                        identifier,
                        identifier.title(),
                        identifier,
                        role,
                        "2026-07-25T10:00:00+00:00",
                    ),
                )
        self.client = server.app.test_client()

    def tearDown(self):
        (
            server.ENVIRONMENT,
            server.USE_POSTGRES,
            server.DATABASE_URL,
            server.DB_PATH,
        ) = self.original
        self.client = None
        gc.collect()
        self.temp_dir.cleanup()

    def authenticate(self, identifier: str):
        role = "admin" if identifier == "admin" else "operator"
        with self.client.session_transaction() as flask_session:
            flask_session["user"] = {
                "id": identifier,
                "name": identifier.title(),
                "login": identifier,
                "role": role,
                "active": True,
            }

    @staticmethod
    def payload(method="credit", installments=1, **overrides):
        data = {
            "method": method,
            "installments": installments,
            "taxPercent": 2.5,
            "receivableDays": 1,
            "validFrom": "2026-07-25T09:00:00-03:00",
            "validUntil": "",
            "status": "active",
        }
        data.update(overrides)
        return data

    def create_modality(self, **payload):
        response = self.client.post(
            "/api/card-modalities",
            json=self.payload(**payload),
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()["data"]

    def count(self, table: str) -> int:
        with sqlite3.connect(server.DB_PATH) as connection:
            return int(connection.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0])

    def test_migrations_are_registered_additive_and_cross_database(self):
        self.assertEqual([item.version for item in MIGRATIONS][-5:], [14, 15, 16, 17, 18])
        self.assertEqual(MIGRATION_008.version, 8)
        self.assertEqual(MIGRATION_009.version, 9)
        for migration in (MIGRATION_008, MIGRATION_009):
            self.assertTrue(migration.sqlite_statements)
            self.assertEqual(
                migration.sqlite_statements,
                migration.postgresql_statements,
            )
            self.assertFalse(any(
                statement.lstrip().upper().startswith(("DROP ", "DELETE "))
                for statement in migration.sqlite_statements
            ))
        with sqlite3.connect(server.DB_PATH) as connection:
            version = connection.execute(
                "SELECT MAX(version) FROM schema_migrations"
            ).fetchone()[0]
            tables = {
                row[0] for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
            indexes = {
                row[0] for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'index'"
                )
            }
        self.assertEqual(version, 18)
        self.assertIn("card_modalities", tables)
        self.assertIn("card_modality_history", tables)
        self.assertIn("idx_card_modalities_store_stable_id", indexes)

    def test_requires_authenticated_administrator(self):
        response = self.client.get("/api/card-modalities")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.get_json(),
            {"ok": False, "error": "Login obrigatório."},
        )

        self.authenticate("operator")
        response = self.client.post(
            "/api/card-modalities",
            json=self.payload(),
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.count("card_modalities"), 0)

    def test_supports_debit_and_credit_from_one_to_ten_installments(self):
        self.authenticate("admin")
        debit = self.create_modality(method="debit", installments=1)
        self.assertEqual(debit["name"], "Débito")
        for installments in range(1, 11):
            modality = self.create_modality(
                method="credit",
                installments=installments,
                taxPercent=installments / 10,
                receivableDays=installments,
            )
            self.assertEqual(modality["name"], f"Crédito {installments}x")
        self.assertEqual(self.count("card_modalities"), 11)
        self.assertEqual(self.count("audit_logs"), 11)

    def test_rejects_invalid_or_duplicate_configuration(self):
        self.authenticate("admin")
        self.create_modality(method="credit", installments=2)
        duplicate = self.client.post(
            "/api/card-modalities",
            json=self.payload(method="credit", installments=2),
        )
        self.assertEqual(duplicate.status_code, 409)

        invalid_payloads = (
            self.payload(method="debit", installments=2),
            self.payload(method="credit", installments=11),
            self.payload(method="credit", installments=1.5),
            self.payload(method="credit", taxPercent=-0.01),
            self.payload(method="credit", taxPercent="NaN"),
            self.payload(method="credit", receivableDays=-1),
            self.payload(method="credit", receivableDays=1.5),
            self.payload(
                method="credit",
                validFrom="2026-07-26T09:00:00-03:00",
                validUntil="2026-07-25T09:00:00-03:00",
            ),
        )
        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                response = self.client.post("/api/card-modalities", json=payload)
                self.assertEqual(response.status_code, 400, response.get_json())

    def test_update_and_status_changes_preserve_stable_history(self):
        self.authenticate("admin")
        created = self.create_modality(method="credit", installments=3)
        stable_id = created["cardModalityId"]

        response = self.client.put(
            f"/api/card-modalities/{stable_id}",
            json=self.payload(
                method="credit",
                installments=3,
                taxPercent=3.75,
                receivableDays=2,
                validFrom="2026-08-01T00:00:00-03:00",
            ),
        )
        self.assertEqual(response.status_code, 200, response.get_json())
        updated = response.get_json()["data"]
        self.assertEqual(updated["cardModalityId"], stable_id)
        self.assertEqual(updated["taxPercent"], 3.75)

        response = self.client.post(
            f"/api/card-modalities/{stable_id}/deactivate",
            json={"validFrom": "2026-09-01T00:00:00-03:00"},
        )
        self.assertEqual(response.status_code, 200, response.get_json())
        self.assertEqual(response.get_json()["data"]["status"], "inactive")

        response = self.client.post(
            f"/api/card-modalities/{stable_id}/activate",
            json={"validFrom": "2026-10-01T00:00:00-03:00"},
        )
        self.assertEqual(response.status_code, 200, response.get_json())
        self.assertEqual(response.get_json()["data"]["status"], "active")

        history = self.client.get(
            f"/api/card-modalities/{stable_id}/history"
        ).get_json()["data"]
        self.assertEqual(len(history), 4)
        self.assertTrue(all(
            item["cardModalityId"] == stable_id for item in history
        ))
        self.assertEqual(
            [item["status"] for item in history],
            ["active", "inactive", "active", "active"],
        )
        self.assertEqual(self.count("card_modality_history"), 3)
        self.assertEqual(self.count("audit_logs"), 4)

    def test_audit_failure_rolls_back_modality(self):
        self.authenticate("admin")
        with mock.patch.object(
            server,
            "record_audit",
            side_effect=RuntimeError("audit unavailable"),
        ):
            response = self.client.post(
                "/api/card-modalities",
                json=self.payload(method="credit", installments=4),
            )
        self.assertEqual(response.status_code, 500)
        self.assertEqual(self.count("card_modalities"), 0)
        self.assertEqual(self.count("audit_logs"), 0)

    def test_postgresql_path_uses_portable_queries(self):
        adapter = _PostgresPathOnSQLite(server.DB_PATH)
        with server.app.test_request_context(
            "/api/card-modalities",
            method="POST",
            json=self.payload(method="credit", installments=5),
        ):
            session["user"] = {
                "id": "admin",
                "name": "Admin",
                "login": "admin",
                "role": "admin",
                "active": True,
            }
            with mock.patch.object(server, "USE_POSTGRES", True), mock.patch.object(
                server,
                "connect_db",
                return_value=adapter,
            ):
                response, status_code = server.create_card_modality_api()
        self.assertEqual(status_code, 201, response.get_json())
        statements = "\n".join(adapter.statements)
        self.assertNotIn("COLLATE NOCASE", statements)
        self.assertIn("INSERT INTO card_modalities", statements)
        self.assertIn("INSERT INTO audit_logs", statements)
        self.assertEqual(self.count("card_modalities"), 1)

    def test_frontend_exposes_admin_screen_and_clears_loaded_session_data(self):
        project = Path(__file__).resolve().parents[1]
        html = (project / "index.html").read_text(encoding="utf-8")
        script = (project / "script.js").read_text(encoding="utf-8")
        self.assertIn('id="cad-modalidade" class="subtab-panel admin-only"', html)
        self.assertIn('fetch("/api/card-modalities"', script)
        clear_start = script.index("function clearSessionCapabilities()")
        clear_end = script.index("\n}", clear_start)
        clear_body = script[clear_start:clear_end]
        self.assertIn("cardModalities = []", clear_body)
        self.assertIn("cardModalityHistory = []", clear_body)
        self.assertIn("cardModalitiesLoaded = false", clear_body)


if __name__ == "__main__":
    unittest.main()
