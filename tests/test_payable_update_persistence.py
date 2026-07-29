import copy
import gc
import json
import os
import sqlite3
import tempfile
import unittest
from unittest import mock

from database_migrations.runner import run_database_migrations
from environment_config import EnvironmentConfig
import server


class FakeCursor:
    def __init__(self, row=None):
        self.row = row

    def fetchone(self):
        return self.row

    def fetchall(self):
        return []


class FakePostgresConnection:
    def __init__(self, payable, state):
        self.payable = copy.deepcopy(payable)
        self.state = copy.deepcopy(state)
        self.calls = []
        self.saved_state = None
        self.updated_payable_params = None
        self.committed = False
        self.rolled_back = False

    def execute(self, sql, params=()):
        normalized = " ".join(sql.split())
        self.calls.append((normalized, params))
        if normalized.startswith("SELECT id, supplier"):
            return FakeCursor(copy.deepcopy(self.payable))
        if normalized.startswith("SELECT data FROM app_state"):
            return FakeCursor({"data": json.dumps(self.state, ensure_ascii=False)})
        if normalized.startswith("UPDATE payables"):
            self.updated_payable_params = params
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


class RecordingConnection:
    def __init__(self, connection):
        self.connection = connection
        self.calls = []

    def execute(self, sql, params=()):
        self.calls.append(" ".join(sql.split()))
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


