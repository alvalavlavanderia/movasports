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


class PayableCreationPersistenceTest(unittest.TestCase):
    ADMIN_PASSWORD = "Payable-Creation-Test-Password-9"

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
        server.DB_PATH = os.path.join(self.temp_dir.name, "payable-creation.db")
        os.environ["MOVA_ADMIN_PASSWORD"] = self.ADMIN_PASSWORD
        server.init_db()

        self.baseline_payable = self.payable_record("payable-baseline")
        state = server.default_state()
        state["payables"] = [self.baseline_payable]
        state["products"] = [{"id": "state-marker", "name": "Preservar"}]
        state["cash"] = [{
            "id": "cash-marker",
            "direction": "in",
            "type": "opening",
            "description": "Marcador de estado",
            "method": "cash",
            "amount": 10.0,
            "refId": "",
            "createdAt": "2026-07-17T10:00:00+00:00",
        }]
        with server.connect_db() as conn:
            self.insert_payable(conn, self.baseline_payable)
            conn.execute(
                """
                INSERT INTO cash_movements (
                    id, store_id, direction, type, description, method, amount, ref_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "cash-marker",
                    "matriz",
                    "in",
                    "opening",
                    "Marcador de estado",
                    "cash",
                    10.0,
                    "",
                    "2026-07-17T10:00:00+00:00",
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
                    "operator-payable",
                    "matriz",
                    "Operador Financeiro",
                    "operator-payable",
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
    def payable_record(payable_id="payable-new"):
        return {
            "id": payable_id,
            "supplier": "Fornecedor Teste",
            "category": "Aluguel",
            "amount": 1250.46,
            "issueDate": "2026-07-01",
            "dueDate": "2026-07-20",
            "notes": "Conta mensal de teste",
            "paidAmount": 0.0,
            "fee": 0.0,
            "discount": 0.0,
            "status": "pending",
            "paidAt": "",
            "createdAt": "2026-07-17T10:00:00+00:00",
            "updatedAt": "2026-07-17T10:00:00+00:00",
        }

    @staticmethod
    def payable_payload(payable_id="payable-new"):
        return {
            "id": payable_id,
            "supplier": "Fornecedor Teste",
            "category": "Aluguel",
            "amount": 1250.456,
            "issueDate": "2026-07-01",
            "dueDate": "2026-07-20",
            "notes": "Conta mensal de teste",
        }

    @staticmethod
    def insert_payable(conn, payable):
        conn.execute(
            """
            INSERT INTO payables (
                id, store_id, supplier, category, amount, issue_date, due_date,
                notes, paid_amount, fee, discount, status, paid_at, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payable["id"],
                "matriz",
                payable["supplier"],
                payable["category"],
                payable["amount"],
                payable["issueDate"],
                payable["dueDate"],
                payable["notes"],
                payable["paidAmount"],
                payable["fee"],
                payable["discount"],
                payable["status"],
                payable["paidAt"],
                payable["createdAt"],
                payable["updatedAt"],
            ),
        )

    def authenticate(self):
        with self.client.session_transaction() as session:
            session["user"] = {
                "id": "operator-payable",
                "name": "Operador Financeiro",
                "login": "operator-payable",
                "role": "operator",
                "active": True,
            }

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

    def persistence_sentinels(self):
        return (
            mock.patch.object(server, "write_state", side_effect=AssertionError("write_state chamado")),
            mock.patch.object(
                server,
                "sync_business_tables",
                side_effect=AssertionError("sync_business_tables chamado"),
            ),
            mock.patch.object(
                server,
                "sync_payable_to_state",
                side_effect=AssertionError("sync_payable_to_state chamado"),
            ),
        )

    def assert_direct_persistence_failure_rolls_back(self, statement_prefix, payable_id):
        payable = self.payable_record(payable_id)
        before_state = self.raw_state()
        before_counts = self.table_counts()
        original_connect = server.connect_db

        def failing_connect():
            return FailingConnection(original_connect(), statement_prefix)

        write_state, sync_business_tables, sync_payable_to_state = self.persistence_sentinels()
        with (
            server.app.test_request_context("/api/payables", method="POST"),
            mock.patch.object(server, "connect_db", side_effect=failing_connect),
            write_state,
            sync_business_tables,
            sync_payable_to_state,
        ):
            with self.assertRaisesRegex(sqlite3.OperationalError, "falha sentinela controlada"):
                server.persist_payable_creation(payable)

        self.assertEqual(self.raw_state(), before_state)
        self.assertEqual(self.table_counts(), before_counts)

    def test_post_persists_payable_state_and_audit_without_global_rebuild(self):
        self.authenticate()
        before_state = self.raw_state()
        before_counts = self.table_counts()
        write_state, sync_business_tables, sync_payable_to_state = self.persistence_sentinels()

        with write_state as write_mock, sync_business_tables as business_mock, sync_payable_to_state as payable_mock:
            response = self.client.post("/api/payables", json=self.payable_payload())

        self.assertEqual(response.status_code, 201)
        payload = response.get_json()
        self.assertEqual(set(payload), {"ok", "data"})
        self.assertTrue(payload["ok"])
        payable = payload["data"]
        self.assertEqual(payable["id"], "payable-new")
        self.assertEqual(payable["amount"], 1250.46)
        self.assertEqual(payable["status"], "pending")
        self.assertEqual(payable["paidAmount"], 0.0)
        self.assertEqual(payable["fee"], 0.0)
        self.assertEqual(payable["discount"], 0.0)
        self.assertEqual(payable["paidAt"], "")
        write_mock.assert_not_called()
        business_mock.assert_not_called()
        payable_mock.assert_not_called()

        with sqlite3.connect(server.DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM payables WHERE id = ?", (payable["id"],)).fetchone()
            audit = conn.execute(
                "SELECT action, module, ref_id, details FROM audit_logs WHERE ref_id = ?",
                (payable["id"],),
            ).fetchone()
        self.assertEqual(row["store_id"], "matriz")
        self.assertEqual(row["supplier"], payable["supplier"])
        self.assertEqual(row["category"], payable["category"])
        self.assertEqual(row["amount"], payable["amount"])
        self.assertEqual(row["issue_date"], payable["issueDate"])
        self.assertEqual(row["due_date"], payable["dueDate"])
        self.assertEqual(row["notes"], payable["notes"])
        self.assertEqual(row["paid_amount"], payable["paidAmount"])
        self.assertEqual(row["fee"], payable["fee"])
        self.assertEqual(row["discount"], payable["discount"])
        self.assertEqual(row["status"], payable["status"])
        self.assertEqual(row["paid_at"], payable["paidAt"])
        self.assertEqual(row["created_at"], payable["createdAt"])
        self.assertEqual(row["updated_at"], payable["updatedAt"])
        self.assertEqual((audit["action"], audit["module"], audit["ref_id"]), ("create", "payable", payable["id"]))
        self.assertEqual(json.loads(audit["details"])["payable"]["id"], payable["id"])

        after_state = self.raw_state()
        self.assertEqual(after_state["payables"], [self.baseline_payable, payable])
        self.assertEqual(
            {key: value for key, value in after_state.items() if key != "payables"},
            {key: value for key, value in before_state.items() if key != "payables"},
        )
        after_counts = self.table_counts()
        for table, before_count in before_counts.items():
            expected = before_count + 1 if table in {"payables", "audit_logs"} else before_count
            self.assertEqual(after_counts[table], expected, table)

    def test_duplicate_id_preserves_replacement_contract(self):
        self.authenticate()
        before_counts = self.table_counts()
        replacement = {
            **self.payable_payload("payable-baseline"),
            "supplier": "Fornecedor Substituto",
            "amount": 300.0,
            "dueDate": "2026-08-10",
        }
        write_state, sync_business_tables, sync_payable_to_state = self.persistence_sentinels()
        with write_state, sync_business_tables, sync_payable_to_state:
            response = self.client.post("/api/payables", json=replacement)

        self.assertEqual(response.status_code, 201)
        payable = response.get_json()["data"]
        with sqlite3.connect(server.DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM payables WHERE id = ?", (payable["id"],)).fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["supplier"], "Fornecedor Substituto")
        self.assertEqual(rows[0]["amount"], 300.0)
        self.assertEqual(self.raw_state()["payables"], [payable])
        after_counts = self.table_counts()
        self.assertEqual(after_counts["payables"], before_counts["payables"])
        self.assertEqual(after_counts["audit_logs"], before_counts["audit_logs"] + 1)

    def test_existing_authentication_and_validation_contracts_are_preserved(self):
        unauthenticated = self.client.post("/api/payables", json=self.payable_payload())
        self.assertEqual(unauthenticated.status_code, 401)
        self.assertEqual(set(unauthenticated.get_json()), {"ok", "error"})

        self.authenticate()
        invalid_json = self.client.post("/api/payables", data="[]", content_type="application/json")
        self.assertEqual(invalid_json.status_code, 400)
        self.assertEqual(invalid_json.get_json(), {"ok": False, "error": "Envie um JSON válido."})

        cases = (
            ({"category": ""}, "Categoria é obrigatória."),
            ({"amount": 0}, "Valor deve ser maior que zero."),
            ({"dueDate": ""}, "Data de vencimento é obrigatória."),
            ({"status": "invalid"}, "Status inválido."),
        )
        for index, (changes, expected_error) in enumerate(cases):
            with self.subTest(expected_error=expected_error):
                response = self.client.post(
                    "/api/payables",
                    json={**self.payable_payload(f"payable-invalid-{index}"), **changes},
                )
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.get_json(), {"ok": False, "error": expected_error})

    def test_transaction_rolls_back_payable_and_state_when_audit_fails(self):
        payable = self.payable_record("payable-audit-failure")
        before_state = self.raw_state()
        before_counts = self.table_counts()
        write_state, sync_business_tables, sync_payable_to_state = self.persistence_sentinels()

        with (
            server.app.test_request_context("/api/payables", method="POST"),
            mock.patch.object(server, "record_audit", side_effect=RuntimeError("audit failure")),
            write_state,
            sync_business_tables,
            sync_payable_to_state,
        ):
            with self.assertRaisesRegex(RuntimeError, "audit failure"):
                server.persist_payable_creation(payable)

        self.assertEqual(self.raw_state(), before_state)
        self.assertEqual(self.table_counts(), before_counts)

    def test_transaction_rolls_back_when_payable_insert_fails(self):
        self.assert_direct_persistence_failure_rolls_back(
            "INSERT INTO payables",
            "payable-insert-failure",
        )

    def test_transaction_rolls_back_when_app_state_update_fails(self):
        self.assert_direct_persistence_failure_rolls_back(
            "INSERT INTO app_state",
            "payable-state-failure",
        )

    def test_postgres_path_locks_state_and_uses_compatible_sql(self):
        existing_state = server.default_state()
        existing_state["payables"] = [self.baseline_payable]
        existing_state["products"] = [{"id": "state-marker", "name": "Preservar"}]
        fake_connection = FakePostgresConnection(existing_state)
        payable = self.payable_record("payable-postgres")
        write_state, sync_business_tables, sync_payable_to_state = self.persistence_sentinels()

        with (
            server.app.test_request_context("/api/payables", method="POST"),
            mock.patch.object(server, "USE_POSTGRES", True),
            mock.patch.object(server, "connect_db", return_value=fake_connection),
            write_state,
            sync_business_tables,
            sync_payable_to_state,
        ):
            server.persist_payable_creation(payable)

        self.assertTrue(fake_connection.committed)
        self.assertFalse(fake_connection.rolled_back)
        statements = [sql for sql, _ in fake_connection.calls]
        self.assertTrue(any(sql == "SELECT data FROM app_state WHERE id = 1 FOR UPDATE" for sql in statements))
        self.assertTrue(any(sql.startswith("INSERT INTO payables") for sql in statements))
        self.assertTrue(any(sql.startswith("INSERT INTO app_state") for sql in statements))
        self.assertTrue(any(sql.startswith("INSERT INTO audit_logs") for sql in statements))
        self.assertEqual(fake_connection.saved_state["payables"], [self.baseline_payable, payable])
        self.assertEqual(fake_connection.saved_state["products"], existing_state["products"])
        for sql, params in fake_connection.calls:
            if params:
                translated = server.translate_postgres_sql(sql)
                self.assertNotIn("?", translated)
                self.assertIn("%s", translated)


if __name__ == "__main__":
    unittest.main()
