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
    def __init__(self, payable, state):
        self.payable = copy.deepcopy(payable)
        self.state = copy.deepcopy(state)
        self.calls = []
        self.saved_state = None
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
            self.payable.update({
                "paidAmount": params[0],
                "fee": params[1],
                "discount": params[2],
                "status": params[3],
                "paidAt": params[4],
                "updatedAt": params[5],
            })
        if normalized.startswith("INSERT INTO app_state"):
            self.saved_state = json.loads(params[0])
        return FakeCursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.rolled_back = exc_type is not None
        self.committed = exc_type is None


class TrackingConnection:
    def __init__(self, connection, failure_prefix=None):
        self.connection = connection
        self.failure_prefix = failure_prefix
        self.calls = []
        self.commits = 0
        self.rollbacks = 0

    def execute(self, sql, params=()):
        normalized = " ".join(sql.split())
        self.calls.append((normalized, params))
        if self.failure_prefix and normalized.startswith(self.failure_prefix):
            raise sqlite3.OperationalError("falha sentinela controlada")
        return self.connection.execute(sql, params)

    def __enter__(self):
        self.connection.__enter__()
        return self

    def __exit__(self, exc_type, exc, traceback):
        try:
            result = self.connection.__exit__(exc_type, exc, traceback)
            if exc_type is None:
                self.commits += 1
            else:
                self.rollbacks += 1
            return result
        finally:
            self.connection.close()

    def __getattr__(self, name):
        return getattr(self.connection, name)