class PayableUpdatePersistenceTest(unittest.TestCase):
    ADMIN_PASSWORD = "Payable-Update-Test-Password-9"

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
        server.DB_PATH = os.path.join(self.temp_dir.name, "payable-update.db")
        os.environ["MOVA_ADMIN_PASSWORD"] = self.ADMIN_PASSWORD
        run_database_migrations(
            test_mode=True,
            sqlite_path=server.DB_PATH,
            create_database=True,
        )
        with server.connect_db() as conn:
            conn.execute(
                "INSERT INTO stores (id, name, created_at) VALUES (?, ?, ?)",
                ("matriz", "Matriz", server.utc_now()),
            )
            conn.execute(
                "INSERT INTO app_state (id, data, updated_at) VALUES (1, ?, ?)",
                (
                    json.dumps(server.default_state(), ensure_ascii=False),
                    server.utc_now(),
                ),
            )

        self.payable = self.payable_record("payable-update")
        self.other_payable = self.payable_record("payable-other")
        self.other_payable["supplier"] = "Outro fornecedor"
        self.other_payable["amount"] = 400.0
        state = server.default_state()
        state["payables"] = [copy.deepcopy(self.payable), copy.deepcopy(self.other_payable)]
        state["products"] = [{"id": "state-marker", "name": "Preservar"}]
        state["cash"] = [{
            "id": "cash-marker",
            "direction": "in",
            "type": "opening",
            "description": "Marcador de estado",
            "method": "cash",
            "amount": 10.0,
            "refId": "",
            "createdAt": "2026-07-18T10:00:00+00:00",
        }]
        with server.connect_db() as conn:
            self.insert_payable(conn, self.payable)
            self.insert_payable(conn, self.other_payable)
            conn.execute(
                """
                INSERT INTO cash_movements (
                    id, store_id, direction, type, description, method, amount, ref_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "cash-marker", "matriz", "in", "opening", "Marcador de estado",
                    "cash", 10.0, "", "2026-07-18T10:00:00+00:00",
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
                    "operator-payable-update", "matriz", "Operador Financeiro",
                    "operator-payable-update", "not-used", "operator", 1, server.utc_now(),
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
    def payable_record(payable_id):
        return {
            "id": payable_id,
            "supplier": "Fornecedor Original",
            "category": "Aluguel",
            "amount": 1250.0,
            "issueDate": "2026-07-01",
            "dueDate": "2026-07-20",
            "notes": "Conta original",
            "paidAmount": 0.0,
            "fee": 0.0,
            "discount": 0.0,
            "status": "pending",
            "paidAt": "",
            "createdAt": "2026-07-17T10:00:00+00:00",
            "updatedAt": "2026-07-17T10:00:00+00:00",
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
                payable["id"], "matriz", payable["supplier"], payable["category"],
                payable["amount"], payable["issueDate"], payable["dueDate"], payable["notes"],
                payable["paidAmount"], payable["fee"], payable["discount"], payable["status"],
                payable["paidAt"], payable["createdAt"], payable["updatedAt"],
            ),
        )

    def authenticate(self, user_id="operator-payable-update"):
        with self.client.session_transaction() as session:
            session["user"] = {
                "id": user_id,
                "name": "Operador Financeiro",
                "login": "operator-payable-update",
                "role": "operator",
                "active": True,
            }

    def raw_state(self):
        with sqlite3.connect(server.DB_PATH) as conn:
            row = conn.execute("SELECT data FROM app_state WHERE id = 1").fetchone()
            return json.loads(row[0])

    def fetch_payable(self, payable_id):
        with sqlite3.connect(server.DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM payables WHERE id = ?", (payable_id,)).fetchone()
            return dict(row) if row else None

    def table_counts(self):
        tables = (
            "stores", "app_state", "users", "audit_logs", "brands", "categories",
            "suppliers", "customers", "products", "sales", "sale_items", "sale_payments",
            "cash_movements", "cash_closings", "receivables", "receivable_payments",
            "sale_returns", "sale_return_items", "payables",
        )
        with sqlite3.connect(server.DB_PATH) as conn:
            return {table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in tables}

    def unrelated_table_snapshot(self):
        tables = (
            "stores", "users", "brands", "categories", "suppliers", "customers",
            "products", "sales", "sale_items", "sale_payments", "cash_movements",
            "cash_closings", "receivables", "receivable_payments", "sale_returns",
            "sale_return_items",
        )
        with sqlite3.connect(server.DB_PATH) as conn:
            return {
                table: conn.execute(f"SELECT * FROM {table} ORDER BY rowid").fetchall()
                for table in tables
            }

    @staticmethod
    def persistence_sentinels():
        return (
            mock.patch.object(server, "write_state", side_effect=AssertionError("write_state chamado")),
            mock.patch.object(
                server, "sync_business_tables", side_effect=AssertionError("sync_business_tables chamado")
            ),
            mock.patch.object(
                server, "sync_payable_to_state", side_effect=AssertionError("sync_payable_to_state chamado")
            ),
        )

    def assert_failure_rolls_back(self, statement_prefix):
        before_state = self.raw_state()
        before_row = self.fetch_payable(self.payable["id"])
        before_counts = self.table_counts()
        original_connect = server.connect_db

        def failing_connect():
            return FailingConnection(original_connect(), statement_prefix)

        sentinels = self.persistence_sentinels()
        with (
            server.app.test_request_context(
                f"/api/payables/{self.payable['id']}", method="PUT"
            ),
            mock.patch.object(server, "connect_db", side_effect=failing_connect),
            sentinels[0], sentinels[1], sentinels[2],
        ):
            with self.assertRaisesRegex(sqlite3.OperationalError, "falha sentinela controlada"):
                server.persist_payable_update(self.payable["id"], {"amount": 999.0})

        self.assertEqual(self.raw_state(), before_state)
        self.assertEqual(self.fetch_payable(self.payable["id"]), before_row)
        self.assertEqual(self.table_counts(), before_counts)

    def test_full_update_preserves_contract_audit_and_table_isolation(self):
        self.authenticate()
        before_state = self.raw_state()
        before_counts = self.table_counts()
        unrelated_before = self.unrelated_table_snapshot()
        other_before = self.fetch_payable(self.other_payable["id"])
        payload = {
            "id": "payload-id-must-be-ignored",
            "supplier": "Fornecedor Atualizado",
            "category": "Servicos",
            "amount": 987.656,
            "issueDate": "data-livre",
            "dueDate": "vencimento-livre",
            "notes": "Conta atualizada",
            "paidAmount": 100.129,
            "fee": 4.555,
            "discount": 1.234,
            "status": "paid",
            "paidAt": "horario-livre",
            "createdAt": "2026-01-02T03:04:05+00:00",
            "unknown": "ignorar",
        }
        sentinels = self.persistence_sentinels()
        with sentinels[0] as write_mock, sentinels[1] as business_mock, sentinels[2] as payable_mock:
            response = self.client.put(f"/api/payables/{self.payable['id']}", json=payload)

        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(set(body), {"ok", "data"})
        self.assertTrue(body["ok"])
        payable = body["data"]
        self.assertEqual(payable["id"], self.payable["id"])
        self.assertNotIn("unknown", payable)
        self.assertEqual(payable["amount"], 987.66)
        self.assertEqual(payable["paidAmount"], 100.13)
        self.assertEqual(payable["fee"], 4.56)
        self.assertEqual(payable["discount"], 1.23)
        self.assertEqual(payable["issueDate"], "data-livre")
        self.assertEqual(payable["dueDate"], "vencimento-livre")
        self.assertNotEqual(payable["updatedAt"], self.payable["updatedAt"])
        write_mock.assert_not_called()
        business_mock.assert_not_called()
        payable_mock.assert_not_called()

        row = self.fetch_payable(self.payable["id"])
        self.assertEqual(row["supplier"], payable["supplier"])
        self.assertEqual(row["amount"], payable["amount"])
        self.assertEqual(row["paid_amount"], payable["paidAmount"])
        self.assertEqual(row["status"], payable["status"])
        self.assertEqual(row["created_at"], payable["createdAt"])
        self.assertEqual(self.fetch_payable(self.other_payable["id"]), other_before)

        after_state = self.raw_state()
        self.assertEqual(after_state["payables"], [payable, self.other_payable])
        self.assertEqual(
            {key: value for key, value in after_state.items() if key != "payables"},
            {key: value for key, value in before_state.items() if key != "payables"},
        )
        after_counts = self.table_counts()
        for table, count in before_counts.items():
            expected = count + 1 if table == "audit_logs" else count
            self.assertEqual(after_counts[table], expected, table)
        self.assertEqual(self.unrelated_table_snapshot(), unrelated_before)
        with sqlite3.connect(server.DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            audit = conn.execute(
                "SELECT user_id, user_role, action, module, ref_id, details FROM audit_logs WHERE ref_id = ?",
                (self.payable["id"],),
            ).fetchone()
        self.assertEqual(
            (audit["user_id"], audit["user_role"], audit["action"], audit["module"], audit["ref_id"]),
            ("operator-payable-update", "operator", "update", "payable", self.payable["id"]),
        )
        self.assertEqual(json.loads(audit["details"]), {"payable": payable})

    def test_partial_empty_unknown_and_url_id_behavior_are_preserved(self):
        self.authenticate()
        partial = self.client.put(
            f"/api/payables/{self.payable['id']}",
            json={"id": "outro-id", "supplier": "Fornecedor Parcial", "extra": "ignorar"},
        )
        self.assertEqual(partial.status_code, 200)
        partial_payable = partial.get_json()["data"]
        self.assertEqual(partial_payable["id"], self.payable["id"])
        self.assertEqual(partial_payable["supplier"], "Fornecedor Parcial")
        self.assertEqual(partial_payable["category"], self.payable["category"])
        self.assertEqual(partial_payable["amount"], self.payable["amount"])
        self.assertNotIn("extra", partial_payable)

        empty = self.client.put(f"/api/payables/{self.payable['id']}", json={})
        self.assertEqual(empty.status_code, 200)
        empty_payable = empty.get_json()["data"]
        self.assertEqual(empty_payable["supplier"], "Fornecedor Parcial")
        self.assertEqual(empty_payable["id"], self.payable["id"])
        self.assertTrue(empty_payable["updatedAt"])

    def test_authentication_not_found_json_and_validation_contracts_are_preserved(self):
        unauthenticated = self.client.put(f"/api/payables/{self.payable['id']}", json={})
        self.assertEqual(unauthenticated.status_code, 401)
        self.assertEqual(set(unauthenticated.get_json()), {"ok", "error"})

        self.authenticate("usuario-inexistente")
        expired = self.client.put(f"/api/payables/{self.payable['id']}", json={})
        self.assertEqual(expired.status_code, 401)

        self.authenticate()
        invalid_json = self.client.put(
            f"/api/payables/{self.payable['id']}", data="[]", content_type="application/json"
        )
        self.assertEqual(invalid_json.status_code, 400)
        self.assertEqual(invalid_json.get_json(), {"ok": False, "error": "Envie um JSON v\u00e1lido."})
        missing = self.client.put("/api/payables/inexistente", json={})
        self.assertEqual(missing.status_code, 404)
        self.assertEqual(missing.get_json(), {"ok": False, "error": "Conta n\u00e3o encontrada."})

        cases = (
            ({"category": ""}, "Categoria \u00e9 obrigat\u00f3ria."),
            ({"amount": 0}, "Valor deve ser maior que zero."),
            ({"amount": -1}, "Valor deve ser maior que zero."),
            ({"dueDate": ""}, "Data de vencimento \u00e9 obrigat\u00f3ria."),
            ({"status": "invalid"}, "Status inv\u00e1lido."),
        )
        for changes, expected_error in cases:
            with self.subTest(expected_error=expected_error):
                response = self.client.put(f"/api/payables/{self.payable['id']}", json=changes)
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.get_json(), {"ok": False, "error": expected_error})

    def test_paid_and_cancelled_accounts_block_silent_reopening(self):
        self.authenticate()
        paid = self.client.put(
            f"/api/payables/{self.payable['id']}",
            json={"status": "paid", "paidAmount": 1250, "paidAt": "2026-07-18T12:00:00Z"},
        )
        self.assertEqual(paid.status_code, 200)

        reopened_paid = self.client.put(
            f"/api/payables/{self.payable['id']}",
            json={
                "status": "pending", "paidAmount": None, "paidAt": None,
                "amount": 800, "dueDate": "qualquer-texto",
            },
        )
        self.assertEqual(reopened_paid.status_code, 400)
        self.assertIn("nao pode ser editada", reopened_paid.get_json()["error"])

        with server.connect_db() as conn:
            conn.execute(
                """
                UPDATE payables
                SET status = 'cancelled', paid_amount = 0, paid_at = NULL
                WHERE id = ?
                """,
                (self.payable["id"],),
            )
        reopened = self.client.put(
            f"/api/payables/{self.payable['id']}", json={"status": "pending"}
        )
        self.assertEqual(reopened.status_code, 400)
        self.assertIn("nao pode ser editada", reopened.get_json()["error"])
        self.assertEqual(self.table_counts()["cash_movements"], 1)

    def test_transaction_rolls_back_when_payable_update_fails(self):
        self.assert_failure_rolls_back("UPDATE payables")

    def test_transaction_rolls_back_when_app_state_update_fails(self):
        self.assert_failure_rolls_back("INSERT INTO app_state")

    def test_transaction_rolls_back_when_audit_fails(self):
        before_state = self.raw_state()
        before_row = self.fetch_payable(self.payable["id"])
        before_counts = self.table_counts()
        sentinels = self.persistence_sentinels()
        with (
            server.app.test_request_context(
                f"/api/payables/{self.payable['id']}", method="PUT"
            ),
            mock.patch.object(server, "record_audit", side_effect=RuntimeError("audit failure")),
            sentinels[0], sentinels[1], sentinels[2],
        ):
            with self.assertRaisesRegex(RuntimeError, "audit failure"):
                server.persist_payable_update(self.payable["id"], {"amount": 999.0})
        self.assertEqual(self.raw_state(), before_state)
        self.assertEqual(self.fetch_payable(self.payable["id"]), before_row)
        self.assertEqual(self.table_counts(), before_counts)

    def test_sqlite_uses_begin_immediate_and_one_persistence_connection(self):
        original_connect = server.connect_db
        recording = RecordingConnection(original_connect())
        sentinels = self.persistence_sentinels()
        with (
            server.app.test_request_context(
                f"/api/payables/{self.payable['id']}", method="PUT"
            ),
            mock.patch.object(server, "connect_db", return_value=recording) as connect_mock,
            sentinels[0], sentinels[1], sentinels[2],
        ):
            payable, error = server.persist_payable_update(
                self.payable["id"], {"notes": "Atualizacao SQLite"}
            )
        self.assertIsNone(error)
        self.assertEqual(payable["notes"], "Atualizacao SQLite")
        connect_mock.assert_called_once_with()
        self.assertEqual(recording.calls[0], "BEGIN IMMEDIATE")

    def test_postgres_path_locks_rows_and_uses_one_transaction(self):
        state = server.default_state()
        state["payables"] = [copy.deepcopy(self.payable), copy.deepcopy(self.other_payable)]
        state["products"] = [{"id": "state-marker", "name": "Preservar"}]
        fake = FakePostgresConnection(self.payable, state)
        sentinels = self.persistence_sentinels()
        with (
            server.app.test_request_context(
                f"/api/payables/{self.payable['id']}", method="PUT"
            ),
            mock.patch.object(server, "USE_POSTGRES", True),
            mock.patch.object(server, "connect_db", return_value=fake) as connect_mock,
            sentinels[0], sentinels[1], sentinels[2],
        ):
            payable, error = server.persist_payable_update(
                self.payable["id"], {"supplier": "Fornecedor PostgreSQL"}
            )

        self.assertIsNone(error)
        self.assertEqual(payable["supplier"], "Fornecedor PostgreSQL")
        connect_mock.assert_called_once_with()
        self.assertTrue(fake.committed)
        self.assertFalse(fake.rolled_back)
        statements = [sql for sql, _ in fake.calls]
        payable_lock = next(
            index for index, sql in enumerate(statements)
            if sql.startswith("SELECT id, supplier") and sql.endswith("FOR UPDATE")
        )
        state_lock = statements.index("SELECT data FROM app_state WHERE id = 1 FOR UPDATE")
        payable_update = next(index for index, sql in enumerate(statements) if sql.startswith("UPDATE payables"))
        state_update = next(index for index, sql in enumerate(statements) if sql.startswith("INSERT INTO app_state"))
        audit_insert = next(index for index, sql in enumerate(statements) if sql.startswith("INSERT INTO audit_logs"))
        self.assertLess(payable_lock, state_lock)
        self.assertLess(payable_update, state_lock)
        self.assertLess(state_lock, state_update)
        self.assertLess(state_update, audit_insert)
        self.assertEqual(fake.saved_state["payables"], [payable, self.other_payable])
        self.assertEqual(fake.saved_state["products"], state["products"])
        for sql, params in fake.calls:
            if params:
                translated = server.translate_postgres_sql(sql)
                self.assertNotIn("?", translated)
                self.assertIn("%s", translated)


if __name__ == "__main__":
    unittest.main()
