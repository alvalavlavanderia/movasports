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


class PayablePersistenceIntegrationTest(unittest.TestCase):
    ADMIN_PASSWORD = "Payable-Integration-Test-Password-9"

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
        server.DB_PATH = os.path.join(self.temp_dir.name, "payable-integration.db")
        server.app.config["TESTING"] = False
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

        self.baseline_cash = {
            "id": "cash-integration-marker",
            "direction": "in",
            "type": "opening",
            "description": "Marcador de integracao",
            "method": "cash",
            "amount": 1000.0,
            "refId": "",
            "createdAt": "2026-07-18T10:00:00+00:00",
        }
        state = server.default_state()
        state["payables"] = []
        state["cash"] = [copy.deepcopy(self.baseline_cash)]
        state["products"] = [{"id": "state-marker", "name": "Preservar"}]
        state["cashClosings"] = [{"id": "closing-marker", "date": "2026-07-18"}]
        with server.connect_db() as conn:
            conn.execute(
                """
                INSERT INTO cash_movements (
                    id, store_id, direction, type, description, method, amount, ref_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    self.baseline_cash["id"], "matriz", self.baseline_cash["direction"],
                    self.baseline_cash["type"], self.baseline_cash["description"],
                    self.baseline_cash["method"], self.baseline_cash["amount"],
                    self.baseline_cash["refId"], self.baseline_cash["createdAt"],
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
                    "operator-payable-integration", "matriz", "Operador Financeiro",
                    "operator-payable-integration", "not-used", "operator", 1, server.utc_now(),
                ),
            )
        self.client = server.app.test_client()
        with self.client.session_transaction() as session:
            session["user"] = {
                "id": "operator-payable-integration",
                "name": "Operador Financeiro",
                "login": "operator-payable-integration",
                "role": "operator",
                "active": True,
            }

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
    def payable_payload(payable_id="payable-integration"):
        return {
            "id": payable_id,
            "supplier": "Fornecedor Inicial",
            "category": "Aluguel",
            "amount": 100.0,
            "issueDate": "2026-07-01",
            "dueDate": "2026-07-30",
            "notes": "Conta integrada",
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

    def raw_state(self):
        with sqlite3.connect(server.DB_PATH) as conn:
            return json.loads(conn.execute("SELECT data FROM app_state WHERE id = 1").fetchone()[0])

    def raw_payable(self, payable_id="payable-integration"):
        with sqlite3.connect(server.DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM payables WHERE id = ?", (payable_id,)).fetchone()
            return dict(row) if row else None

    def raw_movements(self, payable_id="payable-integration"):
        with sqlite3.connect(server.DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            return [
                dict(row)
                for row in conn.execute(
                    "SELECT * FROM cash_movements WHERE ref_id = ? ORDER BY created_at, id",
                    (payable_id,),
                ).fetchall()
            ]

    def raw_audits(self, payable_id="payable-integration"):
        with sqlite3.connect(server.DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            return [
                dict(row)
                for row in conn.execute(
                    "SELECT * FROM audit_logs WHERE ref_id = ? ORDER BY created_at, id",
                    (payable_id,),
                ).fetchall()
            ]

    def table_counts(self):
        tables = (
            "stores", "app_state", "users", "audit_logs", "brands", "categories",
            "suppliers", "customers", "products", "sales", "sale_items", "sale_payments",
            "cash_movements", "cash_closings", "receivables", "receivable_payments",
            "sale_returns", "sale_return_items", "payables",
        )
        with sqlite3.connect(server.DB_PATH) as conn:
            return {table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in tables}

    def test_create_edit_and_pay_coexist_without_global_rebuild(self):
        before_state = self.raw_state()
        before_counts = self.table_counts()
        sentinels = self.persistence_sentinels()
        with sentinels[0], sentinels[1], sentinels[2]:
            created = self.client.post("/api/payables", json=self.payable_payload())
            edited = self.client.put(
                "/api/payables/payable-integration",
                json={"supplier": "Fornecedor Editado", "amount": 120.0},
            )
            paid = self.client.post(
                "/api/payables/payable-integration/pay",
                json={
                    "amount": 40.0,
                    "method": "pix",
                    "paidAt": "2026-07-18T15:00:00+00:00",
                },
            )

        self.assertEqual(created.status_code, 201)
        self.assertEqual(edited.status_code, 200)
        self.assertEqual(paid.status_code, 200)
        self.assertEqual(edited.get_json()["data"]["supplier"], "Fornecedor Editado")
        paid_data = paid.get_json()["data"]
        self.assertEqual(paid_data["payable"]["amount"], 120.0)
        self.assertEqual(paid_data["payable"]["paidAmount"], 40.0)
        self.assertEqual(paid_data["payable"]["status"], "pending")
        self.assertEqual(len(paid_data["cash"]), 1)

        row = self.raw_payable()
        self.assertEqual(row["supplier"], "Fornecedor Editado")
        self.assertEqual(row["amount"], 120.0)
        self.assertEqual(row["paid_amount"], 40.0)
        movements = self.raw_movements()
        self.assertEqual(len(movements), 1)
        self.assertEqual(movements[0]["amount"], 40.0)

        state = self.raw_state()
        state_payable = next(item for item in state["payables"] if item["id"] == "payable-integration")
        self.assertEqual(state_payable, paid_data["payable"])
        self.assertEqual(state["cash"], [paid_data["cash"][0], self.baseline_cash])
        self.assertEqual(state["products"], before_state["products"])
        self.assertEqual(state["cashClosings"], before_state["cashClosings"])
        self.assertEqual([item["action"] for item in self.raw_audits()], ["create", "update", "pay"])

        after_counts = self.table_counts()
        for table, count in before_counts.items():
            expected = count
            if table == "payables":
                expected += 1
            elif table == "cash_movements":
                expected += 1
            elif table == "audit_logs":
                expected += 3
            self.assertEqual(after_counts[table], expected, table)

    def test_partial_payment_and_later_edits_do_not_duplicate_movements(self):
        sentinels = self.persistence_sentinels()
        with sentinels[0], sentinels[1], sentinels[2]:
            self.assertEqual(
                self.client.post("/api/payables", json=self.payable_payload()).status_code,
                201,
            )
            partial = self.client.post(
                "/api/payables/payable-integration/pay",
                json={"amount": 25.0, "paidAt": "2026-07-18T15:00:00+00:00"},
            )
            edit_partial = self.client.put(
                "/api/payables/payable-integration",
                json={"notes": "Editada depois do pagamento parcial"},
            )
            movement_count_after_edit = len(self.raw_movements())
            final_payment = self.client.post(
                "/api/payables/payable-integration/pay",
                json={"paidAt": "2026-07-18T16:00:00+00:00"},
            )
            edit_paid = self.client.put(
                "/api/payables/payable-integration",
                json={"supplier": "Fornecedor depois da baixa"},
            )

        self.assertEqual(partial.status_code, 200)
        self.assertEqual(partial.get_json()["data"]["payable"]["paidAmount"], 25.0)
        self.assertEqual(edit_partial.status_code, 200)
        self.assertEqual(edit_partial.get_json()["data"]["paidAmount"], 25.0)
        self.assertEqual(movement_count_after_edit, 1)
        self.assertEqual(final_payment.status_code, 200)
        self.assertEqual(final_payment.get_json()["data"]["payable"]["status"], "paid")
        self.assertEqual(edit_paid.status_code, 400)
        self.assertIn("nao pode ser editada", edit_paid.get_json()["error"])
        self.assertEqual(len(self.raw_movements()), 2)
        self.assertEqual([item["amount"] for item in self.raw_movements()], [25.0, 75.0])

    def test_failed_update_does_not_change_previously_committed_creation(self):
        sentinels = self.persistence_sentinels()
        with sentinels[0], sentinels[1], sentinels[2]:
            created = self.client.post("/api/payables", json=self.payable_payload())
        self.assertEqual(created.status_code, 201)
        before_row = self.raw_payable()
        before_state = self.raw_state()
        before_counts = self.table_counts()

        sentinels = self.persistence_sentinels()
        with (
            server.app.test_request_context("/api/payables/payable-integration", method="PUT"),
            mock.patch.object(server, "record_audit", side_effect=RuntimeError("audit failure")),
            sentinels[0], sentinels[1], sentinels[2],
        ):
            with self.assertRaisesRegex(RuntimeError, "audit failure"):
                server.persist_payable_update("payable-integration", {"amount": 999.0})

        self.assertEqual(self.raw_payable(), before_row)
        self.assertEqual(self.raw_state(), before_state)
        self.assertEqual(self.table_counts(), before_counts)
        self.assertEqual([item["action"] for item in self.raw_audits()], ["create"])

    def test_update_handler_does_not_repeat_database_initialization(self):
        self.assertEqual(
            self.client.post("/api/payables", json=self.payable_payload()).status_code,
            201,
        )
        sentinels = self.persistence_sentinels()
        with (
            server.app.test_request_context(
                "/api/payables/payable-integration",
                method="PUT",
                json={"notes": "Sem reinicializar o banco"},
            ),
            mock.patch.object(server, "init_db", side_effect=AssertionError("init_db chamado pelo handler")),
            sentinels[0], sentinels[1], sentinels[2],
        ):
            server.session["user"] = {
                "id": "operator-payable-integration",
                "role": "operator",
            }
            response = server.update_payable_api("payable-integration")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["data"]["notes"], "Sem reinicializar o banco")


if __name__ == "__main__":
    unittest.main()
