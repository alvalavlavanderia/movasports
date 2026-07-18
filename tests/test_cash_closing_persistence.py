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


class FailingConnection:
    def __init__(self, connection, statement_prefix):
        self.connection = connection
        self.statement_prefix = statement_prefix

    def execute(self, sql, params=()):
        normalized = " ".join(sql.split())
        if normalized.startswith(self.statement_prefix):
            raise sqlite3.OperationalError("falha sentinela controlada")
        return self.connection.execute(sql, params)

    def __enter__(self):
        self.connection.__enter__()
        return self

    def __exit__(self, exc_type, exc, traceback):
        try:
            return self.connection.__exit__(exc_type, exc, traceback)
        finally:
            self.connection.close()

    def __getattr__(self, name):
        return getattr(self.connection, name)


class CashClosingPersistenceTest(unittest.TestCase):
    ADMIN_PASSWORD = "Cash-Closing-Test-Password-9"

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
        server.DB_PATH = os.path.join(self.temp_dir.name, "cash-closings.db")
        os.environ["MOVA_ADMIN_PASSWORD"] = self.ADMIN_PASSWORD
        server.init_db()

        self.baseline_closing = self.closing_record("closing-baseline")
        self.cash_movements = [
            self.cash_movement("cash-prior", "in", "cash", 20, "2026-07-16T10:00:00+00:00"),
            self.cash_movement("cash-in", "in", "cash", 100, "2026-07-17T10:00:00+00:00"),
            self.cash_movement("cash-out", "out", "cash", 25, "2026-07-17T11:00:00+00:00"),
            self.cash_movement("pix-in", "in", "pix", 40, "2026-07-17T12:00:00+00:00"),
        ]
        state = server.default_state()
        state["cash"] = self.cash_movements
        state["cashClosings"] = [self.baseline_closing]
        state["products"] = [{"id": "state-marker", "name": "Preservar"}]
        with server.connect_db() as conn:
            for movement in self.cash_movements:
                conn.execute(
                    """
                    INSERT INTO cash_movements (
                        id, store_id, direction, type, description, method, amount, ref_id, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        movement["id"],
                        "matriz",
                        movement["direction"],
                        movement["type"],
                        movement["description"],
                        movement["method"],
                        movement["amount"],
                        movement["refId"],
                        movement["createdAt"],
                    ),
                )
            self.insert_closing(conn, self.baseline_closing)
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
                    "operator-closing",
                    "matriz",
                    "Operador Caixa",
                    "operator-closing",
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

    @staticmethod
    def cash_movement(movement_id, direction, method, amount, created_at):
        return {
            "id": movement_id,
            "direction": direction,
            "type": "test",
            "description": "Movimento de teste",
            "method": method,
            "amount": float(amount),
            "refId": "",
            "createdAt": created_at,
        }

    @staticmethod
    def closing_record(closing_id="closing-new"):
        return {
            "id": closing_id,
            "date": "2026-07-17",
            "expectedCash": 95.0,
            "informedCash": 90.0,
            "difference": -5.0,
            "totalBalance": 135.0,
            "cashIn": 100.0,
            "cashOut": 25.0,
            "notes": "Fechamento de teste",
            "userId": "operator-closing",
            "userName": "Operador Caixa",
            "createdAt": "2026-07-17T20:00:00+00:00",
        }

    @staticmethod
    def insert_closing(conn, closing):
        conn.execute(
            """
            INSERT INTO cash_closings (
                id, store_id, date, expected_cash, informed_cash, difference, total_balance,
                cash_in, cash_out, notes, user_id, user_name, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                closing["id"],
                "matriz",
                closing["date"],
                closing["expectedCash"],
                closing["informedCash"],
                closing["difference"],
                closing["totalBalance"],
                closing["cashIn"],
                closing["cashOut"],
                closing["notes"],
                closing["userId"],
                closing["userName"],
                closing["createdAt"],
            ),
        )

    def authenticate(self, role="operator"):
        user = {
            "id": "admin" if role == "admin" else "operator-closing",
            "name": "Administrador" if role == "admin" else "Operador Caixa",
            "login": "admin" if role == "admin" else "operator-closing",
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

    def assert_direct_persistence_failure_rolls_back(self, statement_prefix, closing_id):
        closing = self.closing_record(closing_id)
        before_state = self.raw_state()
        before_counts = self.table_counts()
        original_connect = server.connect_db

        def failing_connect():
            return FailingConnection(original_connect(), statement_prefix)

        with (
            server.app.test_request_context("/api/cash-closings", method="POST"),
            mock.patch.object(server, "connect_db", side_effect=failing_connect),
            mock.patch.object(server, "write_state", side_effect=AssertionError("write_state chamado")),
            mock.patch.object(
                server,
                "sync_business_tables",
                side_effect=AssertionError("sync_business_tables chamado"),
            ),
        ):
            with self.assertRaisesRegex(sqlite3.OperationalError, "falha sentinela controlada"):
                server.persist_cash_closing(closing)

        self.assertEqual(self.raw_state(), before_state)
        self.assertEqual(self.table_counts(), before_counts)

    def test_post_persists_closing_state_and_audit_without_global_rebuild(self):
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
            response = self.client.post(
                "/api/cash-closings",
                json={"date": "2026-07-17", "informedCash": 90, "notes": "Fechamento de teste"},
            )

        self.assertEqual(response.status_code, 201)
        payload = response.get_json()
        self.assertEqual(set(payload), {"ok", "data"})
        self.assertTrue(payload["ok"])
        closing = payload["data"]
        self.assertTrue(closing["id"])
        self.assertEqual(closing["date"], "2026-07-17")
        self.assertEqual(closing["expectedCash"], 95.0)
        self.assertEqual(closing["informedCash"], 90.0)
        self.assertEqual(closing["difference"], -5.0)
        self.assertEqual(closing["totalBalance"], 135.0)
        self.assertEqual(closing["cashIn"], 100.0)
        self.assertEqual(closing["cashOut"], 25.0)
        self.assertEqual(closing["userId"], "operator-closing")
        write_state.assert_not_called()
        sync_business_tables.assert_not_called()

        with sqlite3.connect(server.DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM cash_closings WHERE id = ?", (closing["id"],)).fetchone()
            audit = conn.execute(
                "SELECT action, module, ref_id, details FROM audit_logs WHERE ref_id = ?",
                (closing["id"],),
            ).fetchone()
        self.assertEqual(row["store_id"], "matriz")
        self.assertEqual(row["date"], closing["date"])
        self.assertEqual(row["expected_cash"], closing["expectedCash"])
        self.assertEqual(row["informed_cash"], closing["informedCash"])
        self.assertEqual(row["difference"], closing["difference"])
        self.assertEqual(row["total_balance"], closing["totalBalance"])
        self.assertEqual(row["cash_in"], closing["cashIn"])
        self.assertEqual(row["cash_out"], closing["cashOut"])
        self.assertEqual(row["notes"], closing["notes"])
        self.assertEqual(row["user_id"], closing["userId"])
        self.assertEqual(row["user_name"], closing["userName"])
        self.assertEqual(row["created_at"], closing["createdAt"])
        self.assertEqual((audit["action"], audit["module"], audit["ref_id"]), ("create", "cash_closing", closing["id"]))
        self.assertEqual(json.loads(audit["details"])["closing"]["id"], closing["id"])

        after_state = self.raw_state()
        self.assertEqual(after_state["cashClosings"], [closing, self.baseline_closing])
        self.assertEqual(
            {key: value for key, value in after_state.items() if key != "cashClosings"},
            {key: value for key, value in before_state.items() if key != "cashClosings"},
        )
        after_counts = self.table_counts()
        for table, before_count in before_counts.items():
            expected = before_count + 1 if table in {"cash_closings", "audit_logs"} else before_count
            self.assertEqual(after_counts[table], expected, table)

    def test_existing_authentication_and_validation_contracts_are_preserved(self):
        unauthenticated = self.client.post("/api/cash-closings", json={"informedCash": 90})
        self.assertEqual(unauthenticated.status_code, 401)
        self.assertEqual(set(unauthenticated.get_json()), {"ok", "error"})

        self.authenticate("operator")
        invalid = self.client.post("/api/cash-closings", data="[]", content_type="application/json")
        self.assertEqual(invalid.status_code, 400)
        self.assertEqual(invalid.get_json(), {"ok": False, "error": "Envie um JSON válido."})

    def test_transaction_rolls_back_closing_and_state_when_audit_fails(self):
        closing = self.closing_record("closing-audit-failure")
        before_state = self.raw_state()
        before_counts = self.table_counts()

        with (
            server.app.test_request_context("/api/cash-closings", method="POST"),
            mock.patch.object(server, "record_audit", side_effect=RuntimeError("audit failure")),
            mock.patch.object(server, "write_state", side_effect=AssertionError("write_state chamado")),
            mock.patch.object(
                server,
                "sync_business_tables",
                side_effect=AssertionError("sync_business_tables chamado"),
            ),
        ):
            with self.assertRaisesRegex(RuntimeError, "audit failure"):
                server.persist_cash_closing(closing)

        self.assertEqual(self.raw_state(), before_state)
        self.assertEqual(self.table_counts(), before_counts)

    def test_transaction_rolls_back_when_closing_insert_fails(self):
        self.assert_direct_persistence_failure_rolls_back(
            "INSERT INTO cash_closings",
            "closing-insert-failure",
        )

    def test_transaction_rolls_back_when_app_state_update_fails(self):
        self.assert_direct_persistence_failure_rolls_back(
            "INSERT INTO app_state",
            "closing-state-failure",
        )

    def test_postgres_path_locks_state_and_uses_compatible_sql(self):
        existing_state = server.default_state()
        existing_state["cashClosings"] = [self.baseline_closing]
        existing_state["products"] = [{"id": "state-marker", "name": "Preservar"}]
        fake_connection = FakePostgresConnection(existing_state)
        closing = self.closing_record("closing-postgres")

        with (
            server.app.test_request_context("/api/cash-closings", method="POST"),
            mock.patch.object(server, "USE_POSTGRES", True),
            mock.patch.object(server, "connect_db", return_value=fake_connection),
            mock.patch.object(server, "write_state", side_effect=AssertionError("write_state chamado")),
            mock.patch.object(
                server,
                "sync_business_tables",
                side_effect=AssertionError("sync_business_tables chamado"),
            ),
        ):
            server.persist_cash_closing(closing)

        self.assertTrue(fake_connection.committed)
        self.assertFalse(fake_connection.rolled_back)
        statements = [sql for sql, _ in fake_connection.calls]
        self.assertTrue(any(sql == "SELECT data FROM app_state WHERE id = 1 FOR UPDATE" for sql in statements))
        self.assertTrue(any(sql.startswith("INSERT INTO cash_closings") for sql in statements))
        self.assertTrue(any(sql.startswith("INSERT INTO app_state") for sql in statements))
        self.assertTrue(any(sql.startswith("INSERT INTO audit_logs") for sql in statements))
        self.assertEqual(fake_connection.saved_state["cashClosings"], [closing, self.baseline_closing])
        self.assertEqual(fake_connection.saved_state["products"], existing_state["products"])
        for sql, params in fake_connection.calls:
            if params:
                translated = server.translate_postgres_sql(sql)
                self.assertNotIn("?", translated)
                self.assertIn("%s", translated)


if __name__ == "__main__":
    unittest.main()
