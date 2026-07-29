from __future__ import annotations

import gc
import json
import os
import sqlite3
import tempfile
import unittest
from unittest import mock

from database_migrations.migrations.v010_transactional_sales import MIGRATION_010
from database_migrations.runner import run_database_migrations
from environment_config import EnvironmentConfig
import server


AUTHORIZED_ENV = {
    "APP_ENV": "development",
    "MOVA_ALLOW_MIGRATIONS": "true",
}


class _EmptyResult:
    def fetchone(self):
        return None

    def fetchall(self):
        return []


class _PostgresPathOnSQLite:
    def __init__(self, path: str):
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.statements: list[str] = []

    def execute(self, sql, params=()):
        self.statements.append(sql)
        if "pg_advisory_xact_lock" in sql:
            return _EmptyResult()
        return self.connection.execute(sql.replace(" FOR UPDATE", ""), params)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        if exc_type:
            self.connection.rollback()
        else:
            self.connection.commit()
        self.connection.close()


class SaleBusinessRulesTest(unittest.TestCase):
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
        server.DB_PATH = os.path.join(self.temp_dir.name, "sales.db")
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
            connection.execute(
                "INSERT INTO app_state (id, data, updated_at) VALUES (1, ?, ?)",
                (
                    json.dumps(server.default_state(), ensure_ascii=False),
                    "2026-07-25T10:00:00+00:00",
                ),
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
        self.authenticate("operator")
        self.brand = self.create_catalog("/api/brands", "Mova")
        self.category = self.create_catalog("/api/categories", "Fitness")
        self.size = self.create_catalog("/api/sizes", "M")
        self.color = self.create_catalog("/api/colors", "Preto")
        self.supplier = self.client.post(
            "/api/suppliers",
            json={
                "name": "Fornecedor Venda",
                "email": "fornecedor@example.test",
            },
        ).get_json()["data"]
        self.customer = self.client.post(
            "/api/customers",
            json={
                "name": "Cliente Venda",
                "cpf": "52998224725",
                "phone": "48999991111",
                "email": "cliente@example.test",
                "limit": 500,
            },
        ).get_json()["data"]
        self.product = self.create_product()

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

    def create_catalog(self, endpoint: str, name: str) -> dict:
        response = self.client.post(endpoint, json={"name": name})
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()["data"]

    def create_product(self) -> dict:
        response = self.client.post(
            "/api/stock-entries",
            headers={"Idempotency-Key": "sale-product-opening"},
            json={
                "quantity": 5,
                "product": {
                    "barcode": "789900000101",
                    "name": "Legging Venda",
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
        return response.get_json()["data"]["product"]

    def create_card_modality(
        self,
        method: str = "credit",
        installments: int = 3,
        tax_percent: float = 2.5,
        receivable_days: int = 2,
    ) -> dict:
        self.authenticate("admin")
        response = self.client.post(
            "/api/card-modalities",
            json={
                "method": method,
                "installments": installments,
                "taxPercent": tax_percent,
                "receivableDays": receivable_days,
                "validFrom": "2020-01-01T00:00:00+00:00",
                "validUntil": "",
                "status": "active",
            },
        )
        self.authenticate("operator")
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()["data"]

    def sale_payload(self, **overrides) -> dict:
        payload = {
            "customerId": self.customer["id"],
            "items": [{
                "productId": self.product["id"],
                "quantity": 1,
                "practicedUnitPrice": 100,
                "unitDiscount": 0,
                "unitAddition": 0,
                "unitCost": 0.01,
            }],
            "discount": 0,
            "addition": 0,
            "payments": [{"method": "cash", "amount": 100}],
        }
        payload.update(overrides)
        return payload

    def post_sale(self, key: str, payload: dict | None = None):
        return self.client.post(
            "/api/sales",
            headers={"Idempotency-Key": key},
            json=payload or self.sale_payload(),
        )

    def scalar(self, sql: str, params=()):
        with sqlite3.connect(server.DB_PATH) as connection:
            return connection.execute(sql, params).fetchone()[0]

    def row(self, sql: str, params=()) -> sqlite3.Row:
        with sqlite3.connect(server.DB_PATH) as connection:
            connection.row_factory = sqlite3.Row
            return connection.execute(sql, params).fetchone()

    def test_migration_is_additive_and_cross_database(self):
        self.assertEqual(MIGRATION_010.version, 10)
        self.assertEqual(
            MIGRATION_010.sqlite_statements,
            MIGRATION_010.postgresql_statements,
        )
        self.assertFalse(any(
            statement.lstrip().upper().startswith(("DROP ", "DELETE "))
            for statement in MIGRATION_010.sqlite_statements
        ))
        self.assertEqual(self.scalar("SELECT MAX(version) FROM schema_migrations"), 18)
        self.assertEqual(
            self.scalar(
                "SELECT COUNT(*) FROM sqlite_master "
                "WHERE type = 'table' AND name = 'sale_sequences'"
            ),
            1,
        )

    def test_requires_session_and_idempotency_key(self):
        with self.client.session_transaction() as flask_session:
            flask_session.clear()
        response = self.post_sale("no-session")
        self.assertEqual(response.status_code, 401)
        self.authenticate("operator")
        response = self.client.post("/api/sales", json=self.sale_payload())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["code"], "IDEMPOTENCY_KEY_REQUIRED")
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM sales"), 0)

    def test_cash_pix_mixed_sale_is_atomic_and_uses_server_snapshots(self):
        payload = self.sale_payload(
            id="CLIENT-SALE",
            createdAt="2000-01-01T00:00:00Z",
            items=[{
                "productId": self.product["id"],
                "quantity": 2,
                "practicedUnitPrice": 110,
                "unitDiscount": 5,
                "unitAddition": 2,
                "unitCost": 0.01,
            }],
            discount=4,
            addition=10,
            payments=[
                {"method": "cash", "amount": 100, "tenderedAmount": 120},
                {"method": "pix", "amount": 120},
            ],
        )
        with (
            mock.patch.object(server, "init_db", side_effect=AssertionError),
            mock.patch.object(server, "write_state", side_effect=AssertionError),
            mock.patch.object(
                server, "sync_business_tables", side_effect=AssertionError
            ),
            mock.patch.object(server, "sync_sale_to_state", side_effect=AssertionError),
        ):
            response = self.post_sale("mixed-sale", payload)
        self.assertEqual(response.status_code, 201, response.get_json())
        result = response.get_json()["data"]
        sale = result["sale"]
        self.assertEqual(sale["id"], "VENDA001")
        self.assertNotEqual(sale["createdAt"], payload["createdAt"])
        self.assertEqual(sale["subtotal"], 214)
        self.assertEqual(sale["total"], 220)
        self.assertEqual(sale["costTotal"], 100)
        self.assertEqual(sale["changeAmount"], 20)
        self.assertEqual(self.scalar(
            "SELECT stock FROM products WHERE id = ?", (self.product["id"],)
        ), 3)
        item = self.row("SELECT * FROM sale_items WHERE sale_id = ?", (sale["id"],))
        self.assertEqual(item["unit_cost"], 50)
        self.assertEqual(item["original_unit_price"], 100)
        self.assertEqual(item["practiced_unit_price"], 110)
        self.assertEqual(item["final_unit_price"], 107)
        self.assertEqual(item["allocated_global_addition"], 10)
        self.assertEqual(item["allocated_global_discount"], 4)
        self.assertEqual(item["net_total"], 220)
        self.assertEqual(self.scalar(
            "SELECT COALESCE(SUM(amount), 0) FROM cash_movements "
            "WHERE ref_id = ?", (sale["id"],)
        ), 220)
        self.assertEqual(self.scalar(
            "SELECT COUNT(*) FROM inventory_movements WHERE reference_id = ?",
            (sale["id"],),
        ), 1)
        self.assertEqual(self.scalar(
            "SELECT COUNT(*) FROM audit_logs WHERE module = 'sale' AND ref_id = ?",
            (sale["id"],),
        ), 1)
        state = json.loads(self.scalar("SELECT data FROM app_state WHERE id = 1"))
        self.assertEqual(state["sales"][0]["id"], sale["id"])

    def test_idempotent_replay_and_conflict_do_not_duplicate_effects(self):
        first = self.post_sale("same-sale")
        replay = self.post_sale("same-sale")
        self.assertEqual(first.status_code, 201, first.get_json())
        self.assertEqual(replay.status_code, 200, replay.get_json())
        self.assertEqual(first.get_json()["data"], replay.get_json()["data"])
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM sales"), 1)
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM sale_payments"), 1)
        self.assertEqual(self.scalar(
            "SELECT stock FROM products WHERE id = ?", (self.product["id"],)
        ), 4)
        changed = self.sale_payload(discount=1, payments=[
            {"method": "cash", "amount": 99}
        ])
        conflict = self.post_sale("same-sale", changed)
        self.assertEqual(conflict.status_code, 409)
        self.assertEqual(conflict.get_json()["code"], "IDEMPOTENCY_CONFLICT")

    def test_card_uses_effective_modality_snapshot_and_one_net_receivable(self):
        modality = self.create_card_modality()
        options = self.client.get("/api/sales/card-modalities")
        self.assertEqual(options.status_code, 200)
        self.assertEqual(len(options.get_json()["data"]), 1)
        response = self.post_sale(
            "card-sale",
            self.sale_payload(payments=[{
                "method": "credit",
                "amount": 100,
                "cardModalityId": modality["cardModalityId"],
            }]),
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        sale_id = response.get_json()["data"]["sale"]["id"]
        payment = self.row(
            "SELECT * FROM sale_payments WHERE sale_id = ?", (sale_id,)
        )
        receivable = self.row(
            "SELECT * FROM receivables WHERE sale_id = ?", (sale_id,)
        )
        self.assertEqual(payment["installments"], 3)
        self.assertEqual(payment["tax_percent"], 2.5)
        self.assertEqual(payment["gross_amount"], 100)
        self.assertEqual(payment["fee_amount"], 2.5)
        self.assertEqual(payment["net_amount"], 97.5)
        self.assertEqual(receivable["amount"], 97.5)
        self.assertEqual(receivable["gross_amount"], 100)
        self.assertEqual(receivable["card_modality_id"], modality["cardModalityId"])
        self.assertEqual(self.scalar(
            "SELECT COUNT(*) FROM receivables WHERE sale_id = ?", (sale_id,)
        ), 1)
        self.assertEqual(self.scalar(
            "SELECT COUNT(*) FROM cash_movements WHERE ref_id = ?", (sale_id,)
        ), 0)

    def test_store_credit_requires_identified_eligible_customer(self):
        payment = [{"method": "storeCredit", "amount": 100, "installments": 2}]
        response = self.post_sale(
            "store-credit",
            self.sale_payload(
                payments=payment,
                storeCreditFirstDueDate="2099-01-31",
            ),
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        sale_id = response.get_json()["data"]["sale"]["id"]
        rows = []
        with sqlite3.connect(server.DB_PATH) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                "SELECT * FROM receivables WHERE sale_id = ? ORDER BY due_date",
                (sale_id,),
            ).fetchall()
        self.assertEqual([row["installment"] for row in rows], ["1/2", "2/2"])
        self.assertEqual([row["amount"] for row in rows], [50, 50])
        self.assertEqual(
            [row["due_date"] for row in rows],
            ["2099-01-31", "2099-02-28"],
        )
        self.assertTrue(all(
            row["original_due_date"] == row["due_date"]
            and row["open_amount"] == row["amount"]
            for row in rows
        ))

        blank_customer = self.post_sale(
            "default-credit",
            self.sale_payload(customerId="", payments=payment),
        )
        self.assertEqual(blank_customer.status_code, 400)
        with server.connect_db() as connection:
            connection.execute(
                "UPDATE customers SET status = 'blocked' WHERE id = ?",
                (self.customer["id"],),
            )
        blocked = self.post_sale(
            "blocked-credit",
            self.sale_payload(payments=payment),
        )
        self.assertEqual(blocked.status_code, 409)

    def test_store_credit_limit_requires_explicit_authorization_and_is_raised(self):
        with server.connect_db() as connection:
            connection.execute(
                "UPDATE customers SET credit_limit = 50 WHERE id = ?",
                (self.customer["id"],),
            )
        payments = [{"method": "storeCredit", "amount": 100, "installments": 3}]
        rejected = self.post_sale(
            "credit-limit-rejected",
            self.sale_payload(payments=payments),
        )
        self.assertEqual(rejected.status_code, 409, rejected.get_json())
        self.assertEqual(rejected.get_json()["code"], "CREDIT_LIMIT_EXCEEDED")
        self.assertEqual(
            self.scalar("SELECT COUNT(*) FROM sales"),
            0,
        )

        accepted = self.post_sale(
            "credit-limit-authorized",
            self.sale_payload(
                payments=payments,
                authorizeCreditLimit=True,
                storeCreditFirstDueDate="2099-01-31",
            ),
        )
        self.assertEqual(accepted.status_code, 201, accepted.get_json())
        self.assertEqual(
            self.scalar(
                "SELECT credit_limit FROM customers WHERE id = ?",
                (self.customer["id"],),
            ),
            100,
        )
        self.assertEqual(
            self.scalar(
                "SELECT COUNT(*) FROM customer_credit_limit_history "
                "WHERE customer_id = ?",
                (self.customer["id"],),
            ),
            1,
        )
        self.assertEqual(
            self.scalar(
                "SELECT COUNT(*) FROM receivables WHERE sale_id = ?",
                (accepted.get_json()["data"]["sale"]["id"],),
            ),
            3,
        )

    def test_store_credit_rejects_more_than_three_installments(self):
        response = self.post_sale(
            "credit-four-installments",
            self.sale_payload(
                payments=[{
                    "method": "storeCredit",
                    "amount": 100,
                    "installments": 4,
                }],
            ),
        )
        self.assertEqual(response.status_code, 400, response.get_json())

    def test_conditional_reservation_blocks_unavailable_quantity(self):
        state = json.loads(self.scalar("SELECT data FROM app_state WHERE id = 1"))
        state["conditionals"] = [{
            "id": "COND001",
            "status": "open",
            "items": [{"productId": self.product["id"], "quantity": 5}],
        }]
        with server.connect_db() as connection:
            connection.execute(
                "UPDATE app_state SET data = ? WHERE id = 1",
                (json.dumps(state, ensure_ascii=False),),
            )
        response = self.post_sale("reserved-stock")
        self.assertEqual(response.status_code, 409)
        self.assertEqual(
            response.get_json()["code"],
            "INSUFFICIENT_AVAILABLE_STOCK",
        )
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM sales"), 0)

    def test_audit_failure_rolls_back_every_effect(self):
        with mock.patch.object(
            server, "record_audit", side_effect=RuntimeError("audit failed")
        ):
            response = self.post_sale("rollback-sale")
        self.assertEqual(response.status_code, 500)
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM sales"), 0)
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM cash_movements"), 0)
        self.assertEqual(self.scalar(
            "SELECT stock FROM products WHERE id = ?", (self.product["id"],)
        ), 5)
        state = json.loads(self.scalar("SELECT data FROM app_state WHERE id = 1"))
        self.assertEqual(state.get("sales"), [])

    def test_postgresql_path_locks_sale_and_app_state(self):
        adapters = []

        def connect():
            adapter = _PostgresPathOnSQLite(server.DB_PATH)
            adapters.append(adapter)
            return adapter

        with (
            mock.patch.object(server, "USE_POSTGRES", True),
            mock.patch.object(server, "connect_db", side_effect=connect),
        ):
            with server.app.test_request_context():
                from flask import session

                session["user"] = {
                    "id": "operator",
                    "name": "Operator",
                    "role": "operator",
                    "active": True,
                }
                result, replayed = server.persist_sale_creation(
                    self.sale_payload(),
                    "postgres-path",
                )
        self.assertFalse(replayed)
        self.assertEqual(result["sale"]["id"], "VENDA001")
        statements = "\n".join(
            statement
            for adapter in adapters
            for statement in adapter.statements
        )
        self.assertIn("pg_advisory_xact_lock", statements)
        self.assertIn("FOR UPDATE", statements)


if __name__ == "__main__":
    unittest.main()