class PayablePaymentPersistenceTest(unittest.TestCase):
    ADMIN_PASSWORD = "Payable-Payment-Test-Password-9"

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original = {
            "environment": server.ENVIRONMENT,
            "use_postgres": server.USE_POSTGRES,
            "database_url": server.DATABASE_URL,
            "db_path": server.DB_PATH,
            "admin_password": os.environ.get("MOVA_ADMIN_PASSWORD"),
            "testing": server.app.config.get("TESTING"),
        }
        server.ENVIRONMENT = EnvironmentConfig("development", "configured", False, False)
        server.USE_POSTGRES = False
        server.DATABASE_URL = ""
        server.DB_PATH = os.path.join(self.temp_dir.name, "payable-payment.db")
        server.app.config["TESTING"] = False
        os.environ["MOVA_ADMIN_PASSWORD"] = self.ADMIN_PASSWORD
        server.init_db()

        self.payable = self.payable_record("payable-target")
        self.other_payable = self.payable_record("payable-other", amount=250.0)
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
        state["payables"] = [self.payable, self.other_payable]
        state["cash"] = [self.baseline_movement]
        state["products"] = [{"id": "state-marker", "name": "Preservar"}]
        state["cashClosings"] = [{"id": "closing-marker", "date": "2026-07-17"}]
        with server.connect_db() as conn:
            self.insert_payable(conn, self.payable)
            self.insert_payable(conn, self.other_payable)
            self.insert_movement(conn, self.baseline_movement)
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
                    "operator-payable-payment",
                    "matriz",
                    "Operador Financeiro",
                    "operator-payable-payment",
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
        server.app.config["TESTING"] = self.original["testing"]
        if self.original["admin_password"] is None:
            os.environ.pop("MOVA_ADMIN_PASSWORD", None)
        else:
            os.environ["MOVA_ADMIN_PASSWORD"] = self.original["admin_password"]
        self.client = None
        gc.collect()
        self.temp_dir.cleanup()

    @staticmethod
    def payable_record(payable_id, amount=100.0, **changes):
        payable = {
            "id": payable_id,
            "supplier": "Fornecedor Teste",
            "category": "Aluguel",
            "amount": amount,
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
        payable.update(changes)
        return payable

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
                payable["id"], "matriz", payable["supplier"], payable["category"], payable["amount"],
                payable["issueDate"], payable["dueDate"], payable["notes"], payable["paidAmount"],
                payable["fee"], payable["discount"], payable["status"], payable["paidAt"],
                payable["createdAt"], payable["updatedAt"],
            ),
        )

    @staticmethod
    def insert_movement(conn, movement):
        conn.execute(
            """
            INSERT INTO cash_movements (
                id, store_id, direction, type, description, method, amount, ref_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                movement["id"], "matriz", movement["direction"], movement["type"],
                movement["description"], movement["method"], movement["amount"],
                movement["refId"], movement["createdAt"],
            ),
        )

    def authenticate(self, valid=True):
        with self.client.session_transaction() as session:
            session["user"] = {
                "id": "operator-payable-payment" if valid else "missing-user",
                "name": "Operador Financeiro",
                "login": "operator-payable-payment",
                "role": "operator",
                "active": True,
            }

    def raw_state(self):
        with sqlite3.connect(server.DB_PATH) as conn:
            return json.loads(conn.execute("SELECT data FROM app_state WHERE id = 1").fetchone()[0])

    def raw_payable(self, payable_id="payable-target"):
        with sqlite3.connect(server.DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM payables WHERE id = ?", (payable_id,)).fetchone()
            return dict(row) if row else None

    def raw_movements(self):
        with sqlite3.connect(server.DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute("SELECT * FROM cash_movements ORDER BY created_at, id").fetchall()]

    def raw_audits(self):
        with sqlite3.connect(server.DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute("SELECT * FROM audit_logs ORDER BY created_at, id").fetchall()]

    def table_counts(self):
        tables = (
            "stores", "app_state", "users", "audit_logs", "brands", "categories", "suppliers",
            "customers", "products", "sales", "sale_items", "sale_payments", "cash_movements",
            "cash_closings", "receivables", "receivable_payments", "sale_returns", "sale_return_items",
            "payables",
        )
        with sqlite3.connect(server.DB_PATH) as conn:
            return {table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in tables}

    @staticmethod
    def persistence_sentinels():
        return (
            mock.patch.object(server, "write_state", side_effect=AssertionError("write_state chamado")),
            mock.patch.object(server, "sync_business_tables", side_effect=AssertionError("sync_business_tables chamado")),
            mock.patch.object(server, "sync_payable_to_state", side_effect=AssertionError("sync_payable_to_state chamado")),
        )

    def post_payment(self, payload=None, payable_id="payable-target", raw=False):
        if raw:
            return self.client.post(
                f"/api/payables/{payable_id}/pay",
                data=payload,
                content_type="application/json",
            )
        return self.client.post(f"/api/payables/{payable_id}/pay", json=payload)

    def replace_payable(self, payable):
        with server.connect_db() as conn:
            conn.execute("DELETE FROM payables WHERE id = ?", (payable["id"],))
            self.insert_payable(conn, payable)
            state = self.raw_state()
            state["payables"] = [payable if item.get("id") == payable["id"] else item for item in state["payables"]]
            conn.execute(
                "UPDATE app_state SET data = ?, updated_at = ? WHERE id = 1",
                (json.dumps(state, ensure_ascii=False), server.utc_now()),
            )

    def test_total_payment_preserves_contract_state_audit_and_isolation(self):
        self.authenticate()
        before_state = self.raw_state()
        before_counts = self.table_counts()
        write_state, business_tables, payable_state = self.persistence_sentinels()
        with write_state as write_mock, business_tables as business_mock, payable_state as payable_mock:
            response = self.post_payment({
                "amount": 90.0,
                "fee": 10.0,
                "discount": 20.0,
                "method": "cash",
                "paidAt": "2026-07-18T15:30:00+00:00",
                "note": "Pagamento final",
            })

        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(set(body), {"ok", "data"})
        self.assertEqual(set(body["data"]), {"payable", "cash"})
        payable = body["data"]["payable"]
        cash = body["data"]["cash"]
        self.assertEqual(len(cash), 1)
        self.assertEqual(payable["paidAmount"], 90.0)
        self.assertEqual(payable["fee"], 10.0)
        self.assertEqual(payable["discount"], 20.0)
        self.assertEqual(payable["status"], "paid")
        self.assertEqual(payable["paidAt"], "2026-07-18T15:30:00+00:00")
        self.assertEqual(cash[0]["direction"], "out")
        self.assertEqual(cash[0]["type"], "contas a pagar")
        self.assertEqual(cash[0]["description"], "Aluguel - Pagamento final")
        self.assertEqual(cash[0]["method"], "cash")
        self.assertEqual(cash[0]["amount"], 90.0)
        self.assertEqual(cash[0]["refId"], "payable-target")
        self.assertEqual(cash[0]["createdAt"], "2026-07-18T15:30:00+00:00")
        write_mock.assert_not_called()
        business_mock.assert_not_called()
        payable_mock.assert_not_called()

        row = self.raw_payable()
        self.assertEqual(row["store_id"], "matriz")
        self.assertEqual(row["paid_amount"], 90.0)
        self.assertEqual(row["status"], "paid")
        movements = self.raw_movements()
        self.assertEqual(len(movements), 2)
        self.assertEqual([item["id"] for item in movements if item["id"] != "cash-baseline"], [cash[0]["id"]])
        self.assertEqual(movements[-1]["store_id"], "matriz")

        after_state = self.raw_state()
        self.assertEqual(after_state["payables"], [self.other_payable, payable])
        self.assertEqual(after_state["cash"], [cash[0], self.baseline_movement])
        self.assertEqual(
            {key: value for key, value in after_state.items() if key not in {"payables", "cash"}},
            {key: value for key, value in before_state.items() if key not in {"payables", "cash"}},
        )
        audit = self.raw_audits()[-1]
        self.assertEqual((audit["action"], audit["module"], audit["ref_id"]), ("pay", "payable", "payable-target"))
        self.assertEqual(audit["user_id"], "operator-payable-payment")
        details = json.loads(audit["details"])
        self.assertEqual(details, {"payable": payable, "cash": cash})

        after_counts = self.table_counts()
        for table, count in before_counts.items():
            expected = count + 1 if table in {"cash_movements", "audit_logs"} else count
            self.assertEqual(after_counts[table], expected, table)
        self.assertEqual(self.raw_payable("payable-other")["amount"], 250.0)

    def test_partial_payments_accumulate_and_final_payment_uses_current_balance(self):
        self.authenticate()
        first = self.post_payment({"amount": 30.0, "paidAt": "2026-07-18T10:00:00+00:00"})
        second = self.post_payment({"amount": 20.0, "paidAt": "2026-07-18T11:00:00+00:00"})
        final = self.post_payment({"paidAt": "2026-07-18T12:00:00+00:00"})

        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.get_json()["data"]["payable"]["paidAmount"], 30.0)
        self.assertEqual(first.get_json()["data"]["payable"]["status"], "pending")
        self.assertEqual(first.get_json()["data"]["payable"]["paidAt"], "2026-07-18T10:00:00+00:00")
        self.assertEqual(second.get_json()["data"]["payable"]["paidAmount"], 50.0)
        self.assertEqual(second.get_json()["data"]["payable"]["status"], "pending")
        self.assertEqual(final.get_json()["data"]["payable"]["paidAmount"], 100.0)
        self.assertEqual(final.get_json()["data"]["payable"]["status"], "paid")
        self.assertEqual([item["amount"] for item in self.raw_movements() if item["ref_id"] == "payable-target"], [30.0, 20.0, 50.0])

    def test_empty_missing_and_invalid_json_use_current_defaults(self):
        self.authenticate()
        with mock.patch.object(server, "utc_now", return_value="2026-07-18T13:45:00+00:00"):
            empty = self.post_payment({})
        self.assertEqual(empty.status_code, 200)
        empty_data = empty.get_json()["data"]
        self.assertEqual(empty_data["payable"]["paidAmount"], 100.0)
        self.assertEqual(empty_data["cash"][0]["method"], "pix")
        self.assertEqual(empty_data["cash"][0]["createdAt"], "2026-07-18T13:45:00+00:00")
        self.assertEqual(empty_data["cash"][0]["description"], "Aluguel")

        third = self.payable_record("payable-third", amount=75.0, fee=5.0, discount=10.0)
        self.replace_payable(third)
        missing = self.post_payment(None, payable_id="payable-third", raw=True)
        self.assertEqual(missing.status_code, 200)
        self.assertEqual(missing.get_json()["data"]["payable"]["paidAmount"], 70.0)
        self.assertEqual(missing.get_json()["data"]["payable"]["fee"], 5.0)
        self.assertEqual(missing.get_json()["data"]["payable"]["discount"], 10.0)

        fourth = self.payable_record("payable-fourth", amount=40.0)
        self.replace_payable(fourth)
        invalid = self.post_payment("{", payable_id="payable-fourth", raw=True)
        self.assertEqual(invalid.status_code, 200)
        self.assertEqual(invalid.get_json()["data"]["payable"]["paidAmount"], 40.0)

    def test_rounding_tolerance_and_unvalidated_method_are_preserved(self):
        self.authenticate()
        partial = self.post_payment({"amount": 33.336, "method": "wire"})
        self.assertEqual(partial.status_code, 200)
        self.assertEqual(partial.get_json()["data"]["cash"][0]["amount"], 33.34)
        self.assertEqual(partial.get_json()["data"]["cash"][0]["method"], "wire")

        tolerance_payable = self.payable_record("payable-tolerance", amount=10.0)
        self.replace_payable(tolerance_payable)
        tolerance = self.post_payment({"amount": 10.01}, payable_id="payable-tolerance")
        self.assertEqual(tolerance.status_code, 200)
        self.assertEqual(tolerance.get_json()["data"]["payable"]["paidAmount"], 10.01)
        self.assertEqual(tolerance.get_json()["data"]["payable"]["status"], "paid")

    def test_cancelled_and_overdue_accounts_keep_permissive_behavior(self):
        self.authenticate()
        cancelled = self.payable_record("payable-target", status="cancelled")
        self.replace_payable(cancelled)
        cancelled_response = self.post_payment({"amount": 40.0})
        self.assertEqual(cancelled_response.status_code, 200)
        self.assertEqual(cancelled_response.get_json()["data"]["payable"]["status"], "pending")

        overdue = self.payable_record("payable-overdue", amount=30.0, dueDate="2020-01-01")
        self.replace_payable(overdue)
        overdue_response = self.post_payment({}, payable_id="payable-overdue")
        self.assertEqual(overdue_response.status_code, 200)
        self.assertEqual(overdue_response.get_json()["data"]["payable"]["status"], "paid")

    def test_current_error_contracts_and_permissions_are_preserved(self):
        unauthenticated = self.post_payment({"amount": 10.0})
        self.assertEqual(unauthenticated.status_code, 401)
        self.assertEqual(unauthenticated.get_json(), {"ok": False, "error": "Login obrigatório."})

        self.authenticate(valid=False)
        invalid_session = self.post_payment({"amount": 10.0})
        self.assertEqual(invalid_session.status_code, 401)
        self.assertEqual(invalid_session.get_json(), {"ok": False, "error": "Sessao expirada. Faca login novamente."})

        self.authenticate()
        missing = self.post_payment({}, payable_id="missing")
        self.assertEqual(missing.status_code, 404)
        self.assertEqual(missing.get_json(), {"ok": False, "error": "Conta não encontrada."})

        paid = self.payable_record("payable-target", status="paid", paidAmount=100.0)
        self.replace_payable(paid)
        already_paid = self.post_payment({"amount": 1.0})
        self.assertEqual(already_paid.status_code, 409)
        self.assertEqual(already_paid.get_json(), {"ok": False, "error": "Conta já está paga."})

    def test_invalid_amounts_do_not_modify_data(self):
        self.authenticate()
        for amount, expected in (
            (0, "Valor pago deve ser maior que zero."),
            (-1, "Valor pago deve ser maior que zero."),
            (100.02, "Valor pago nao pode ser maior que o saldo em aberto."),
        ):
            with self.subTest(amount=amount):
                before_state = self.raw_state()
                before_counts = self.table_counts()
                response = self.post_payment({"amount": amount})
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.get_json(), {"ok": False, "error": expected})
                self.assertEqual(self.raw_state(), before_state)
                self.assertEqual(self.table_counts(), before_counts)

    def test_json_list_preserves_existing_internal_error_behavior(self):
        self.authenticate()
        response = self.post_payment("[1]", raw=True)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(self.raw_payable()["paid_amount"], 0.0)
        self.assertEqual(len(self.raw_movements()), 1)

    def test_sqlite_uses_one_connection_begin_immediate_and_one_commit(self):
        tracker = TrackingConnection(server.connect_db())
        with (
            server.app.test_request_context("/api/payables/payable-target/pay", method="POST"),
            mock.patch.object(server, "connect_db", return_value=tracker) as connect_mock,
        ):
            payable, cash = server.persist_payable_payment("payable-target", {"amount": 25.0})

        self.assertEqual(payable["paidAmount"], 25.0)
        self.assertEqual(len(cash), 1)
        connect_mock.assert_called_once_with()
        self.assertEqual(tracker.calls[0][0], "BEGIN IMMEDIATE")
        self.assertEqual(tracker.commits, 1)
        self.assertEqual(tracker.rollbacks, 0)

    def assert_failure_rolls_back(self, failure_prefix=None, audit_failure=False):
        before_state = self.raw_state()
        before_payables = {item: self.raw_payable(item) for item in ("payable-target", "payable-other")}
        before_movements = self.raw_movements()
        before_audits = self.raw_audits()
        tracker = TrackingConnection(server.connect_db(), failure_prefix)
        audit_patch = (
            mock.patch.object(server, "record_audit", side_effect=RuntimeError("audit failure"))
            if audit_failure else mock.patch.object(server, "record_audit", wraps=server.record_audit)
        )
        write_state, business_tables, payable_state = self.persistence_sentinels()
        with (
            server.app.test_request_context("/api/payables/payable-target/pay", method="POST"),
            mock.patch.object(server, "connect_db", return_value=tracker),
            audit_patch,
            write_state,
            business_tables,
            payable_state,
        ):
            expected = RuntimeError if audit_failure else sqlite3.OperationalError
            with self.assertRaises(expected):
                server.persist_payable_payment("payable-target", {"amount": 25.0})

        self.assertEqual(self.raw_state(), before_state)
        self.assertEqual({item: self.raw_payable(item) for item in before_payables}, before_payables)
        self.assertEqual(self.raw_movements(), before_movements)
        self.assertEqual(self.raw_audits(), before_audits)
        self.assertEqual(tracker.commits, 0)
        self.assertEqual(tracker.rollbacks, 1)

    def test_failures_roll_back_every_payment_structure(self):
        for prefix in ("UPDATE payables", "INSERT INTO cash_movements", "INSERT INTO app_state"):
            with self.subTest(prefix=prefix):
                self.assert_failure_rolls_back(failure_prefix=prefix)
        self.assert_failure_rolls_back(audit_failure=True)

    def test_postgres_locks_payable_then_state_and_uses_one_transaction(self):
        state = self.raw_state()
        fake = FakePostgresConnection(self.payable, state)
        write_state, business_tables, payable_state = self.persistence_sentinels()
        with (
            server.app.test_request_context("/api/payables/payable-target/pay", method="POST"),
            mock.patch.object(server, "USE_POSTGRES", True),
            mock.patch.object(server, "connect_db", return_value=fake) as connect_mock,
            write_state,
            business_tables,
            payable_state,
        ):
            payable, cash = server.persist_payable_payment("payable-target", {
                "amount": 25.0,
                "method": "credit",
                "paidAt": "2026-07-18T16:00:00+00:00",
            })

        connect_mock.assert_called_once_with()
        self.assertTrue(fake.committed)
        self.assertFalse(fake.rolled_back)
        statements = [sql for sql, _ in fake.calls]
        payable_lock = next(i for i, sql in enumerate(statements) if sql.startswith("SELECT id, supplier"))
        state_lock = statements.index("SELECT data FROM app_state WHERE id = 1 FOR UPDATE")
        self.assertIn("FOR UPDATE", statements[payable_lock])
        self.assertLess(payable_lock, state_lock)
        self.assertTrue(any(sql.startswith("UPDATE payables") for sql in statements))
        self.assertTrue(any(sql.startswith("INSERT INTO cash_movements") for sql in statements))
        self.assertTrue(any(sql.startswith("INSERT INTO app_state") for sql in statements))
        self.assertTrue(any(sql.startswith("INSERT INTO audit_logs") for sql in statements))
        self.assertEqual(fake.saved_state["payables"], [self.other_payable, payable])
        self.assertEqual(fake.saved_state["cash"], [cash[0], self.baseline_movement])
        for sql, params in fake.calls:
            if params:
                translated = server.translate_postgres_sql(sql)
                self.assertNotIn("?", translated)
                self.assertIn("%s", translated)

    def test_postgres_rolls_back_when_audit_fails(self):
        fake = FakePostgresConnection(self.payable, self.raw_state())
        write_state, business_tables, payable_state = self.persistence_sentinels()
        with (
            server.app.test_request_context("/api/payables/payable-target/pay", method="POST"),
            mock.patch.object(server, "USE_POSTGRES", True),
            mock.patch.object(server, "connect_db", return_value=fake),
            mock.patch.object(server, "record_audit", side_effect=RuntimeError("audit failure")),
            write_state,
            business_tables,
            payable_state,
        ):
            with self.assertRaisesRegex(RuntimeError, "audit failure"):
                server.persist_payable_payment("payable-target", {"amount": 25.0})

        self.assertFalse(fake.committed)
        self.assertTrue(fake.rolled_back)

    def test_sequential_full_retry_reloads_paid_status(self):
        self.authenticate()
        first = self.post_payment({})
        second = self.post_payment({})
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 409)
        self.assertEqual(len([item for item in self.raw_movements() if item["ref_id"] == "payable-target"]), 1)


if __name__ == "__main__":
    unittest.main()
