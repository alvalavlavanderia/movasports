import gc
import json
import os
import sqlite3
import tempfile
import unittest
from unittest import mock

from database_migrations.migrations.v005_purchase_financial_flows import MIGRATION_005
from database_migrations.runner import run_database_migrations
from environment_config import EnvironmentConfig
import server


AUTHORIZED_ENV = {
    "APP_ENV": "development",
    "MOVA_ALLOW_MIGRATIONS": "true",
}


class _EmptyCursor:
    def fetchone(self):
        return None

    def fetchall(self):
        return []


class _PostgresPathOnSQLite:
    def __init__(self, path):
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.statements = []

    def execute(self, sql, params=()):
        self.statements.append(" ".join(sql.split()))
        if "pg_advisory_xact_lock" in sql:
            return _EmptyCursor()
        return self.connection.execute(sql.replace(" FOR UPDATE", ""), params)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        if exc_type:
            self.connection.rollback()
        else:
            self.connection.commit()
        self.connection.close()


class PurchaseFinancialBusinessRulesTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original = (
            server.ENVIRONMENT,
            server.USE_POSTGRES,
            server.DATABASE_URL,
            server.DB_PATH,
        )
        server.ENVIRONMENT = EnvironmentConfig("development", "configured", False, False)
        server.USE_POSTGRES = False
        server.DATABASE_URL = ""
        server.DB_PATH = os.path.join(self.temp_dir.name, "purchase-financial.db")
        run_database_migrations(
            environ=AUTHORIZED_ENV,
            sqlite_path=server.DB_PATH,
            create_database=True,
        )
        with server.connect_db() as connection:
            connection.execute(
                "INSERT INTO stores (id, name, created_at) VALUES (?, ?, ?)",
                ("matriz", "Matriz", "2026-07-23T10:00:00Z"),
            )
            connection.execute(
                "INSERT INTO app_state (id, data, updated_at) VALUES (1, ?, ?)",
                (json.dumps(server.default_state()), "2026-07-23T10:00:00Z"),
            )
            connection.execute(
                """
                INSERT INTO users (
                    id, store_id, name, login, password_hash, role, active, updated_at
                ) VALUES ('operator', 'matriz', 'Operador', 'operator', 'not-used',
                          'operator', 1, '2026-07-23T10:00:00Z')
                """
            )
        self.client = server.app.test_client()
        with self.client.session_transaction() as session:
            session["user"] = {
                "id": "operator", "name": "Operador", "login": "operator",
                "role": "operator", "active": True,
            }
        self.brand = self.catalog("/api/brands", "Mova")
        self.category = self.catalog("/api/categories", "Fitness")
        self.size = self.catalog("/api/sizes", "M")
        self.color = self.catalog("/api/colors", "Preto")
        self.supplier = self.client.post(
            "/api/suppliers",
            json={"name": "Fornecedor A", "document": "", "email": "a@example.test"},
        ).get_json()["data"]
        self.entry = self.create_entry()

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

    def catalog(self, endpoint, name):
        response = self.client.post(endpoint, json={"name": name})
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()["data"]

    def create_entry(self, key="purchase-entry"):
        response = self.client.post(
            "/api/stock-entries",
            headers={"Idempotency-Key": key},
            json={
                "quantity": 3,
                "product": {
                    "barcode": "789500000001",
                    "name": "Legging Purchase",
                    "gender": "Feminino",
                    "brandId": self.brand["id"],
                    "categoryId": self.category["id"],
                    "sizeId": self.size["id"],
                    "colorId": self.color["id"],
                    "supplierId": self.supplier["id"],
                    "cost": 50,
                    "price": 100,
                    "minStock": 1,
                    "active": True,
                },
            },
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()["data"]["entry"]

    def link_payable(self, amount=150, due="2026-08-22"):
        response = self.client.post(
            f"/api/stock-entries/{self.entry['id']}/payables",
            json={"amount": amount, "dueDate": due, "notes": "Compra teste"},
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()["data"]["payables"][0]

    def test_migration_005_is_additive_and_registered(self):
        self.assertEqual(MIGRATION_005.version, 5)
        self.assertTrue(any("CREATE TABLE supplier_returns" in sql for sql in MIGRATION_005.sqlite_statements))
        self.assertTrue(any("CREATE TABLE supplier_credits" in sql for sql in MIGRATION_005.postgresql_statements))
        with sqlite3.connect(server.DB_PATH) as connection:
            tables = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
            version = connection.execute(
                "SELECT MAX(version) FROM schema_migrations"
            ).fetchone()[0]
        self.assertEqual(version, 18)
        self.assertTrue({
            "stock_entry_payables", "stock_entry_cancellations",
            "purchase_stock_movements", "supplier_returns",
            "supplier_return_items", "supplier_credits",
            "supplier_return_allocations", "supplier_credit_usages",
            "supplier_credit_allocations",
        } <= tables)

    def test_entry_can_create_multiple_independent_payables(self):
        response = self.client.post(
            f"/api/stock-entries/{self.entry['id']}/payables",
            json={
                "payables": [
                    {"amount": 100, "dueDate": "2026-08-22"},
                    {"amount": 60, "dueDate": "2026-09-22"},
                ]
            },
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        data = response.get_json()["data"]
        self.assertEqual(len(data["payables"]), 2)
        self.assertEqual(data["entry"]["financial"]["payableTotal"], 160)
        self.assertEqual(data["entry"]["financial"]["difference"], -10)
        self.assertTrue(all(item["supplierId"] == self.supplier["id"] for item in data["payables"]))
        self.assertTrue(all(item["category"] == "Mercadorias" for item in data["payables"]))

    def test_entry_cancellation_reverses_stock_and_unpaid_payables_once(self):
        payable = self.link_payable()
        payload = {"reason": "Nota fiscal cancelada", "notes": "Teste"}
        first = self.client.post(
            f"/api/stock-entries/{self.entry['id']}/cancel",
            headers={"Idempotency-Key": "cancel-entry-1"},
            json=payload,
        )
        second = self.client.post(
            f"/api/stock-entries/{self.entry['id']}/cancel",
            headers={"Idempotency-Key": "cancel-entry-1"},
            json=payload,
        )
        self.assertEqual(first.status_code, 200, first.get_json())
        self.assertEqual(second.status_code, 200, second.get_json())
        with server.connect_db() as connection:
            product = connection.execute("SELECT stock FROM products").fetchone()
            movements = connection.execute(
                "SELECT COUNT(*) FROM purchase_stock_movements WHERE movement_type = 'entry_cancellation'"
            ).fetchone()[0]
            inventory = connection.execute(
                """
                SELECT real_before, real_after
                FROM inventory_movements
                WHERE movement_type = 'entry_cancellation'
                """
            ).fetchall()
            status = connection.execute(
                "SELECT status FROM payables WHERE id = ?", (payable["id"],)
            ).fetchone()[0]
        self.assertEqual(product["stock"], 0)
        self.assertEqual(movements, 1)
        self.assertEqual(
            [(row["real_before"], row["real_after"]) for row in inventory],
            [(3, 0)],
        )
        self.assertEqual(status, "cancelled")

    def test_entry_cancellation_is_blocked_after_real_payment(self):
        payable = self.link_payable()
        opening = self.client.post(
            "/api/cash-movements",
            json={
                "direction": "in",
                "type": "opening",
                "description": "Saldo para teste",
                "method": "pix",
                "amount": 100,
            },
        )
        self.assertEqual(opening.status_code, 201, opening.get_json())
        payment = self.client.post(
            f"/api/payables/{payable['id']}/pay",
            json={"amount": 10, "method": "pix"},
        )
        self.assertEqual(payment.status_code, 200, payment.get_json())
        response = self.client.post(
            f"/api/stock-entries/{self.entry['id']}/cancel",
            headers={"Idempotency-Key": "cancel-paid-entry"},
            json={"reason": "Tentativa inválida"},
        )
        self.assertEqual(response.status_code, 409)
        with server.connect_db() as connection:
            self.assertEqual(connection.execute("SELECT stock FROM products").fetchone()[0], 3)

    def test_supplier_return_creates_credit_and_fifo_credit_reduces_payable(self):
        payable = self.link_payable()
        response = self.client.post(
            "/api/supplier-returns",
            headers={"Idempotency-Key": "supplier-return-1"},
            json={
                "entryId": self.entry["id"],
                "reason": "Produto em desacordo",
                "items": [{"entryItemId": self.entry["items"][0]["id"], "quantity": 1}],
                "financial": {"creditAmount": 50},
            },
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        returned = response.get_json()["data"]["return"]
        self.assertEqual(returned["totalValue"], 50)
        self.assertEqual(returned["financialStatus"], "settled")
        usage = self.client.post(
            f"/api/payables/{payable['id']}/supplier-credit",
            headers={"Idempotency-Key": "credit-use-1"},
            json={"amount": 30},
        )
        self.assertEqual(usage.status_code, 200, usage.get_json())
        data = usage.get_json()["data"]
        self.assertEqual(data["payable"]["openAmount"], 120)
        self.assertEqual(data["credits"][0]["availableAmount"], 20)
        with server.connect_db() as connection:
            stock = connection.execute("SELECT stock FROM products").fetchone()[0]
            cash = connection.execute("SELECT COUNT(*) FROM cash_movements").fetchone()[0]
            inventory = connection.execute(
                """
                SELECT real_before, real_after
                FROM inventory_movements
                WHERE movement_type = 'supplier_return'
                """
            ).fetchall()
        self.assertEqual(stock, 2)
        self.assertEqual(cash, 0)
        self.assertEqual(
            [(row["real_before"], row["real_after"]) for row in inventory],
            [(3, 2)],
        )

    def test_return_limits_and_refund_cash_are_transactional(self):
        first = self.client.post(
            "/api/supplier-returns",
            headers={"Idempotency-Key": "return-cash"},
            json={
                "entryId": self.entry["id"],
                "reason": "Defeito",
                "items": [{"entryItemId": self.entry["items"][0]["id"], "quantity": 2}],
                "financial": {"cashRefund": 100},
            },
        )
        self.assertEqual(first.status_code, 201, first.get_json())
        invalid = self.client.post(
            "/api/supplier-returns",
            headers={"Idempotency-Key": "return-too-much"},
            json={
                "entryId": self.entry["id"],
                "reason": "Excesso",
                "items": [{"entryItemId": self.entry["items"][0]["id"], "quantity": 2}],
            },
        )
        self.assertEqual(invalid.status_code, 409)
        with server.connect_db() as connection:
            cash = connection.execute(
                "SELECT direction, method, amount FROM cash_movements"
            ).fetchall()
            self.assertEqual(connection.execute("SELECT stock FROM products").fetchone()[0], 1)
        self.assertEqual([(row["direction"], row["method"], row["amount"]) for row in cash], [("in", "cash", 100)])

    def test_credit_card_is_not_a_valid_payable_payment_method(self):
        payable = self.link_payable()
        response = self.client.post(
            f"/api/payables/{payable['id']}/pay",
            json={"amount": 10, "method": "credit"},
        )
        self.assertEqual(response.status_code, 400)
        with server.connect_db() as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM cash_movements").fetchone()[0], 0)

    def test_payable_abatement_updates_supplier_balance(self):
        payable = self.link_payable()
        response = self.client.post(
            "/api/supplier-returns",
            headers={"Idempotency-Key": "return-abatement"},
            json={
                "entryId": self.entry["id"],
                "reason": "Mercadoria divergente",
                "items": [{"entryItemId": self.entry["items"][0]["id"], "quantity": 1}],
                "financial": {
                    "payableAbatements": [{"payableId": payable["id"], "amount": 50}]
                },
            },
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        supplier = self.client.get(
            f"/api/suppliers/{self.supplier['id']}"
        ).get_json()["data"]["supplier"]
        self.assertEqual(supplier["openAmount"], 100)

    def test_pending_return_cancellation_restores_stock_once(self):
        created = self.client.post(
            "/api/supplier-returns",
            headers={"Idempotency-Key": "return-to-cancel"},
            json={
                "entryId": self.entry["id"],
                "reason": "Envio incorreto",
                "items": [{"entryItemId": self.entry["items"][0]["id"], "quantity": 1}],
            },
        )
        return_id = created.get_json()["data"]["return"]["id"]
        first = self.client.post(f"/api/supplier-returns/{return_id}/cancel")
        second = self.client.post(f"/api/supplier-returns/{return_id}/cancel")
        self.assertEqual(first.status_code, 200, first.get_json())
        self.assertEqual(second.status_code, 200, second.get_json())
        with server.connect_db() as connection:
            stock = connection.execute("SELECT stock FROM products").fetchone()[0]
            movements = connection.execute(
                """
                SELECT COUNT(*) FROM purchase_stock_movements
                WHERE movement_type = 'supplier_return_cancellation'
                """
            ).fetchone()[0]
            inventory = connection.execute(
                """
                SELECT movement_type, real_before, real_after
                FROM inventory_movements
                WHERE movement_type IN (
                    'supplier_return', 'supplier_return_cancellation'
                )
                ORDER BY created_at, id
                """
            ).fetchall()
        self.assertEqual(stock, 3)
        self.assertEqual(movements, 1)
        self.assertEqual(
            sorted(
                (row["movement_type"], row["real_before"], row["real_after"])
                for row in inventory
            ),
            [
                ("supplier_return", 3, 2),
                ("supplier_return_cancellation", 2, 3),
            ],
        )

    def test_entry_payable_uses_postgresql_lock_path(self):
        adapter = _PostgresPathOnSQLite(server.DB_PATH)
        with (
            server.app.test_request_context(
                f"/api/stock-entries/{self.entry['id']}/payables",
                method="POST",
            ),
            mock.patch.object(server, "USE_POSTGRES", True),
            mock.patch.object(server, "connect_db", return_value=adapter),
        ):
            server.session["user"] = {
                "id": "operator", "name": "Operador", "role": "operator"
            }
            entry, payables = server.create_entry_payables(
                self.entry["id"],
                {"amount": 150, "dueDate": "2026-08-22"},
            )
        self.assertEqual(len(payables), 1)
        self.assertEqual(entry["financial"]["payableTotal"], 150)
        self.assertTrue(any("FOR UPDATE" in sql for sql in adapter.statements))

    def test_audit_failure_rolls_back_supplier_return(self):
        with mock.patch.object(server, "record_audit", side_effect=RuntimeError("audit")):
            with self.assertRaises(RuntimeError):
                with server.app.test_request_context(
                    "/api/supplier-returns", method="POST"
                ):
                    server.session["user"] = {
                        "id": "operator", "name": "Operador", "role": "operator"
                    }
                    server.create_supplier_return(
                        {
                            "entryId": self.entry["id"],
                            "reason": "Rollback",
                            "items": [{
                                "entryItemId": self.entry["items"][0]["id"],
                                "quantity": 1,
                            }],
                        },
                        "return-rollback",
                    )
        with server.connect_db() as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM supplier_returns").fetchone()[0], 0)
            self.assertEqual(
                connection.execute(
                    """
                    SELECT COUNT(*) FROM inventory_movements
                    WHERE movement_type = 'supplier_return'
                    """
                ).fetchone()[0],
                0,
            )
            self.assertEqual(connection.execute("SELECT stock FROM products").fetchone()[0], 3)


if __name__ == "__main__":
    unittest.main()
