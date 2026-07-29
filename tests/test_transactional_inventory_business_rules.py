from __future__ import annotations

import gc
import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

from database_migrations.migrations.v006_transactional_inventory import MIGRATION_006
from database_migrations.runner import run_database_migrations
from environment_config import EnvironmentConfig
import server


AUTHORIZED_ENV = {
    "APP_ENV": "development",
    "MOVA_ALLOW_MIGRATIONS": "true",
}


class TransactionalInventoryBusinessRulesTest(unittest.TestCase):
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
        server.DB_PATH = os.path.join(self.temp_dir.name, "inventory.db")
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
                (
                    json.dumps(server.default_state(), ensure_ascii=False),
                    "2026-07-23T10:00:00Z",
                ),
            )
            connection.execute(
                """
                INSERT INTO users (
                    id, store_id, name, login, password_hash, role, active, updated_at
                )
                VALUES ('operator', 'matriz', 'Operador', 'operator', 'not-used',
                        'operator', 1, '2026-07-23T10:00:00Z')
                """
            )
        self.client = server.app.test_client()
        with self.client.session_transaction() as flask_session:
            flask_session["user"] = {
                "id": "operator",
                "name": "Operador",
                "login": "operator",
                "role": "operator",
                "active": True,
            }
        self.brand = self.create_catalog("/api/brands", "Mova")
        self.category = self.create_catalog("/api/categories", "Fitness")
        self.size = self.create_catalog("/api/sizes", "M")
        self.color = self.create_catalog("/api/colors", "Preto")
        self.supplier = self.client.post(
            "/api/suppliers",
            json={
                "name": "Fornecedor Estoque",
                "document": "",
                "email": "estoque@example.test",
            },
        ).get_json()["data"]
        self.customer = self.client.post(
            "/api/customers",
            json={
                "name": "Cliente Estoque",
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

    def create_catalog(self, endpoint: str, name: str) -> dict:
        response = self.client.post(endpoint, json={"name": name})
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()["data"]

    def create_product(self, quantity: int = 5) -> dict:
        response = self.client.post(
            "/api/stock-entries",
            headers={"Idempotency-Key": "inventory-opening-entry"},
            json={
                "quantity": quantity,
                "product": {
                    "barcode": "789900000001",
                    "name": "Legging Transacional",
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

    def create_sale(self, quantity: int = 2) -> dict:
        response = self.client.post(
            "/api/sales",
            headers={"Idempotency-Key": f"inventory-sale-{quantity}-{os.urandom(4).hex()}"},
            json={
                "customerId": self.customer["id"],
                "customerName": self.customer["name"],
                "items": [{
                    "productId": self.product["id"],
                    "quantity": quantity,
                    "unitCost": 50,
                    "unitPrice": 100,
                }],
                "payments": [{"method": "cash", "amount": quantity * 100}],
                "discount": 0,
            },
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()["data"]

    def movement_rows(self) -> list[sqlite3.Row]:
        with sqlite3.connect(server.DB_PATH) as connection:
            connection.row_factory = sqlite3.Row
            return connection.execute(
                """
                SELECT *
                FROM inventory_movements
                WHERE product_id = ?
                ORDER BY created_at, id
                """,
                (self.product["id"],),
            ).fetchall()

    def product_stock(self) -> int:
        with sqlite3.connect(server.DB_PATH) as connection:
            return int(connection.execute(
                "SELECT stock FROM products WHERE id = ?",
                (self.product["id"],),
            ).fetchone()[0])

    def test_migration_006_is_additive_and_registered(self):
        self.assertEqual(MIGRATION_006.version, 6)
        self.assertTrue(any(
            "CREATE TABLE inventory_movements" in statement
            for statement in MIGRATION_006.sqlite_statements
        ))
        self.assertTrue(any(
            "CREATE TABLE inventory_movements" in statement
            for statement in MIGRATION_006.postgresql_statements
        ))
        self.assertFalse(any(
            "ALTER TABLE" in statement.upper()
            for statement in MIGRATION_006.sqlite_statements
        ))
        with sqlite3.connect(server.DB_PATH) as connection:
            version = connection.execute(
                "SELECT MAX(version) FROM schema_migrations"
            ).fetchone()[0]
            indexes = {
                row[1]
                for row in connection.execute(
                    "PRAGMA index_list(inventory_movements)"
                )
            }
        self.assertEqual(version, 18)
        self.assertIn("idx_inventory_movements_store_source", indexes)
        self.assertIn("idx_inventory_movements_product_created", indexes)

    def test_opening_snapshot_is_non_destructive_and_idempotent(self):
        legacy_product = {
            **self.product,
            "id": "legacy-opening-product",
            "barcode": "789900000002",
            "barcodeNormalized": "789900000002",
            "name": "Produto Legado",
            "stock": 4,
        }
        with server.connect_db() as connection:
            server.upsert_product(connection, legacy_product)
            opening_statement = MIGRATION_006.sqlite_statements[-1]
            connection.execute(opening_statement)
            connection.execute(opening_statement)
            row = connection.execute(
                """
                SELECT movement_type, quantity, real_before, real_after,
                       reserved_after, available_after
                FROM inventory_movements
                WHERE product_id = ?
                """,
                (legacy_product["id"],),
            ).fetchone()
            count = connection.execute(
                """
                SELECT COUNT(*)
                FROM inventory_movements
                WHERE product_id = ?
                """,
                (legacy_product["id"],),
            ).fetchone()[0]
            stock = connection.execute(
                "SELECT stock FROM products WHERE id = ?",
                (legacy_product["id"],),
            ).fetchone()[0]

        self.assertEqual(count, 1)
        self.assertEqual(row["movement_type"], "opening_balance")
        self.assertEqual(row["quantity"], 4)
        self.assertEqual(row["real_before"], 0)
        self.assertEqual(row["real_after"], 4)
        self.assertEqual(row["reserved_after"], 0)
        self.assertEqual(row["available_after"], 4)
        self.assertEqual(stock, 4)

    def test_entry_records_real_available_and_app_state_mirror(self):
        rows = self.movement_rows()
        self.assertEqual(len(rows), 1)
        movement = rows[0]
        self.assertEqual(movement["movement_type"], "entry")
        self.assertEqual(movement["real_before"], 0)
        self.assertEqual(movement["real_after"], 5)
        self.assertEqual(movement["reserved_after"], 0)
        self.assertEqual(movement["available_after"], 5)
        state = self.client.get("/api/state").get_json()["data"]
        mirrored = state["inventoryMovements"][0]
        self.assertEqual(mirrored["id"], movement["id"])
        self.assertEqual(mirrored["availableAfter"], 5)

    def test_conditional_reserves_and_releases_without_changing_real_stock(self):
        response = self.client.post(
            "/api/conditionals",
            json={
                "customerId": self.customer["id"],
                "items": [{
                    "productId": self.product["id"],
                    "quantity": 2,
                    "unitPrice": 100,
                    "unitCost": 50,
                }],
            },
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        conditional = response.get_json()["data"]
        product = next(
            item
            for item in self.client.get("/api/products").get_json()["data"]
            if item["id"] == self.product["id"]
        )
        self.assertEqual(product["stock"], 5)
        self.assertEqual(product["reservedStock"], 2)
        self.assertEqual(product["availableStock"], 3)

        blocked = self.client.post(
            "/api/sales",
            headers={"Idempotency-Key": "conditional-blocked-sale"},
            json={
                "customerId": self.customer["id"],
                "items": [{"productId": self.product["id"], "quantity": 4}],
                "payments": [{"method": "cash", "amount": 400}],
            },
        )
        self.assertEqual(blocked.status_code, 409)
        self.assertEqual(self.product_stock(), 5)

        finalized = self.client.put(
            f"/api/conditionals/{conditional['id']}",
            json={"finalItems": []},
        )
        self.assertEqual(finalized.status_code, 200, finalized.get_json())
        product = next(
            item
            for item in self.client.get("/api/products").get_json()["data"]
            if item["id"] == self.product["id"]
        )
        self.assertEqual(product["stock"], 5)
        self.assertEqual(product["reservedStock"], 0)
        self.assertEqual(product["availableStock"], 5)
        movements = {
            row["movement_type"]: row
            for row in self.movement_rows()
        }
        self.assertEqual(movements["conditional_reserve"]["reserved_after"], 2)
        self.assertEqual(movements["conditional_return"]["reserved_after"], 0)

    def test_sale_and_cancellation_change_real_stock_once(self):
        sale_data = self.create_sale(2)
        self.assertEqual(self.product_stock(), 3)
        sale_movement = sale_data["inventoryMovements"][0]
        self.assertEqual(sale_movement["realBefore"], 5)
        self.assertEqual(sale_movement["realAfter"], 3)

        cancelled = self.client.post(
            f"/api/sales/{sale_data['sale']['id']}/cancel",
            headers={"Idempotency-Key": "inventory-sale-cancellation"},
            json={"reason": "Venda registrada incorretamente"},
        )
        self.assertEqual(cancelled.status_code, 200, cancelled.get_json())
        self.assertEqual(self.product_stock(), 5)
        second = self.client.post(
            f"/api/sales/{sale_data['sale']['id']}/cancel",
            headers={"Idempotency-Key": "inventory-sale-cancellation"},
            json={"reason": "Venda registrada incorretamente"},
        )
        self.assertEqual(second.status_code, 200)
        self.assertTrue(second.get_json()["replayed"])
        self.assertEqual(self.product_stock(), 5)
        rows = self.movement_rows()
        types = [row["movement_type"] for row in rows]
        self.assertEqual(types.count("sale"), 1)
        self.assertEqual(types.count("customer_return"), 1)

    def test_customer_return_recomposes_only_selected_quantity(self):
        sale_data = self.create_sale(2)
        response = self.client.post(
            "/api/returns",
            headers={"Idempotency-Key": "inventory-partial-return"},
            json={
                "saleId": sale_data["sale"]["id"],
                "reason": "Tamanho",
                "items": [{
                    "productId": self.product["id"],
                    "productName": self.product["name"],
                    "action": "return",
                    "quantity": 1,
                    "unitPrice": 100,
                }],
            },
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        self.assertEqual(self.product_stock(), 4)
        movement = response.get_json()["data"]["inventoryMovements"][0]
        self.assertEqual(movement["movementType"], "customer_return")
        self.assertEqual(movement["realBefore"], 3)
        self.assertEqual(movement["realAfter"], 4)

    def test_history_preserves_product_snapshot_and_supports_filters(self):
        original_name = self.product["name"]
        self.create_sale(1)
        update = {**self.product, "name": "Legging Renomeada"}
        update_response = self.client.put(
            f"/api/products/{self.product['id']}",
            json=update,
        )
        self.assertEqual(update_response.status_code, 200, update_response.get_json())

        response = self.client.get(
            f"/api/inventory-movements?productId={self.product['id']}&type=sale"
        )
        self.assertEqual(response.status_code, 200, response.get_json())
        movements = response.get_json()["data"]
        self.assertEqual(len(movements), 1)
        self.assertEqual(movements[0]["productName"], original_name)
        self.assertEqual(movements[0]["barcode"], "789900000001")
        self.assertEqual(movements[0]["userName"], "Operador")

    def test_negative_or_empty_inventory_movement_is_rejected_atomically(self):
        with server.app.test_request_context("/"):
            server.session["user"] = {
                "id": "operator",
                "name": "Operador",
            }
            with self.assertRaises(server.InventoryOperationError):
                with server.connect_db() as connection:
                    connection.execute("BEGIN IMMEDIATE")
                    server.persist_inventory_movement(
                        connection,
                        product_id=self.product["id"],
                        movement_type="invalid",
                        real_before=5,
                        real_after=-1,
                        reserved_before=0,
                        reserved_after=0,
                        reference_type="test",
                        reference_id="negative",
                        source_key="test:negative",
                        created_at="2026-07-23T10:00:00Z",
                    )
        self.assertEqual(self.product_stock(), 5)
        self.assertFalse(any(
            row["source_key"] == "test:negative"
            for row in self.movement_rows()
        ))

    def test_stale_stock_snapshot_is_rejected_without_partial_write(self):
        stale_product = {**self.product, "stock": 4}
        stale_sale = {
            "id": "VENDA-STOCK-CONFLICT",
            "customerId": self.customer["id"],
            "customerName": self.customer["name"],
            "items": [{
                "productId": self.product["id"],
                "quantity": 1,
                "unitCost": 50,
                "unitPrice": 100,
                "total": 100,
            }],
            "subtotal": 100,
            "discount": 0,
            "total": 100,
            "costTotal": 50,
            "payments": [{"method": "cash", "amount": 100}],
            "status": "completed",
            "createdAt": "2026-07-23T10:01:00Z",
            "updatedAt": "2026-07-23T10:01:00Z",
        }
        with server.connect_db() as connection:
            connection.execute(
                "UPDATE products SET stock = 3 WHERE id = ?",
                (self.product["id"],),
            )
        with server.app.test_request_context("/api/sales", method="POST"):
            server.session["user"] = {
                "id": "operator",
                "name": "Operador",
                "role": "operator",
            }
            with self.assertRaises(server.InventoryOperationError) as context:
                server.sync_sale_to_state(
                    stale_sale,
                    [stale_product],
                    [],
                    [],
                )
        self.assertEqual(context.exception.code, "INVENTORY_CONFLICT")
        self.assertEqual(self.product_stock(), 3)
        with sqlite3.connect(server.DB_PATH) as connection:
            self.assertEqual(
                connection.execute(
                    "SELECT COUNT(*) FROM sales WHERE id = ?",
                    (stale_sale["id"],),
                ).fetchone()[0],
                0,
            )
            self.assertEqual(
                connection.execute(
                    """
                    SELECT COUNT(*) FROM inventory_movements
                    WHERE reference_id = ?
                    """,
                    (stale_sale["id"],),
                ).fetchone()[0],
                0,
            )

    def test_frontend_exposes_balances_history_and_hides_unavailable_items(self):
        root = Path(__file__).resolve().parents[1]
        html = (root / "index.html").read_text(encoding="utf-8")
        script = (root / "script.js").read_text(encoding="utf-8")
        self.assertIn("<th>Real</th>", html)
        self.assertIn("<th>Reservado</th>", html)
        self.assertIn("<th>Disponível</th>", html)
        self.assertIn('id="inventoryHistoryList"', html)
        self.assertIn("availableProductStock(product) > 0", script)
        self.assertIn('inventoryMovements: "/api/inventory-movements"', script)
        self.assertIn("function renderInventoryHistory()", script)


if __name__ == "__main__":
    unittest.main()
