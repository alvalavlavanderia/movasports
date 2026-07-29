from __future__ import annotations

import gc
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest import mock

from flask import session

from database_migrations.migrations.v016_catalog_documents import MIGRATION_016
from database_migrations.registry import MIGRATIONS
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


class PostgresPathOnSQLite:
    def __init__(self, path: str, statements: list[str]):
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.statements = statements

    def execute(self, sql, params=()):
        self.statements.append(" ".join(sql.split()))
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


class CatalogDocumentsBusinessRulesTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original = (
            server.ENVIRONMENT,
            server.USE_POSTGRES,
            server.DATABASE_URL,
            server.DB_PATH,
            server.app.config.get("TESTING"),
        )
        server.ENVIRONMENT = EnvironmentConfig(
            "development",
            "configured",
            False,
            False,
        )
        server.USE_POSTGRES = False
        server.DATABASE_URL = ""
        server.DB_PATH = os.path.join(self.temp_dir.name, "catalog-documents.db")
        server.app.config["TESTING"] = True
        run_database_migrations(
            environ=AUTHORIZED_ENV,
            sqlite_path=server.DB_PATH,
            create_database=True,
        )
        with server.connect_db() as connection:
            connection.execute(
                "INSERT INTO stores (id, name, created_at) VALUES (?, ?, ?)",
                ("matriz", "Mova Sports", "2026-07-26T10:00:00+00:00"),
            )
            connection.execute(
                "INSERT INTO app_state (id, data, updated_at) VALUES (1, ?, ?)",
                (
                    json.dumps(server.default_state(), ensure_ascii=False),
                    "2026-07-26T10:00:00+00:00",
                ),
            )
            for identifier, role in (("operator", "operator"), ("admin", "admin")):
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
                        "2026-07-26T10:00:00+00:00",
                    ),
                )
        self.client = server.app.test_client()
        self.authenticate()
        self.brand = self.create_catalog("/api/brands", "Mova")
        self.other_brand = self.create_catalog("/api/brands", "Outra Marca")
        self.category = self.create_catalog("/api/categories", "Fitness")
        self.size = self.create_catalog("/api/sizes", "M")
        self.color = self.create_catalog("/api/colors", "Preto")
        supplier_response = self.client.post(
            "/api/suppliers",
            json={"name": "Fornecedor Catálogo", "email": "fornecedor@example.test"},
        )
        self.assertEqual(supplier_response.status_code, 201)
        self.supplier = supplier_response.get_json()["data"]
        customer_response = self.client.post(
            "/api/customers",
            json={
                "name": "Cliente Catálogo",
                "cpf": "52998224725",
                "phone": "48999991111",
                "email": "cliente@example.test",
                "limit": 500,
            },
        )
        self.assertEqual(customer_response.status_code, 201)
        self.customer = customer_response.get_json()["data"]
        self.product = self.create_product(
            "789900001501",
            "Legging Catálogo",
            5,
            50,
            100,
        )
        self.second_product = self.create_product(
            "789900001502",
            "Top Catálogo",
            2,
            35,
            75,
            brand_id=self.other_brand["id"],
        )
        self.unavailable_product = self.create_product(
            "789900001503",
            "Produto Indisponível",
            1,
            20,
            45,
        )
        with server.connect_db() as connection:
            connection.execute(
                "UPDATE products SET stock = 0 WHERE id = ?",
                (self.unavailable_product["id"],),
            )

    def tearDown(self):
        (
            server.ENVIRONMENT,
            server.USE_POSTGRES,
            server.DATABASE_URL,
            server.DB_PATH,
            server.app.config["TESTING"],
        ) = self.original
        self.client = None
        gc.collect()
        self.temp_dir.cleanup()

    def authenticate(self, identifier: str = "operator"):
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

    def create_product(
        self,
        barcode: str,
        name: str,
        quantity: int,
        cost: float,
        price: float,
        *,
        brand_id: str | None = None,
    ) -> dict:
        response = self.client.post(
            "/api/stock-entries",
            headers={"Idempotency-Key": f"opening-{barcode}"},
            json={
                "quantity": quantity,
                "product": {
                    "barcode": barcode,
                    "name": name,
                    "gender": "Feminino",
                    "brandId": brand_id or self.brand["id"],
                    "categoryId": self.category["id"],
                    "sizeId": self.size["id"],
                    "colorId": self.color["id"],
                    "supplierId": self.supplier["id"],
                    "cost": cost,
                    "price": price,
                    "minStock": 1,
                    "active": True,
                    "description": f"Descrição de {name}",
                },
            },
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()["data"]["product"]

    def create_sale(self) -> dict:
        response = self.client.post(
            "/api/sales",
            headers={"Idempotency-Key": "catalog-sale"},
            json={
                "customerId": self.customer["id"],
                "items": [{
                    "productId": self.product["id"],
                    "quantity": 1,
                    "practicedUnitPrice": 100,
                    "unitDiscount": 0,
                    "unitAddition": 0,
                }],
                "discount": 10,
                "addition": 0,
                "payments": [{"method": "cash", "amount": 90}],
            },
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()["data"]["sale"]

    def create_conditional(self, quantity: int = 3) -> dict:
        response = self.client.post(
            "/api/conditionals",
            headers={"Idempotency-Key": "catalog-conditional"},
            json={
                "customerId": self.customer["id"],
                "items": [{
                    "productId": self.product["id"],
                    "quantity": quantity,
                    "unitPrice": 100,
                }],
            },
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()["data"]

    def document(self, payload: dict, key: str):
        return self.client.post(
            "/api/documents",
            json=payload,
            headers={"Idempotency-Key": key},
        )

    def scalar(self, sql: str, params=()):
        with sqlite3.connect(server.DB_PATH) as connection:
            return connection.execute(sql, params).fetchone()[0]

    def test_migration_is_additive_registered_and_cross_database(self):
        self.assertIn(MIGRATION_016, MIGRATIONS)
        self.assertEqual(MIGRATION_016.version, 16)
        self.assertEqual(
            MIGRATION_016.sqlite_statements,
            MIGRATION_016.postgresql_statements,
        )
        self.assertFalse(any(
            statement.lstrip().upper().startswith(("DROP ", "DELETE ", "UPDATE "))
            for statement in MIGRATION_016.sqlite_statements
        ))
        self.assertEqual(
            self.scalar("SELECT MAX(version) FROM schema_migrations"),
            18,
        )

    def test_catalog_is_authenticated_available_and_never_exposes_sensitive_fields(self):
        self.client.post("/api/logout")
        unauthorized = self.client.get("/api/catalog/products")
        self.assertEqual(unauthorized.status_code, 401)
        self.authenticate()
        self.create_sale()
        self.create_conditional(3)

        response = self.client.get("/api/catalog/products")

        self.assertEqual(response.status_code, 200, response.get_json())
        data = response.get_json()["data"]
        products = {item["id"]: item for item in data["items"]}
        self.assertEqual(set(products), {self.product["id"], self.second_product["id"]})
        self.assertEqual(products[self.product["id"]]["availability"], "last_unit")
        self.assertEqual(products[self.second_product["id"]]["availability"], "available")
        serialized = json.dumps(data, ensure_ascii=False)
        for forbidden in ("barcode", "cost", "stock", "margin", "reservedStock"):
            self.assertNotIn(f'"{forbidden}"', serialized)

    def test_catalog_filters_order_and_detail_use_the_backend(self):
        filtered = self.client.get(
            "/api/catalog/products",
            query_string={
                "query": "top outra",
                "brand": "Outra Marca",
                "category": "Fitness",
                "size": "M",
                "color": "Preto",
                "minPrice": "70",
                "maxPrice": "80",
                "order": "price_desc",
            },
        )
        self.assertEqual(filtered.status_code, 200, filtered.get_json())
        self.assertEqual(
            [item["id"] for item in filtered.get_json()["data"]["items"]],
            [self.second_product["id"]],
        )
        detail = self.client.get(
            f"/api/catalog/products/{self.second_product['id']}"
        )
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.get_json()["data"]["name"], "Top Catálogo")
        missing = self.client.get(
            f"/api/catalog/products/{self.unavailable_product['id']}"
        )
        self.assertEqual(missing.status_code, 404)
        invalid = self.client.get(
            "/api/catalog/products",
            query_string={"minPrice": "100", "maxPrice": "10"},
        )
        self.assertEqual(invalid.status_code, 400)

    def test_sale_document_is_historical_idempotent_audited_and_reprintable(self):
        sale = self.create_sale()
        with server.connect_db() as connection:
            connection.execute(
                """
                UPDATE products
                SET name = 'Nome Atualizado',
                    brand_name = 'Outra Marca',
                    brand_id = ?
                WHERE id = ?
                """,
                (self.other_brand["id"], self.product["id"]),
            )
        payload = {
            "type": "sale_receipt",
            "sourceId": sale["id"],
            "format": "thermal",
            "options": {},
        }

        created = self.document(payload, "sale-document")
        replay = self.document(payload, "sale-document")
        conflict = self.document(
            {**payload, "format": "a4"},
            "sale-document",
        )
        second_emission = self.document(payload, "sale-document-second")

        self.assertEqual(created.status_code, 201, created.get_json())
        self.assertEqual(replay.status_code, 200, replay.get_json())
        self.assertEqual(conflict.status_code, 409, conflict.get_json())
        self.assertEqual(second_emission.status_code, 201, second_emission.get_json())
        first = created.get_json()["data"]
        self.assertEqual(replay.get_json()["data"]["id"], first["id"])
        self.assertEqual(first["copyNumber"], 1)
        self.assertEqual(second_emission.get_json()["data"]["copyNumber"], 2)
        item = first["snapshot"]["operation"]["items"][0]
        self.assertEqual(item["name"], "Legging Catálogo")
        self.assertEqual(item["brand"], "Mova")
        self.assertEqual(item["netTotal"], 90)
        self.assertNotIn("unitCost", item)

        reprint = self.client.post(
            f"/api/documents/{first['id']}/reprint",
            headers={"Idempotency-Key": "sale-document-reprint"},
        )
        self.assertEqual(reprint.status_code, 201, reprint.get_json())
        copy = reprint.get_json()["data"]
        self.assertEqual(copy["copyNumber"], 3)
        self.assertEqual(copy["snapshot"], first["snapshot"])
        self.assertEqual(
            self.scalar(
                "SELECT COUNT(*) FROM audit_logs "
                "WHERE module = 'document'"
            ),
            3,
        )

    def test_conditional_and_exchange_documents_preserve_safe_snapshots(self):
        sale = self.create_sale()
        conditional = self.create_conditional(1)
        conditional_response = self.document(
            {
                "type": "conditional",
                "sourceId": conditional["id"],
                "format": "a4",
                "options": {},
            },
            "conditional-document",
        )
        self.assertEqual(
            conditional_response.status_code,
            201,
            conditional_response.get_json(),
        )
        conditional_snapshot = conditional_response.get_json()["data"]["snapshot"]
        self.assertEqual(
            conditional_snapshot["operation"]["conditionalNumber"],
            conditional["conditionalNumber"],
        )
        self.assertNotIn(
            "unitCost",
            conditional_snapshot["operation"]["items"][0],
        )

        with server.connect_db() as connection:
            sale_item_id = connection.execute(
                "SELECT id FROM sale_items WHERE sale_id = ?",
                (sale["id"],),
            ).fetchone()["id"]
            now = "2026-07-26T16:00:00+00:00"
            connection.execute(
                """
                INSERT INTO exchanges (
                    id, store_id, exchange_number, sale_id, customer_id,
                    customer_name, status, origin, reason, notes,
                    credit_total, new_items_total, difference_amount,
                    difference_direction, user_id, user_name,
                    idempotency_key, request_hash, response_json,
                    reconciliation_required, created_at, updated_at
                ) VALUES (
                    'exchange-document-source', 'matriz', 1, ?, ?,
                    'Cliente Catálogo', 'completed', 'commercial',
                    'Tamanho', '', 90, 75, 15, 'refund',
                    'operator', 'Operator', 'exchange-source-key',
                    'hash', '{}', 0, ?, ?
                )
                """,
                (sale["id"], self.customer["id"], now, now),
            )
            connection.execute(
                """
                INSERT INTO exchange_return_items (
                    id, exchange_id, sale_item_id, product_id, barcode,
                    name, brand, size, color, quantity, unit_credit,
                    credit_total, unit_cost, cost_total,
                    physical_condition, restocked
                ) VALUES (
                    'exchange-return-source', 'exchange-document-source',
                    ?, ?, '789900001501', 'Legging Catálogo',
                    'Mova', 'M', 'Preto', 1, 90, 90, 50, 50,
                    'resellable', 1
                )
                """,
                (sale_item_id, self.product["id"]),
            )
            connection.execute(
                """
                INSERT INTO exchange_new_items (
                    id, exchange_id, product_id, barcode, name, brand,
                    size, color, quantity, original_unit_price,
                    practiced_unit_price, unit_discount, unit_addition,
                    net_total, unit_cost, cost_total, stock_before,
                    stock_after
                ) VALUES (
                    'exchange-new-source', 'exchange-document-source',
                    ?, '789900001502', 'Top Catálogo', 'Outra Marca',
                    'M', 'Preto', 1, 75, 75, 0, 0, 75, 35, 35, 2, 1
                )
                """,
                (self.second_product["id"],),
            )
        exchange_response = self.document(
            {
                "type": "exchange",
                "sourceId": "exchange-document-source",
                "format": "a4",
                "options": {},
            },
            "exchange-document",
        )
        self.assertEqual(
            exchange_response.status_code,
            201,
            exchange_response.get_json(),
        )
        exchange = exchange_response.get_json()["data"]["snapshot"]["operation"]
        self.assertEqual(exchange["exchangeNumber"], 1)
        self.assertNotIn("unitCost", exchange["returnedItems"][0])
        self.assertNotIn("costTotal", exchange["returnedItems"][0])
        self.assertNotIn("stockBefore", exchange["newItems"][0])
        self.assertNotIn("stockAfter", exchange["newItems"][0])

    def test_catalog_document_revalidates_query_and_excludes_sensitive_data(self):
        response = self.document(
            {
                "type": "catalog",
                "sourceId": "",
                "format": "a4",
                "options": {
                    "filters": {
                        "brand": "Outra Marca",
                        "order": "price_asc",
                    }
                },
            },
            "catalog-document",
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        operation = response.get_json()["data"]["snapshot"]["operation"]
        self.assertEqual(operation["total"], 1)
        self.assertEqual(operation["items"][0]["id"], self.second_product["id"])
        serialized = json.dumps(operation, ensure_ascii=False)
        for forbidden in ("barcode", "cost", "stock", "margin"):
            self.assertNotIn(f'"{forbidden}"', serialized)

    def test_product_labels_use_real_code128_and_validate_limits(self):
        response = self.document(
            {
                "type": "product_labels",
                "sourceId": "",
                "format": "thermal",
                "options": {
                    "items": [{
                        "productId": self.product["id"],
                        "copies": 2,
                    }]
                },
            },
            "label-document",
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        operation = response.get_json()["data"]["snapshot"]["operation"]
        self.assertEqual(operation["totalLabels"], 2)
        label = operation["items"][0]
        self.assertEqual(label["barcode"], "789900001501")
        self.assertIn("<svg", label["barcodeSvg"])
        self.assertIn("789900001501", label["barcodeSvg"])
        self.assertNotIn("cost", json.dumps(operation))

        invalid = self.document(
            {
                "type": "product_labels",
                "sourceId": "",
                "format": "thermal",
                "options": {
                    "items": [{
                        "productId": self.product["id"],
                        "copies": 51,
                    }]
                },
            },
            "label-document-invalid",
        )
        self.assertEqual(invalid.status_code, 400)

    def test_document_creation_rolls_back_when_audit_fails(self):
        with (
            server.app.test_request_context("/api/documents"),
            mock.patch.object(
                server,
                "record_audit",
                side_effect=RuntimeError("audit failed"),
            ),
        ):
            session["user"] = {
                "id": "operator",
                "name": "Operator",
                "role": "operator",
            }
            with self.assertRaisesRegex(RuntimeError, "audit failed"):
                server.persist_generated_document(
                    "product_labels",
                    "",
                    "thermal",
                    {
                        "items": [{
                            "productId": self.product["id"],
                            "copies": 1,
                        }]
                    },
                    "rollback-document",
                )
        self.assertEqual(
            self.scalar(
                "SELECT COUNT(*) FROM generated_documents "
                "WHERE idempotency_key = 'rollback-document'"
            ),
            0,
        )

    def test_postgresql_path_uses_lock_and_single_transaction_adapter(self):
        statements: list[str] = []

        def connect():
            return PostgresPathOnSQLite(server.DB_PATH, statements)

        server.USE_POSTGRES = True
        with (
            server.app.test_request_context("/api/documents"),
            mock.patch.object(server, "connect_db", side_effect=connect),
        ):
            session["user"] = {
                "id": "operator",
                "name": "Operator",
                "role": "operator",
            }
            result, replayed = server.persist_generated_document(
                "catalog",
                "",
                "a4",
                {"filters": {"order": "name"}},
                "postgres-document",
            )
        server.USE_POSTGRES = False

        self.assertFalse(replayed)
        self.assertEqual(result["documentType"], "catalog")
        self.assertTrue(any("pg_advisory_xact_lock" in sql for sql in statements))
        self.assertEqual(
            self.scalar(
                "SELECT COUNT(*) FROM generated_documents "
                "WHERE idempotency_key = 'postgres-document'"
            ),
            1,
        )

    def test_document_source_is_isolated_by_store(self):
        conditional = self.create_conditional(1)
        with server.connect_db() as connection:
            connection.execute(
                "INSERT INTO stores (id, name, created_at) VALUES (?, ?, ?)",
                ("other", "Outra Loja", "2026-07-26T12:00:00+00:00"),
            )
            with self.assertRaises(server.DocumentOperationError) as raised:
                server.conditional_document_snapshot(
                    connection,
                    conditional["id"],
                    "other",
                )
        self.assertEqual(raised.exception.status_code, 404)

    def test_frontend_uses_authoritative_catalog_and_document_states(self):
        root = Path(__file__).resolve().parents[1]
        script = (root / "script.js").read_text(encoding="utf-8")
        html = (root / "index.html").read_text(encoding="utf-8")
        css = (root / "style.css").read_text(encoding="utf-8")

        for identifier in (
            "catalogSizeFilter",
            "catalogColorFilter",
            "catalogMinPrice",
            "catalogMaxPrice",
            "catalogOrder",
            "catalogDocumentsList",
            "catalogDetailModal",
        ):
            self.assertIn(f'id="{identifier}"', html)
        self.assertIn("/api/catalog/products", script)
        self.assertIn("/api/documents", script)
        self.assertIn("printProductLabel", script)
        self.assertIn("formatStoreDateTime", script)
        self.assertIn("Nenhum produto disponível", script)
        self.assertIn("catalog-error-state", css)
        self.assertIn("catalog-document-row", css)
        self.assertNotIn("Disponível ${availableProductStock(product)}", script)


if __name__ == "__main__":
    unittest.main()
