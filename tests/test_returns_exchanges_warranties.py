from __future__ import annotations

import gc
import io
import json
import os
import sqlite3
import tempfile
import unittest
from unittest import mock

from database_migrations.migrations.v013_returns_exchanges_warranties import (
    MIGRATION_013,
)
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


class ReturnsExchangesWarrantiesTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original = (
            server.ENVIRONMENT,
            server.USE_POSTGRES,
            server.DATABASE_URL,
            server.DB_PATH,
            server.PRODUCT_UPLOAD_DIR,
            server.USE_CLOUDINARY,
        )
        server.ENVIRONMENT = EnvironmentConfig(
            "development", "configured", False, False
        )
        server.USE_POSTGRES = False
        server.DATABASE_URL = ""
        server.DB_PATH = os.path.join(self.temp_dir.name, "after-sales.db")
        server.PRODUCT_UPLOAD_DIR = os.path.join(
            self.temp_dir.name,
            "uploads",
        )
        server.USE_CLOUDINARY = False
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
            for identifier, role in (
                ("operator", "operator"),
                ("admin", "admin"),
            ):
                connection.execute(
                    """
                    INSERT INTO users (
                        id, store_id, name, login, password_hash,
                        role, active, updated_at
                    ) VALUES (?, 'matriz', ?, ?, 'not-used', ?, 1, ?)
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
        self.brand = self.catalog("/api/brands", "Mova")
        self.category = self.catalog("/api/categories", "Fitness")
        self.size = self.catalog("/api/sizes", "M")
        self.color = self.catalog("/api/colors", "Preto")
        supplier_response = self.client.post(
            "/api/suppliers",
            json={"name": "Fornecedor Pos Venda"},
        )
        self.assertEqual(supplier_response.status_code, 201)
        self.supplier = supplier_response.get_json()["data"]
        customer_response = self.client.post(
            "/api/customers",
            json={
                "name": "Cliente Pos Venda",
                "cpf": "52998224725",
                "phone": "48999991111",
                "limit": 1000,
            },
        )
        self.assertEqual(customer_response.status_code, 201)
        self.customer = customer_response.get_json()["data"]
        self.product = self.product_entry(
            "789900000201", "Legging Original", 10, 50, 100
        )
        self.replacement = self.product_entry(
            "789900000202", "Legging Substituta", 10, 60, 120
        )

    def tearDown(self):
        (
            server.ENVIRONMENT,
            server.USE_POSTGRES,
            server.DATABASE_URL,
            server.DB_PATH,
            server.PRODUCT_UPLOAD_DIR,
            server.USE_CLOUDINARY,
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

    def catalog(self, endpoint: str, name: str) -> dict:
        response = self.client.post(endpoint, json={"name": name})
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()["data"]

    def product_entry(
        self,
        barcode: str,
        name: str,
        quantity: int,
        cost: float,
        price: float,
    ) -> dict:
        response = self.client.post(
            "/api/stock-entries",
            headers={"Idempotency-Key": f"entry-{barcode}"},
            json={
                "quantity": quantity,
                "product": {
                    "barcode": barcode,
                    "name": name,
                    "gender": "Feminino",
                    "brandId": self.brand["id"],
                    "categoryId": self.category["id"],
                    "sizeId": self.size["id"],
                    "colorId": self.color["id"],
                    "supplierId": self.supplier["id"],
                    "cost": cost,
                    "price": price,
                    "minStock": 1,
                    "active": True,
                },
            },
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()["data"]["product"]

    def create_sale(self, key: str, payments=None, quantity=2, discount=20):
        response = self.client.post(
            "/api/sales",
            headers={"Idempotency-Key": key},
            json={
                "customerId": self.customer["id"],
                "items": [{
                    "productId": self.product["id"],
                    "quantity": quantity,
                    "practicedUnitPrice": 100,
                    "unitDiscount": 0,
                    "unitAddition": 0,
                }],
                "discount": discount,
                "addition": 0,
                "payments": payments or [{
                    "method": "cash",
                    "amount": quantity * 100 - discount,
                }],
            },
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()["data"]["sale"]

    def return_payload(self, sale: dict, quantity=1, condition="resellable"):
        return {
            "saleId": sale["id"],
            "reason": "Desistencia",
            "notes": "Operacao de teste",
            "items": [{
                "saleItemId": sale["items"][0]["id"],
                "quantity": quantity,
                "physicalCondition": condition,
                "unitPrice": 0.01,
            }],
        }

    def scalar(self, sql: str, params=()):
        with sqlite3.connect(server.DB_PATH) as connection:
            return connection.execute(sql, params).fetchone()[0]

    def row(self, sql: str, params=()):
        with sqlite3.connect(server.DB_PATH) as connection:
            connection.row_factory = sqlite3.Row
            return connection.execute(sql, params).fetchone()

    def test_migration_is_additive_and_cross_database(self):
        self.assertEqual(MIGRATION_013.version, 13)
        self.assertEqual(
            MIGRATION_013.sqlite_statements,
            MIGRATION_013.postgresql_statements,
        )
        self.assertFalse(any(
            statement.lstrip().upper().startswith(("DROP ", "DELETE "))
            for statement in MIGRATION_013.sqlite_statements
        ))
        for table in (
            "sale_return_allocations",
            "sale_return_receivable_reductions",
            "exchanges",
            "exchange_cancellations",
            "exchange_return_items",
            "exchange_new_items",
            "warranties",
            "warranty_events",
        ):
            self.assertEqual(
                self.scalar(
                    "SELECT COUNT(*) FROM sqlite_master "
                    "WHERE type = 'table' AND name = ?",
                    (table,),
                ),
                1,
            )

    def test_partial_return_uses_historical_net_and_is_idempotent(self):
        sale = self.create_sale("return-sale")
        payload = self.return_payload(sale)
        response = self.client.post(
            "/api/returns",
            headers={"Idempotency-Key": "return-one"},
            json=payload,
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        result = response.get_json()["data"]
        self.assertEqual(result["return"]["netTotal"], 90)
        self.assertEqual(result["return"]["items"][0]["unitPrice"], 90)
        self.assertEqual(result["products"][0]["stock"], 9)
        self.assertEqual(result["cash"][0]["direction"], "out")
        self.assertEqual(result["cash"][0]["amount"], 90)
        replay = self.client.post(
            "/api/returns",
            headers={"Idempotency-Key": "return-one"},
            json=payload,
        )
        self.assertEqual(replay.status_code, 200)
        self.assertTrue(replay.get_json()["replayed"])
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM sale_returns"), 1)
        self.assertEqual(
            self.scalar(
                "SELECT stock FROM products WHERE id = ?",
                (self.product["id"],),
            ),
            9,
        )

    def test_previous_return_limits_quantity_and_damaged_item_is_not_restocked(self):
        sale = self.create_sale("return-limit-sale")
        first = self.client.post(
            "/api/returns",
            headers={"Idempotency-Key": "return-limit-one"},
            json=self.return_payload(sale, condition="damaged"),
        )
        self.assertEqual(first.status_code, 201, first.get_json())
        self.assertFalse(
            first.get_json()["data"]["return"]["items"][0]["restocked"]
        )
        self.assertEqual(
            self.scalar(
                "SELECT stock FROM products WHERE id = ?",
                (self.product["id"],),
            ),
            8,
        )
        exceeded = self.client.post(
            "/api/returns",
            headers={"Idempotency-Key": "return-limit-two"},
            json=self.return_payload(sale, quantity=2),
        )
        self.assertEqual(exceeded.status_code, 409)
        self.assertEqual(
            exceeded.get_json()["code"],
            "RETURN_QUANTITY_EXCEEDED",
        )

    def test_mixed_payment_return_is_allocated_by_original_composition(self):
        sale = self.create_sale(
            "mixed-return-sale",
            payments=[
                {"method": "cash", "amount": 90},
                {"method": "pix", "amount": 90},
            ],
        )
        response = self.client.post(
            "/api/returns",
            headers={"Idempotency-Key": "mixed-return"},
            json=self.return_payload(sale),
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        result = response.get_json()["data"]
        self.assertEqual(
            sorted((item["method"], item["amount"]) for item in result["cash"]),
            [("cash", 45), ("pix", 45)],
        )
        self.assertEqual(
            sorted(
                (item["method"], item["grossAmount"])
                for item in result["allocations"]
            ),
            [("cash", 45), ("pix", 45)],
        )

    def test_pending_card_return_reduces_receivable_without_cash_output(self):
        self.authenticate("admin")
        modality = self.client.post(
            "/api/card-modalities",
            json={
                "method": "credit",
                "installments": 1,
                "taxPercent": 0,
                "receivableDays": 1,
                "validFrom": "2020-01-01T00:00:00+00:00",
                "status": "active",
            },
        ).get_json()["data"]
        self.authenticate("operator")
        sale = self.create_sale(
            "card-return-sale",
            payments=[{
                "method": "credit",
                "amount": 180,
                "cardModalityId": modality["cardModalityId"],
            }],
        )
        response = self.client.post(
            "/api/returns",
            headers={"Idempotency-Key": "card-return"},
            json=self.return_payload(sale),
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        result = response.get_json()["data"]
        self.assertEqual(result["cash"], [])
        self.assertEqual(result["allocations"][0]["pendingReduction"], 90)
        receivable = self.row(
            "SELECT open_amount, return_reduction_total FROM receivables "
            "WHERE sale_id = ?",
            (sale["id"],),
        )
        self.assertEqual(receivable["open_amount"], 90)
        self.assertEqual(receivable["return_reduction_total"], 90)

    def test_store_credit_return_reduces_nearest_installments_and_preserves_details(self):
        sale = self.create_sale(
            "store-credit-return-sale",
            payments=[{
                "method": "storeCredit",
                "amount": 180,
                "installments": 3,
            }],
        )
        response = self.client.post(
            "/api/returns",
            headers={"Idempotency-Key": "store-credit-return"},
            json=self.return_payload(sale),
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        reductions = response.get_json()["data"]["return"][
            "receivableReductions"
        ]
        self.assertEqual([item["amount"] for item in reductions], [60, 30])
        self.assertEqual(
            [item["openAmountAfter"] for item in reductions],
            [0, 30],
        )
        self.assertEqual(
            self.scalar(
                "SELECT COUNT(*) FROM sale_return_receivable_reductions"
            ),
            2,
        )
        state = json.loads(
            self.row("SELECT data FROM app_state WHERE id = 1")["data"]
        )
        mirrored = [
            item
            for item in state["receivables"]
            if item.get("saleId") == sale["id"]
        ]
        self.assertEqual(len(mirrored), 3)
        self.assertTrue(all("customerName" in item for item in mirrored))
        self.assertEqual(
            sum(float(item["openAmount"]) for item in mirrored),
            90,
        )

    def test_exchange_creates_return_linked_sale_and_atomic_stock(self):
        sale = self.create_sale(
            "exchange-sale",
            quantity=1,
            discount=0,
        )
        response = self.client.post(
            "/api/exchanges",
            headers={"Idempotency-Key": "exchange-one"},
            json={
                "saleId": sale["id"],
                "reason": "Tamanho",
                "returnedItems": [{
                    "saleItemId": sale["items"][0]["id"],
                    "quantity": 1,
                    "physicalCondition": "resellable",
                }],
                "newItems": [{
                    "productId": self.replacement["id"],
                    "quantity": 1,
                    "practicedUnitPrice": 120,
                }],
                "payments": [{"method": "pix", "amount": 20}],
            },
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        result = response.get_json()["data"]
        self.assertEqual(result["exchange"]["differenceDirection"], "pay")
        self.assertEqual(result["exchange"]["differenceAmount"], 20)
        self.assertTrue(result["exchange"]["linkedSaleId"].startswith("VENDA"))
        self.assertEqual(result["cash"][0]["amount"], 20)
        self.assertEqual(
            self.scalar(
                "SELECT stock FROM products WHERE id = ?",
                (self.product["id"],),
            ),
            10,
        )
        self.assertEqual(
            self.scalar(
                "SELECT stock FROM products WHERE id = ?",
                (self.replacement["id"],),
            ),
            9,
        )
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM exchanges"), 1)
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM sale_returns"), 1)
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM sales"), 2)

    def test_exchange_difference_accepts_mixed_payment_and_store_credit(self):
        sale = self.create_sale(
            "exchange-mixed-sale",
            quantity=1,
            discount=0,
        )
        response = self.client.post(
            "/api/exchanges",
            headers={"Idempotency-Key": "exchange-mixed"},
            json={
                "saleId": sale["id"],
                "reason": "Modelo",
                "returnedItems": [{
                    "saleItemId": sale["items"][0]["id"],
                    "quantity": 1,
                    "physicalCondition": "resellable",
                }],
                "newItems": [{
                    "productId": self.replacement["id"],
                    "quantity": 1,
                    "practicedUnitPrice": 160,
                }],
                "payments": [
                    {"method": "pix", "amount": 20},
                    {
                        "method": "storeCredit",
                        "amount": 40,
                        "installments": 2,
                    },
                ],
                "storeCreditInstallments": 2,
                "storeCreditFirstDueDate": "2026-08-25",
            },
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        result = response.get_json()["data"]
        self.assertEqual(result["exchange"]["differenceAmount"], 60)
        self.assertEqual(
            sorted(
                (item["method"], item["amount"])
                for item in result["sale"]["payments"]
                if item["method"] != "exchangeCredit"
            ),
            [("pix", 20), ("storeCredit", 40)],
        )
        self.assertEqual(len(result["receivables"]), 2)
        self.assertEqual(
            [item["amount"] for item in result["receivables"]],
            [20, 20],
        )
        self.assertEqual(
            [item["dueDate"] for item in result["receivables"]],
            ["2026-08-25", "2026-09-25"],
        )

    def test_received_card_return_refunds_only_traceable_received_value(self):
        self.authenticate("admin")
        modality = self.client.post(
            "/api/card-modalities",
            json={
                "method": "credit",
                "installments": 1,
                "taxPercent": 0,
                "receivableDays": 1,
                "validFrom": "2020-01-01T00:00:00+00:00",
                "status": "active",
            },
        ).get_json()["data"]
        self.authenticate("operator")
        sale = self.create_sale(
            "received-card-return-sale",
            payments=[{
                "method": "credit",
                "amount": 180,
                "cardModalityId": modality["cardModalityId"],
            }],
        )
        with server.connect_db() as connection:
            receivable = connection.execute(
                "SELECT id FROM receivables WHERE sale_id = ?",
                (sale["id"],),
            ).fetchone()
            connection.execute(
                """
                UPDATE receivables
                SET received = 180, open_amount = 0, status = 'received',
                    paid_at = ?, last_payment_at = ?
                WHERE id = ?
                """,
                (
                    "2026-07-25T12:00:00+00:00",
                    "2026-07-25T12:00:00+00:00",
                    receivable["id"],
                ),
            )
            connection.execute(
                """
                INSERT INTO receivable_payments (
                    id, store_id, receivable_id, sale_id, customer_id,
                    method, amount, created_at, note
                ) VALUES (?, 'matriz', ?, ?, ?, 'credit', 180, ?, ?)
                """,
                (
                    "received-card-payment",
                    receivable["id"],
                    sale["id"],
                    self.customer["id"],
                    "2026-07-25T12:00:00+00:00",
                    "Recebimento rastreavel",
                ),
            )
            with server.app.test_request_context():
                server.session["user"] = {
                    "id": "operator-returns",
                    "name": "Operador",
                }
                server.insert_cash_movement(
                    connection,
                    {
                        "id": "received-card-cash-entry",
                        "direction": "in",
                        "type": "bank_receipt",
                        "description": "Recebimento cartao rastreavel",
                        "method": "credit",
                        "amount": 180,
                        "refId": receivable["id"],
                        "originType": "receivable",
                        "originId": receivable["id"],
                        "createdAt": "2026-07-25T12:00:00+00:00",
                    },
                    "matriz",
                )
        response = self.client.post(
            "/api/returns",
            headers={"Idempotency-Key": "received-card-return"},
            json=self.return_payload(sale),
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        result = response.get_json()["data"]
        self.assertEqual(len(result["cash"]), 1)
        self.assertEqual(result["cash"][0]["direction"], "out")
        self.assertEqual(result["cash"][0]["method"], "credit")
        self.assertEqual(result["cash"][0]["amount"], 90)
        self.assertEqual(result["allocations"][0]["refundedAmount"], 90)

    def test_exchange_other_reason_requires_description(self):
        sale = self.create_sale(
            "exchange-other-reason-sale",
            quantity=1,
            discount=0,
        )
        response = self.client.post(
            "/api/exchanges",
            headers={"Idempotency-Key": "exchange-other-reason"},
            json={
                "saleId": sale["id"],
                "reason": "Outro",
                "returnedItems": [{
                    "saleItemId": sale["items"][0]["id"],
                    "quantity": 1,
                    "physicalCondition": "resellable",
                }],
                "newItems": [{
                    "productId": self.replacement["id"],
                    "quantity": 1,
                }],
                "payments": [{"method": "pix", "amount": 20}],
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM exchanges"), 0)

    def test_exchange_idempotency_rejects_same_key_with_other_content(self):
        sale = self.create_sale(
            "exchange-idempotency-sale",
            quantity=1,
            discount=0,
        )
        payload = {
            "saleId": sale["id"],
            "reason": "Tamanho",
            "returnedItems": [{
                "saleItemId": sale["items"][0]["id"],
                "quantity": 1,
                "physicalCondition": "resellable",
            }],
            "newItems": [{
                "productId": self.replacement["id"],
                "quantity": 1,
            }],
            "payments": [{"method": "pix", "amount": 20}],
        }
        first = self.client.post(
            "/api/exchanges",
            headers={"Idempotency-Key": "exchange-idempotency"},
            json=payload,
        )
        self.assertEqual(first.status_code, 201, first.get_json())
        conflicting = {
            **payload,
            "notes": "Conteudo diferente",
        }
        conflict = self.client.post(
            "/api/exchanges",
            headers={"Idempotency-Key": "exchange-idempotency"},
            json=conflicting,
        )
        self.assertEqual(conflict.status_code, 409)
        self.assertEqual(conflict.get_json()["code"], "IDEMPOTENCY_CONFLICT")
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM exchanges"), 1)

    def test_after_sales_routes_never_use_global_state_reconstruction(self):
        return_sale = self.create_sale("sentinel-return")
        exchange_sale = self.create_sale(
            "sentinel-exchange",
            quantity=1,
            discount=0,
        )
        warranty_sale = self.create_sale(
            "sentinel-warranty",
            quantity=1,
            discount=0,
        )
        with mock.patch.object(
            server,
            "write_state",
            side_effect=AssertionError("write_state must not be called"),
        ), mock.patch.object(
            server,
            "sync_business_tables",
            side_effect=AssertionError(
                "sync_business_tables must not be called"
            ),
        ):
            returned = self.client.post(
                "/api/returns",
                headers={"Idempotency-Key": "sentinel-return-op"},
                json=self.return_payload(return_sale),
            )
            self.assertEqual(returned.status_code, 201, returned.get_json())
            exchanged = self.client.post(
                "/api/exchanges",
                headers={"Idempotency-Key": "sentinel-exchange-op"},
                json={
                    "saleId": exchange_sale["id"],
                    "reason": "Tamanho",
                    "returnedItems": [{
                        "saleItemId": exchange_sale["items"][0]["id"],
                        "quantity": 1,
                        "physicalCondition": "resellable",
                    }],
                    "newItems": [{
                        "productId": self.replacement["id"],
                        "quantity": 1,
                    }],
                    "payments": [{"method": "pix", "amount": 20}],
                },
            )
            self.assertEqual(exchanged.status_code, 201, exchanged.get_json())
            warranty = self.client.post(
                "/api/warranties",
                headers={"Idempotency-Key": "sentinel-warranty-op"},
                json={
                    "saleId": warranty_sale["id"],
                    "saleItemId": warranty_sale["items"][0]["id"],
                    "quantity": 1,
                    "defectCategory": "Costura",
                    "defectDescription": "Costura aberta.",
                    "physicalLocation": "customer",
                },
            )
            self.assertEqual(warranty.status_code, 201, warranty.get_json())

    def test_exchange_audit_failure_rolls_back_all_effects(self):
        sale = self.create_sale(
            "exchange-rollback-sale",
            quantity=1,
            discount=0,
        )
        with mock.patch.object(
            server,
            "record_audit",
            side_effect=RuntimeError("audit failure"),
        ):
            response = self.client.post(
                "/api/exchanges",
                headers={"Idempotency-Key": "exchange-rollback"},
                json={
                    "saleId": sale["id"],
                    "reason": "Tamanho",
                    "returnedItems": [{
                        "saleItemId": sale["items"][0]["id"],
                        "quantity": 1,
                        "physicalCondition": "resellable",
                    }],
                    "newItems": [{
                        "productId": self.replacement["id"],
                        "quantity": 1,
                    }],
                    "payments": [{"method": "pix", "amount": 20}],
                },
            )
        self.assertEqual(response.status_code, 500)
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM exchanges"), 0)
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM sales"), 1)
        self.assertEqual(
            self.scalar(
                "SELECT stock FROM products WHERE id = ?",
                (self.product["id"],),
            ),
            9,
        )
        self.assertEqual(
            self.scalar(
                "SELECT stock FROM products WHERE id = ?",
                (self.replacement["id"],),
            ),
            10,
        )

    def test_warranty_lifecycle_and_supplier_location_rule(self):
        sale = self.create_sale(
            "warranty-sale",
            quantity=1,
            discount=0,
        )
        create = self.client.post(
            "/api/warranties",
            headers={"Idempotency-Key": "warranty-one"},
            json={
                "saleId": sale["id"],
                "saleItemId": sale["items"][0]["id"],
                "quantity": 1,
                "defectCategory": "Costura",
                "defectDescription": "Costura abriu no primeiro uso.",
                "physicalLocation": "customer",
                "photos": [{"url": "https://example.test/evidence.jpg"}],
            },
        )
        self.assertEqual(create.status_code, 201, create.get_json())
        warranty = create.get_json()["data"]["warranty"]
        blocked = self.client.post(
            f"/api/warranties/{warranty['id']}/events",
            json={
                "action": "send_supplier",
                "supplierId": self.supplier["id"],
            },
        )
        self.assertEqual(blocked.status_code, 409)
        received = self.client.post(
            f"/api/warranties/{warranty['id']}/events",
            json={"action": "receive_at_store"},
        )
        self.assertEqual(received.status_code, 200)
        sent = self.client.post(
            f"/api/warranties/{warranty['id']}/events",
            json={
                "action": "send_supplier",
                "supplierId": self.supplier["id"],
                "protocol": "PROTO-1",
            },
        )
        self.assertEqual(sent.status_code, 200, sent.get_json())
        self.assertEqual(sent.get_json()["data"]["warranty"]["status"], "supplier")
        approved = self.client.post(
            f"/api/warranties/{warranty['id']}/events",
            json={"action": "approve", "notes": "Aprovada."},
        )
        self.assertEqual(approved.status_code, 200)
        resolved = self.client.post(
            f"/api/warranties/{warranty['id']}/events",
            json={
                "action": "resolve_repair",
                "notes": "Costura refeita.",
                "awaitingCustomerDelivery": False,
            },
        )
        self.assertEqual(resolved.status_code, 200, resolved.get_json())
        self.assertEqual(
            resolved.get_json()["data"]["warranty"]["status"],
            "resolved",
        )
        self.assertGreaterEqual(
            len(resolved.get_json()["data"]["warranty"]["events"]),
            5,
        )

    def test_warranty_solution_requires_prior_approval(self):
        sale = self.create_sale(
            "warranty-approval-sale",
            quantity=1,
            discount=0,
        )
        created = self.client.post(
            "/api/warranties",
            headers={"Idempotency-Key": "warranty-approval"},
            json={
                "saleId": sale["id"],
                "saleItemId": sale["items"][0]["id"],
                "quantity": 1,
                "defectCategory": "Tecido",
                "defectDescription": "Tecido com falha visivel.",
                "physicalLocation": "store",
            },
        )
        self.assertEqual(created.status_code, 201, created.get_json())
        warranty_id = created.get_json()["data"]["warranty"]["id"]
        blocked = self.client.post(
            f"/api/warranties/{warranty_id}/events",
            json={
                "action": "resolve_repair",
                "notes": "Tentativa sem aprovacao.",
                "awaitingCustomerDelivery": False,
            },
        )
        self.assertEqual(blocked.status_code, 409)
        self.assertEqual(
            self.row(
                "SELECT status FROM warranties WHERE id = ?",
                (warranty_id,),
            )["status"],
            "open",
        )

    def test_exchange_cancellation_reverses_stock_finance_and_is_idempotent(self):
        sale = self.create_sale(
            "exchange-cancel-sale",
            quantity=1,
            discount=0,
        )
        exchanged = self.client.post(
            "/api/exchanges",
            headers={"Idempotency-Key": "exchange-cancel-create"},
            json={
                "saleId": sale["id"],
                "reason": "Tamanho",
                "returnedItems": [{
                    "saleItemId": sale["items"][0]["id"],
                    "quantity": 1,
                    "physicalCondition": "resellable",
                }],
                "newItems": [{
                    "productId": self.replacement["id"],
                    "quantity": 1,
                }],
                "payments": [{"method": "pix", "amount": 20}],
            },
        )
        self.assertEqual(exchanged.status_code, 201, exchanged.get_json())
        exchange = exchanged.get_json()["data"]["exchange"]
        linked_sale_id = exchange["linkedSaleId"]
        cancelled = self.client.post(
            f"/api/exchanges/{exchange['id']}/cancel",
            headers={"Idempotency-Key": "exchange-cancel-operation"},
            json={"reason": "Operacao registrada incorretamente."},
        )
        self.assertEqual(cancelled.status_code, 200, cancelled.get_json())
        result = cancelled.get_json()["data"]
        self.assertEqual(result["exchange"]["status"], "cancelled")
        self.assertEqual(result["return"]["status"], "cancelled")
        self.assertEqual(
            self.scalar(
                "SELECT status FROM sales WHERE id = ?",
                (linked_sale_id,),
            ),
            "cancelled",
        )
        self.assertEqual(
            self.scalar(
                "SELECT stock FROM products WHERE id = ?",
                (self.product["id"],),
            ),
            9,
        )
        self.assertEqual(
            self.scalar(
                "SELECT stock FROM products WHERE id = ?",
                (self.replacement["id"],),
            ),
            10,
        )
        self.assertEqual(
            [(item["direction"], item["method"], item["amount"]) for item in result["cash"]],
            [("out", "pix", 20)],
        )
        replay = self.client.post(
            f"/api/exchanges/{exchange['id']}/cancel",
            headers={"Idempotency-Key": "exchange-cancel-operation"},
            json={"reason": "Operacao registrada incorretamente."},
        )
        self.assertEqual(replay.status_code, 200, replay.get_json())
        self.assertTrue(replay.get_json()["replayed"])
        self.assertEqual(
            self.scalar("SELECT COUNT(*) FROM exchange_cancellations"),
            1,
        )

    def test_exchange_cancellation_restores_original_pending_store_credit(self):
        sale = self.create_sale(
            "exchange-refund-cancel-sale",
            payments=[{
                "method": "storeCredit",
                "amount": 100,
                "installments": 1,
            }],
            quantity=1,
            discount=0,
        )
        exchanged = self.client.post(
            "/api/exchanges",
            headers={"Idempotency-Key": "exchange-refund-create"},
            json={
                "saleId": sale["id"],
                "reason": "Modelo",
                "returnedItems": [{
                    "saleItemId": sale["items"][0]["id"],
                    "quantity": 1,
                    "physicalCondition": "resellable",
                }],
                "newItems": [{
                    "productId": self.replacement["id"],
                    "quantity": 1,
                    "practicedUnitPrice": 60,
                }],
            },
        )
        self.assertEqual(exchanged.status_code, 201, exchanged.get_json())
        exchange = exchanged.get_json()["data"]["exchange"]
        reduced = self.row(
            "SELECT open_amount, return_reduction_total FROM receivables "
            "WHERE sale_id = ?",
            (sale["id"],),
        )
        self.assertEqual(reduced["open_amount"], 60)
        self.assertEqual(reduced["return_reduction_total"], 40)
        cancelled = self.client.post(
            f"/api/exchanges/{exchange['id']}/cancel",
            headers={"Idempotency-Key": "exchange-refund-cancel"},
            json={"reason": "Cliente desistiu da troca."},
        )
        self.assertEqual(cancelled.status_code, 200, cancelled.get_json())
        restored = self.row(
            "SELECT open_amount, return_reduction_total, status "
            "FROM receivables WHERE sale_id = ?",
            (sale["id"],),
        )
        self.assertEqual(restored["open_amount"], 100)
        self.assertEqual(restored["return_reduction_total"], 0)
        self.assertEqual(restored["status"], "open")

    def test_exchange_cancellation_audit_failure_rolls_back(self):
        sale = self.create_sale(
            "exchange-cancel-rollback-sale",
            quantity=1,
            discount=0,
        )
        exchanged = self.client.post(
            "/api/exchanges",
            headers={"Idempotency-Key": "exchange-cancel-rollback-create"},
            json={
                "saleId": sale["id"],
                "reason": "Tamanho",
                "returnedItems": [{
                    "saleItemId": sale["items"][0]["id"],
                    "quantity": 1,
                    "physicalCondition": "resellable",
                }],
                "newItems": [{
                    "productId": self.replacement["id"],
                    "quantity": 1,
                }],
                "payments": [{"method": "pix", "amount": 20}],
            },
        )
        exchange = exchanged.get_json()["data"]["exchange"]
        with mock.patch.object(
            server,
            "record_audit",
            side_effect=RuntimeError("audit failure"),
        ):
            response = self.client.post(
                f"/api/exchanges/{exchange['id']}/cancel",
                headers={"Idempotency-Key": "exchange-cancel-rollback"},
                json={"reason": "Falha simulada."},
            )
        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            self.scalar(
                "SELECT status FROM exchanges WHERE id = ?",
                (exchange["id"],),
            ),
            "completed",
        )
        self.assertEqual(
            self.scalar("SELECT COUNT(*) FROM exchange_cancellations"),
            0,
        )
        self.assertEqual(
            self.scalar(
                "SELECT stock FROM products WHERE id = ?",
                (self.product["id"],),
            ),
            10,
        )
        self.assertEqual(
            self.scalar(
                "SELECT stock FROM products WHERE id = ?",
                (self.replacement["id"],),
            ),
            9,
        )

    def test_supplier_warranty_substitution_creates_traceable_stock_entry(self):
        sale = self.create_sale(
            "warranty-stock-replacement-sale",
            quantity=1,
            discount=0,
        )
        created = self.client.post(
            "/api/warranties",
            headers={"Idempotency-Key": "warranty-stock-replacement"},
            json={
                "saleId": sale["id"],
                "saleItemId": sale["items"][0]["id"],
                "quantity": 1,
                "defectCategory": "Tecido",
                "defectDescription": "Falha confirmada pelo fornecedor.",
                "physicalLocation": "store",
            },
        )
        warranty_id = created.get_json()["data"]["warranty"]["id"]
        sent = self.client.post(
            f"/api/warranties/{warranty_id}/events",
            json={
                "action": "send_supplier",
                "supplierId": self.supplier["id"],
                "protocol": "SUB-001",
            },
        )
        self.assertEqual(sent.status_code, 200, sent.get_json())
        approved = self.client.post(
            f"/api/warranties/{warranty_id}/events",
            json={"action": "approve", "notes": "Substituicao autorizada."},
        )
        self.assertEqual(approved.status_code, 200, approved.get_json())
        resolved = self.client.post(
            f"/api/warranties/{warranty_id}/events",
            json={
                "action": "resolve_substitution",
                "notes": "Produto substituto destinado ao estoque.",
                "replacementDestination": "stock",
                "replacementProductId": self.replacement["id"],
                "replacementQuantity": 1,
                "replacementUnitCost": 65,
                "awaitingCustomerDelivery": False,
            },
        )
        self.assertEqual(resolved.status_code, 200, resolved.get_json())
        warranty = resolved.get_json()["data"]["warranty"]
        self.assertEqual(warranty["status"], "resolved")
        event = warranty["events"][-1]
        self.assertEqual(event["replacementDestination"], "stock")
        self.assertEqual(event["replacementProductId"], self.replacement["id"])
        self.assertTrue(event["stockEntryId"])
        entry = self.row(
            """
            SELECT origin, warranty_id, total_quantity, total_cost
            FROM stock_entries WHERE id = ?
            """,
            (event["stockEntryId"],),
        )
        self.assertEqual(entry["origin"], "warranty_replacement")
        self.assertEqual(entry["warranty_id"], warranty_id)
        self.assertEqual(entry["total_quantity"], 1)
        self.assertEqual(entry["total_cost"], 65)
        self.assertEqual(
            self.scalar(
                "SELECT stock FROM products WHERE id = ?",
                (self.replacement["id"],),
            ),
            11,
        )
        self.assertEqual(
            self.scalar(
                "SELECT COUNT(*) FROM inventory_movements "
                "WHERE reference_type = 'warranty' AND reference_id = ?",
                (warranty_id,),
            ),
            1,
        )

    def test_sale_cancellation_reverses_mixed_finance_stock_and_is_idempotent(self):
        sale = self.create_sale(
            "sale-cancel-mixed",
            payments=[
                {"method": "cash", "amount": 90},
                {"method": "pix", "amount": 90},
            ],
        )
        headers = {"Idempotency-Key": "sale-cancel-mixed-key"}
        payload = {"reason": "Venda registrada incorretamente"}
        with (
            mock.patch.object(
                server,
                "write_state",
                side_effect=AssertionError("write_state chamado"),
            ),
            mock.patch.object(
                server,
                "sync_business_tables",
                side_effect=AssertionError("sync_business_tables chamado"),
            ),
        ):
            first = self.client.post(
                f"/api/sales/{sale['id']}/cancel",
                json=payload,
                headers=headers,
            )
            replay = self.client.post(
                f"/api/sales/{sale['id']}/cancel",
                json=payload,
                headers=headers,
            )

        self.assertEqual(first.status_code, 200, first.get_json())
        self.assertEqual(replay.status_code, 200, replay.get_json())
        self.assertFalse(first.get_json()["replayed"])
        self.assertTrue(replay.get_json()["replayed"])
        result = first.get_json()["data"]
        self.assertEqual(result["sale"]["status"], "cancelled")
        self.assertEqual(
            sorted((item["method"], item["amount"]) for item in result["cash"]),
            [("cash", 90), ("pix", 90)],
        )
        self.assertEqual(result["return"]["netTotal"], 180)
        self.assertEqual(
            self.scalar(
                "SELECT stock FROM products WHERE id = ?",
                (self.product["id"],),
            ),
            10,
        )
        self.assertEqual(
            self.scalar(
                "SELECT COUNT(*) FROM sale_cancellations WHERE sale_id = ?",
                (sale["id"],),
            ),
            1,
        )
        self.assertEqual(
            self.scalar(
                "SELECT COUNT(*) FROM sale_returns WHERE sale_id = ?",
                (sale["id"],),
            ),
            1,
        )

    def test_after_sales_interface_exposes_mixed_exchange_payments(self):
        root = os.path.dirname(os.path.dirname(__file__))
        with open(
            os.path.join(root, "index.html"),
            encoding="utf-8",
        ) as handle:
            markup = handle.read()
        with open(
            os.path.join(root, "script.js"),
            encoding="utf-8",
        ) as handle:
            javascript = handle.read()
        self.assertIn('id="exchangePaymentRows"', markup)
        self.assertIn('id="addExchangePaymentButton"', markup)
        self.assertIn('id="exchangeStoreCreditInstallments"', markup)
        self.assertIn("function readExchangePayments()", javascript)
        self.assertIn("payments = difference > 0 ? readExchangePayments()", javascript)

    def test_warranty_photo_upload_validates_file_content(self):
        invalid = self.client.post(
            "/api/uploads/warranty-photo",
            data={"photo": (io.BytesIO(b"not-an-image"), "evidence.png")},
            content_type="multipart/form-data",
        )
        self.assertEqual(invalid.status_code, 400)
        valid = self.client.post(
            "/api/uploads/warranty-photo",
            data={
                "photo": (
                    io.BytesIO(
                        b"\x89PNG\r\n\x1a\n"
                        b"\x00\x00\x00\rIHDR"
                    ),
                    "evidence.png",
                )
            },
            content_type="multipart/form-data",
        )
        self.assertEqual(valid.status_code, 201, valid.get_json())
        self.assertTrue(valid.get_json()["data"]["url"])

    def test_sale_cancellation_is_blocked_after_completed_return(self):
        sale = self.create_sale("cancel-after-return")
        returned = self.client.post(
            "/api/returns",
            headers={"Idempotency-Key": "cancel-after-return-op"},
            json=self.return_payload(sale),
        )
        self.assertEqual(returned.status_code, 201, returned.get_json())
        response = self.client.post(
            f"/api/sales/{sale['id']}/cancel",
            headers={"Idempotency-Key": "cancel-after-return-attempt"},
            json={"reason": "Cancelamento solicitado pelo cliente"},
        )
        self.assertEqual(response.status_code, 409)
        self.assertEqual(
            response.get_json()["code"],
            "SALE_AFTER_SALES_CONFLICT",
        )

    def test_return_postgresql_adapter_path_uses_locking_and_commits(self):
        sale = self.create_sale("postgres-return-sale")
        adapters = []

        def factory():
            adapter = _PostgresPathOnSQLite(server.DB_PATH)
            adapters.append(adapter)
            return adapter

        with server.app.test_request_context("/"):
            server.session["user"] = {
                "id": "operator",
                "name": "Operator",
                "login": "operator",
                "role": "operator",
                "active": True,
            }
            with mock.patch.object(server, "USE_POSTGRES", True), mock.patch.object(
                server,
                "connect_db",
                side_effect=factory,
            ):
                result, replayed = server.persist_sale_return(
                    self.return_payload(sale),
                    "postgres-return",
                )
        self.assertFalse(replayed)
        self.assertEqual(result["return"]["netTotal"], 90)
        self.assertTrue(any(
            "pg_advisory_xact_lock" in statement
            for adapter in adapters
            for statement in adapter.statements
        ))
        self.assertTrue(any(
            "FOR UPDATE" in statement
            for adapter in adapters
            for statement in adapter.statements
        ))

    def test_audit_failure_rolls_back_return(self):
        sale = self.create_sale("return-rollback-sale")
        with mock.patch.object(
            server,
            "record_audit",
            side_effect=RuntimeError("audit failure"),
        ):
            response = self.client.post(
                "/api/returns",
                headers={"Idempotency-Key": "return-rollback"},
                json=self.return_payload(sale),
            )
        self.assertEqual(response.status_code, 500)
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM sale_returns"), 0)
        self.assertEqual(
            self.scalar(
                "SELECT stock FROM products WHERE id = ?",
                (self.product["id"],),
            ),
            8,
        )


if __name__ == "__main__":
    unittest.main()
