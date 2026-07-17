import copy
import gc
import json
import os
import sqlite3
import tempfile
import unittest
from unittest import mock

from environment_config import EnvironmentConfig
import server


class FakeCursor:
    def __init__(self, row=None):
        self.row = row

    def fetchone(self):
        return self.row


class FakePostgresConnection:
    def __init__(self, state):
        self.state = copy.deepcopy(state)
        self.calls = []
        self.saved_state = None
        self.committed = False
        self.rolled_back = False

    def execute(self, sql, params=()):
        normalized = " ".join(sql.split())
        self.calls.append((normalized, params))
        if normalized.startswith("SELECT data FROM app_state"):
            return FakeCursor({"data": json.dumps(self.state, ensure_ascii=False)})
        if normalized.startswith("INSERT INTO app_state"):
            self.saved_state = json.loads(params[0])
        return FakeCursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.rolled_back = exc_type is not None
        self.committed = exc_type is None


class CashMovementPersistenceTest(unittest.TestCase):
    ADMIN_PASSWORD = "Cash-Movement-Test-Password-9"

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original = {
            "environment": server.ENVIRONMENT,
            "use_postgres": server.USE_POSTGRES,
            "database_url": server.DATABASE_URL,
            "db_path": server.DB_PATH,
            "admin_password": os.environ.get("MOVA_ADMIN_PASSWORD"),
        }
        server.ENVIRONMENT = EnvironmentConfig("development", "configured", False, False)
        server.USE_POSTGRES = False
        server.DATABASE_URL = ""
        server.DB_PATH = os.path.join(self.temp_dir.name, "cash-movements.db")
        os.environ["MOVA_ADMIN_PASSWORD"] = self.ADMIN_PASSWORD
        server.init_db()
        self.baseline_movement = {
            "id": "cash-baseline",
            "direction": "in",
            "type": "opening",
            "description": "Saldo inicial de teste",
            "method": "cash",
            "amount": 10.0,
            "refId": "",
            "createdAt": "2026-07-17T10:00:00+00:00",
        }
        state = server.default_state()
        state["cash"] = [self.baseline_movement]
        state["products"] = [{"id": "state-marker", "name": "Preservar"}]
        with server.connect_db() as conn:
            conn.execute(
                """
                INSERT INTO cash_movements (
                    id, store_id, direction, type, description, method, amount, ref_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    self.baseline_movement["id"],
                    "matriz",
                    self.baseline_movement["direction"],
                    self.baseline_movement["type"],
                    self.baseline_movement["description"],
                    self.baseline_movement["method"],
                    self.baseline_movement["amount"],
                    self.baseline_movement["refId"],
                    self.baseline_movement["createdAt"],
                ),
            )
            conn.execute(
                "UPDATE app_state SET data = ?, updated_at = ? WHERE id = 1",
                (json.dumps(state, ensure_ascii=False), server.utc_now()),
            )
            conn.execute(
                """
                INSERT INTO users (id, store_id, name, login, password_hash, role, active, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "operator-cash",
                    "matriz",
                    "Operador Caixa",
                    "operator-cash",
                    "not-used",
                    "operator",
                    1,
                    server.utc_now(),
                ),
            )
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

    def authenticate(self, role="admin"):
        user = {
            "id": "admin" if role == "admin" else "operator-cash",
            "name": "Administrador" if role == "admin" else "Operador Caixa",
            "login": "admin" if role == "admin" else "operator-cash",
            "role": role,
            "active": True,
        }
        with self.client.session_transaction() as session:
            session["user"] = user

    def raw_state(self):
        with sqlite3.connect(server.DB_PATH) as conn:
            row = conn.execute("SELECT data FROM app_state WHERE id = 1").fetchone()
            return json.loads(row[0])

    def table_counts(self):
        tables = (
            "stores",
            "app_state",
            "users",
            "audit_logs",
            "brands",
            "categories",
            "suppliers",
            "customers",
            "products",
            "sales",
            "sale_items",
            "sale_payments",
            "cash_movements",
            "cash_closings",
            "receivables",
            "receivable_payments",
            "sale_returns",
            "sale_return_items",
            "payables",
        )
        with sqlite3.connect(server.DB_PATH) as conn:
            return {table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in tables}

    @staticmethod
    def movement_payload(movement_id="cash-new"):
        return {
            "id": movement_id,
            "direction": "out",
            "type": "fuel",
            "description": "Despesa operacional de teste",
            "method": "cash",
            "amount": 25.678,
            "refId": "test-reference",
            "createdAt": "2026-07-17T14:30:00+00:00",
        }

    def test_post_persists_cash_state_and_audit_without_global_rebuild(self):
        self.authenticate("operator")
        before_state = self.raw_state()
        before_counts = self.table_counts()

        with (
            mock.patch.object(server, "write_state", side_effect=AssertionError("write_state chamado")) as write_state,
            mock.patch.object(
                server,
                "sync_business_tables",
                side_effect=AssertionError("sync_business_tables chamado"),
            ) as sync_business_tables,
        ):
            response = self.client.post("/api/cash-movements", json=self.movement_payload())

        self.assertEqual(response.status_code, 201)
        payload = response.get_json()
        self.assertEqual(set(payload), {"ok", "data"})
        self.assertTrue(payload["ok"])
        self.assertEqual(set(payload["data"]), {"cash", "receivables"})
        self.assertEqual(payload["data"]["receivables"], [])
        movement = payload["data"]["cash"][0]
        self.assertEqual(movement["id"], "cash-new")
        self.assertEqual(movement["amount"], 25.68)
        write_state.assert_not_called()
        sync_business_tables.assert_not_called()

        with sqlite3.connect(server.DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM cash_movements WHERE id = ?", (movement["id"],)).fetchone()
            audit = conn.execute(
                "SELECT action, module, ref_id, details FROM audit_logs WHERE ref_id = ?",
                (movement["id"],),
            ).fetchone()
        self.assertEqual(row["store_id"], "matriz")
        self.assertEqual(row["direction"], movement["direction"])
        self.assertEqual(row["type"], movement["type"])
        self.assertEqual(row["description"], movement["description"])
        self.assertEqual(row["method"], movement["method"])
        self.assertEqual(row["amount"], movement["amount"])
        self.assertEqual(row["ref_id"], movement["refId"])
        self.assertEqual(row["created_at"], movement["createdAt"])
        self.assertEqual((audit["action"], audit["module"], audit["ref_id"]), ("create", "cash", movement["id"]))
        self.assertEqual(json.loads(audit["details"])["movement"]["id"], movement["id"])

        after_state = self.raw_state()
        self.assertEqual(after_state["cash"], [movement, self.baseline_movement])
        self.assertEqual({key: value for key, value in after_state.items() if key != "cash"}, {
            key: value for key, value in before_state.items() if key != "cash"
        })
        after_counts = self.table_counts()
        for table, before_count in before_counts.items():
            expected = before_count + 1 if table in {"cash_movements", "audit_logs"} else before_count
            self.assertEqual(after_counts[table], expected, table)

    def test_existing_authentication_and_validation_contracts_are_preserved(self):
        unauthenticated = self.client.post("/api/cash-movements", json=self.movement_payload())
        self.assertEqual(unauthenticated.status_code, 401)
        self.assertEqual(set(unauthenticated.get_json()), {"ok", "error"})

        self.authenticate("operator")
        invalid = self.client.post(
            "/api/cash-movements",
            json={**self.movement_payload("cash-invalid"), "direction": "invalid"},
        )
        self.assertEqual(invalid.status_code, 400)
        self.assertEqual(
            invalid.get_json(),
            {"ok": False, "error": "Tipo de movimenta\u00e7\u00e3o inv\u00e1lido."},
        )
        with sqlite3.connect(server.DB_PATH) as conn:
            self.assertIsNone(conn.execute("SELECT id FROM cash_movements WHERE id = ?", ("cash-invalid",)).fetchone())

    def test_transaction_rolls_back_cash_and_state_when_audit_fails(self):
        movement = server.normalize_cash_movement_payload(self.movement_payload("cash-rollback"))
        before_state = self.raw_state()
        before_counts = self.table_counts()

        with (
            server.app.test_request_context("/api/cash-movements", method="POST"),
            mock.patch.object(server, "record_audit", side_effect=RuntimeError("audit failure")),
            mock.patch.object(server, "write_state", side_effect=AssertionError("write_state chamado")),
            mock.patch.object(
                server,
                "sync_business_tables",
                side_effect=AssertionError("sync_business_tables chamado"),
            ),
        ):
            with self.assertRaisesRegex(RuntimeError, "audit failure"):
                server.persist_cash_movement(movement)

        self.assertEqual(self.raw_state(), before_state)
        self.assertEqual(self.table_counts(), before_counts)
        with sqlite3.connect(server.DB_PATH) as conn:
            self.assertIsNone(conn.execute("SELECT id FROM cash_movements WHERE id = ?", (movement["id"],)).fetchone())

    def test_postgres_path_locks_state_and_uses_compatible_sql(self):
        existing_state = server.default_state()
        existing_state["cash"] = [self.baseline_movement]
        fake_connection = FakePostgresConnection(existing_state)
        movement = server.normalize_cash_movement_payload(self.movement_payload("cash-postgres"))

        with (
            server.app.test_request_context("/api/cash-movements", method="POST"),
            mock.patch.object(server, "USE_POSTGRES", True),
            mock.patch.object(server, "connect_db", return_value=fake_connection),
            mock.patch.object(server, "write_state", side_effect=AssertionError("write_state chamado")),
            mock.patch.object(
                server,
                "sync_business_tables",
                side_effect=AssertionError("sync_business_tables chamado"),
            ),
        ):
            server.persist_cash_movement(movement)

        self.assertTrue(fake_connection.committed)
        self.assertFalse(fake_connection.rolled_back)
        statements = [sql for sql, _ in fake_connection.calls]
        self.assertTrue(any(sql == "SELECT data FROM app_state WHERE id = 1 FOR UPDATE" for sql in statements))
        self.assertTrue(any(sql.startswith("INSERT INTO cash_movements") for sql in statements))
        self.assertTrue(any(sql.startswith("INSERT INTO app_state") for sql in statements))
        self.assertTrue(any(sql.startswith("INSERT INTO audit_logs") for sql in statements))
        self.assertEqual(fake_connection.saved_state["cash"], [movement, self.baseline_movement])
        for sql, params in fake_connection.calls:
            if params:
                translated = server.translate_postgres_sql(sql)
                self.assertNotIn("?", translated)
                self.assertIn("%s", translated)


if __name__ == "__main__":
    unittest.main()
