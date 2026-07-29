from __future__ import annotations

import gc
import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from flask import session

from database_migrations.migrations.v007_inventory_counts import MIGRATION_007
from database_migrations.runner import run_database_migrations
from environment_config import EnvironmentConfig
import server


AUTHORIZED_ENV = {
    "APP_ENV": "development",
    "MOVA_ALLOW_MIGRATIONS": "true",
}


class _PostgresPathOnSQLite:
    def __init__(self, path: str):
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.statements: list[str] = []

    def execute(self, sql, params=()):
        self.statements.append(sql)
        return self.connection.execute(sql.replace(" FOR UPDATE", ""), params)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        if exc_type:
            self.connection.rollback()
        else:
            self.connection.commit()
        self.connection.close()


class PhysicalInventoryBusinessRulesTest(unittest.TestCase):
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
        server.DB_PATH = os.path.join(self.temp_dir.name, "physical-inventory.db")
        run_database_migrations(
            environ=AUTHORIZED_ENV,
            sqlite_path=server.DB_PATH,
            create_database=True,
        )
        with server.connect_db() as connection:
            connection.execute(
                "INSERT INTO stores (id, name, created_at) VALUES (?, ?, ?)",
                ("matriz", "Matriz", "2026-07-24T10:00:00+00:00"),
            )
            connection.execute(
                "INSERT INTO app_state (id, data, updated_at) VALUES (1, ?, ?)",
                (
                    json.dumps(server.default_state(), ensure_ascii=False),
                    "2026-07-24T10:00:00+00:00",
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
                        "2026-07-24T10:00:00+00:00",
                    ),
                )
        self.client = server.app.test_client()
        self.authenticate("operator")
        self.brand = self.create_catalog("/api/brands", "Mova")
        self.other_brand = self.create_catalog("/api/brands", "Outra")
        self.category = self.create_catalog("/api/categories", "Fitness")
        self.size = self.create_catalog("/api/sizes", "M")
        self.color = self.create_catalog("/api/colors", "Preto")
        self.supplier = self.client.post(
            "/api/suppliers",
            json={
                "name": "Fornecedor Inventário",
                "document": "",
                "email": "inventario@example.test",
            },
        ).get_json()["data"]
        self.product = self.create_product(
            "789700000001", "Legging Inventário", self.brand["id"], 5
        )
        self.other_product = self.create_product(
            "789700000002", "Top Inventário", self.other_brand["id"], 2
        )

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

    def create_product(
        self,
        barcode: str,
        name: str,
        brand_id: str,
        quantity: int,
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
                    "brandId": brand_id,
                    "categoryId": self.category["id"],
                    "sizeId": self.size["id"],
                    "colorId": self.color["id"],
                    "supplierId": self.supplier["id"],
                    "cost": 40,
                    "price": 90,
                    "minStock": 1,
                    "active": True,
                },
            },
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()["data"]["product"]

    def open_inventory(self, payload=None, key="inventory-open-1") -> dict:
        response = self.client.post(
            "/api/inventories",
            headers={"Idempotency-Key": key},
            json=payload or {"type": "general", "scope": {}},
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()["data"]

    def count_item(self, inventory: dict, item: dict, quantity: int):
        return self.client.put(
            f"/api/inventories/{inventory['id']}/items/{item['id']}/count",
            json={"quantity": quantity, "version": item["countVersion"]},
        )

    def count_all(self, inventory: dict, quantities: dict[str, int] | None = None):
        current = inventory
        for item in list(current["items"]):
            quantity = (
                quantities[item["productId"]]
                if quantities and item["productId"] in quantities
                else item["expectedQuantity"]
            )
            response = self.count_item(current, item, quantity)
            self.assertEqual(response.status_code, 200, response.get_json())
            current = self.client.get(
                f"/api/inventories/{inventory['id']}"
            ).get_json()["data"]
        return current

    def table_count(self, table: str) -> int:
        with sqlite3.connect(server.DB_PATH) as connection:
            return int(connection.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0])

    def product_stock(self, product_id: str) -> int:
        with sqlite3.connect(server.DB_PATH) as connection:
            return int(connection.execute(
                "SELECT stock FROM products WHERE id = ?",
                (product_id,),
            ).fetchone()[0])

    def test_migration_007_is_additive_registered_and_cross_database(self):
        self.assertEqual(MIGRATION_007.version, 7)
        for table in (
            "inventory_sequences",
            "inventories",
            "inventory_items",
            "inventory_count_events",
        ):
            self.assertTrue(any(
                f"CREATE TABLE {table}" in statement
                for statement in MIGRATION_007.sqlite_statements
            ))
            self.assertTrue(any(
                f"CREATE TABLE {table}" in statement
                for statement in MIGRATION_007.postgresql_statements
            ))
        self.assertFalse(any(
            "ALTER TABLE" in statement.upper()
            for statement in MIGRATION_007.sqlite_statements
        ))
        with sqlite3.connect(server.DB_PATH) as connection:
            version = connection.execute(
                "SELECT MAX(version) FROM schema_migrations"
            ).fetchone()[0]
        self.assertEqual(version, 18)

    def test_general_opening_preserves_snapshot_reservations_and_null_counts(self):
        state = self.client.get("/api/state").get_json()["data"]
        state["conditionals"] = [{
            "id": "conditional-open",
            "status": "open",
            "items": [{"productId": self.product["id"], "quantity": 2}],
        }]
        with server.connect_db() as connection:
            connection.execute(
                "UPDATE app_state SET data = ? WHERE id = 1",
                (json.dumps(state, ensure_ascii=False),),
            )

        inventory = self.open_inventory()
        self.assertEqual(inventory["number"], 1)
        self.assertEqual(inventory["status"], "in_progress")
        self.assertEqual(len(inventory["items"]), 2)
        item = next(
            entry
            for entry in inventory["items"]
            if entry["productId"] == self.product["id"]
        )
        self.assertEqual(item["initialReal"], 5)
        self.assertEqual(item["initialReserved"], 2)
        self.assertEqual(item["initialAvailable"], 3)
        self.assertEqual(item["initialExpected"], 3)
        self.assertIsNone(item["countedQuantity"])
        self.assertEqual(inventory["uncountedCount"], 2)
        mirrored = self.client.get("/api/state").get_json()["data"]["inventories"]
        self.assertEqual(mirrored[0]["id"], inventory["id"])

    def test_partial_inventory_filters_scope_and_replays_creation(self):
        payload = {
            "type": "partial",
            "scope": {"brandId": self.brand["id"]},
        }
        inventory = self.open_inventory(payload, "partial-key")
        self.assertEqual(
            [item["productId"] for item in inventory["items"]],
            [self.product["id"]],
        )
        replay = self.client.post(
            "/api/inventories",
            headers={"Idempotency-Key": "partial-key"},
            json=payload,
        )
        self.assertEqual(replay.status_code, 200, replay.get_json())
        self.assertTrue(replay.get_json()["replayed"])
        self.assertEqual(self.table_count("inventories"), 1)

    def test_barcode_lookup_count_zero_and_optimistic_concurrency(self):
        inventory = self.open_inventory()
        item = next(
            entry
            for entry in inventory["items"]
            if entry["productId"] == self.product["id"]
        )
        lookup = self.client.get(
            f"/api/inventories/{inventory['id']}/barcode",
            query_string={"code": self.product["barcode"]},
        )
        self.assertEqual(lookup.status_code, 200, lookup.get_json())
        saved = self.count_item(inventory, item, 0)
        self.assertEqual(saved.status_code, 200, saved.get_json())
        self.assertEqual(saved.get_json()["data"]["item"]["countedQuantity"], 0)
        conflict = self.count_item(inventory, item, 1)
        self.assertEqual(conflict.status_code, 409, conflict.get_json())
        self.assertEqual(conflict.get_json()["code"], "INVENTORY_COUNT_CONFLICT")
        self.assertEqual(self.table_count("inventory_count_events"), 1)

        outside = self.open_inventory(
            {
                "type": "partial",
                "scope": {"productIds": [self.product["id"]]},
            },
            "outside-scope",
        )
        response = self.client.get(
            f"/api/inventories/{outside['id']}/barcode",
            query_string={"code": self.other_product["barcode"]},
        )
        self.assertEqual(response.status_code, 409, response.get_json())
        self.assertEqual(response.get_json()["code"], "PRODUCT_OUTSIDE_INVENTORY")

    def test_finalization_blocks_uncounted_and_operator_adjustment(self):
        inventory = self.open_inventory()
        blocked = self.client.post(
            f"/api/inventories/{inventory['id']}/finalize",
            headers={"Idempotency-Key": "finish-uncounted"},
            json={"notes": ""},
        )
        self.assertEqual(blocked.status_code, 409, blocked.get_json())
        counted = self.count_all(
            inventory,
            {self.product["id"]: 4, self.other_product["id"]: 2},
        )
        operator = self.client.post(
            f"/api/inventories/{inventory['id']}/finalize",
            headers={"Idempotency-Key": "finish-operator"},
            json={"notes": "Falta conferida."},
        )
        self.assertEqual(operator.status_code, 403, operator.get_json())
        self.assertEqual(self.product_stock(self.product["id"]), 5)
        self.assertEqual(counted["status"], "in_progress")

    def test_admin_finalizes_positive_and_negative_adjustments_without_finance(self):
        inventory = self.open_inventory()
        inventory = self.count_all(
            inventory,
            {self.product["id"]: 4, self.other_product["id"]: 3},
        )
        self.authenticate("admin")
        without_notes = self.client.post(
            f"/api/inventories/{inventory['id']}/finalize",
            headers={"Idempotency-Key": "finish-no-notes"},
            json={"notes": ""},
        )
        self.assertEqual(without_notes.status_code, 400, without_notes.get_json())
        finalized = self.client.post(
            f"/api/inventories/{inventory['id']}/finalize",
            headers={"Idempotency-Key": "finish-admin"},
            json={"notes": "Contagem física confirmada."},
        )
        self.assertEqual(finalized.status_code, 200, finalized.get_json())
        data = finalized.get_json()["data"]
        self.assertEqual(data["status"], "finalized")
        self.assertEqual(data["divergenceCount"], 2)
        self.assertEqual(data["positiveQuantity"], 1)
        self.assertEqual(data["negativeQuantity"], 1)
        self.assertEqual(self.product_stock(self.product["id"]), 4)
        self.assertEqual(self.product_stock(self.other_product["id"]), 3)
        with sqlite3.connect(server.DB_PATH) as connection:
            movement_rows = connection.execute(
                """
                SELECT direction, quantity, reference_type
                FROM inventory_movements
                WHERE movement_type = 'inventory_adjustment'
                ORDER BY direction
                """
            ).fetchall()
            cash_count = connection.execute(
                "SELECT COUNT(*) FROM cash_movements"
            ).fetchone()[0]
            payable_count = connection.execute(
                "SELECT COUNT(*) FROM payables"
            ).fetchone()[0]
        self.assertEqual(
            sorted(tuple(row) for row in movement_rows),
            [("in", 1, "physical_inventory"), ("out", 1, "physical_inventory")],
        )
        self.assertEqual(cash_count, 0)
        self.assertEqual(payable_count, 0)

    def test_no_divergence_operator_finalization_is_idempotent(self):
        inventory = self.count_all(self.open_inventory())
        first = self.client.post(
            f"/api/inventories/{inventory['id']}/finalize",
            headers={"Idempotency-Key": "finish-clean"},
            json={"notes": ""},
        )
        self.assertEqual(first.status_code, 200, first.get_json())
        second = self.client.post(
            f"/api/inventories/{inventory['id']}/finalize",
            headers={"Idempotency-Key": "finish-clean"},
            json={"notes": ""},
        )
        self.assertEqual(second.status_code, 200, second.get_json())
        self.assertTrue(second.get_json()["replayed"])
        self.assertEqual(self.table_count("inventory_movements"), 2)

    def test_cancel_preserves_counts_and_does_not_change_stock(self):
        inventory = self.open_inventory()
        item = inventory["items"][0]
        saved = self.count_item(inventory, item, 0)
        self.assertEqual(saved.status_code, 200, saved.get_json())
        before = {
            self.product["id"]: self.product_stock(self.product["id"]),
            self.other_product["id"]: self.product_stock(self.other_product["id"]),
        }
        cancelled = self.client.post(
            f"/api/inventories/{inventory['id']}/cancel",
            json={"reason": "Contagem interrompida."},
        )
        self.assertEqual(cancelled.status_code, 200, cancelled.get_json())
        data = cancelled.get_json()["data"]
        self.assertEqual(data["status"], "cancelled")
        counted = next(entry for entry in data["items"] if entry["id"] == item["id"])
        self.assertEqual(counted["countedQuantity"], 0)
        self.assertEqual(self.product_stock(self.product["id"]), before[self.product["id"]])
        self.assertEqual(
            self.product_stock(self.other_product["id"]),
            before[self.other_product["id"]],
        )

    def test_finalization_uses_current_balance_after_opening(self):
        inventory = self.open_inventory(
            {
                "type": "partial",
                "scope": {"productIds": [self.product["id"]]},
            },
            "current-balance",
        )
        with server.connect_db() as connection:
            connection.execute(
                "UPDATE products SET stock = 6 WHERE id = ?",
                (self.product["id"],),
            )
        refreshed = self.client.get(
            f"/api/inventories/{inventory['id']}"
        ).get_json()["data"]
        item = refreshed["items"][0]
        self.assertEqual(item["initialExpected"], 5)
        self.assertEqual(item["expectedQuantity"], 6)
        saved = self.count_item(refreshed, item, 6)
        self.assertEqual(saved.status_code, 200, saved.get_json())
        finalized = self.client.post(
            f"/api/inventories/{inventory['id']}/finalize",
            headers={"Idempotency-Key": "finish-current"},
            json={"notes": ""},
        )
        self.assertEqual(finalized.status_code, 200, finalized.get_json())
        self.assertEqual(finalized.get_json()["data"]["divergenceCount"], 0)
        self.assertEqual(self.product_stock(self.product["id"]), 6)

    def test_finalization_rolls_back_when_audit_fails(self):
        inventory = self.count_all(
            self.open_inventory(),
            {self.product["id"]: 4, self.other_product["id"]: 2},
        )
        self.authenticate("admin")
        with mock.patch.object(
            server,
            "record_audit",
            side_effect=RuntimeError("audit unavailable"),
        ):
            response = self.client.post(
                f"/api/inventories/{inventory['id']}/finalize",
                headers={"Idempotency-Key": "finish-rollback"},
                json={"notes": "Conferência."},
            )
        self.assertEqual(response.status_code, 500)
        self.assertEqual(self.product_stock(self.product["id"]), 5)
        detail = self.client.get(
            f"/api/inventories/{inventory['id']}"
        ).get_json()["data"]
        self.assertEqual(detail["status"], "in_progress")
        with sqlite3.connect(server.DB_PATH) as connection:
            adjustments = connection.execute(
                """
                SELECT COUNT(*) FROM inventory_movements
                WHERE movement_type = 'inventory_adjustment'
                """
            ).fetchone()[0]
        self.assertEqual(adjustments, 0)

    def test_postgresql_path_locks_state_inventory_items_and_products(self):
        inventory = self.count_all(
            self.open_inventory(
                {
                    "type": "partial",
                    "scope": {"productIds": [self.product["id"]]},
                },
                "postgres-path",
            )
        )
        self.authenticate("admin")
        adapter = _PostgresPathOnSQLite(server.DB_PATH)
        server.USE_POSTGRES = True
        with server.app.test_request_context("/"):
            session["user"] = {
                "id": "admin",
                "name": "Admin",
                "login": "admin",
                "role": "admin",
                "active": True,
            }
            with mock.patch.object(server, "connect_db", return_value=adapter):
                result, replayed = server.finalize_inventory(
                    inventory["id"],
                    {"notes": ""},
                    "finish-postgres",
                )
        server.USE_POSTGRES = False
        self.assertFalse(replayed)
        self.assertEqual(result["status"], "finalized")
        lock_statements = [
            statement for statement in adapter.statements if "FOR UPDATE" in statement
        ]
        self.assertGreaterEqual(len(lock_statements), 4)

    def test_frontend_exposes_complete_inventory_workflow(self):
        html = Path("index.html").read_text(encoding="utf-8")
        script = Path("script.js").read_text(encoding="utf-8")
        self.assertIn('data-tab="inventario"', html)
        self.assertIn('id="inventoryCreateForm"', html)
        self.assertIn('id="inventoryBarcodeForm"', html)
        self.assertIn('id="inventoryFinalizeButton"', html)
        self.assertIn('id="inventoryUserFilter"', html)
        self.assertIn('id="inventoryStartFilter"', html)
        self.assertIn('id="inventoryEndFilter"', html)
        self.assertIn('inventories: "/api/inventories"', script)
        self.assertIn("savePhysicalInventoryCount", script)
        self.assertIn("finalizePhysicalInventory", script)
        self.assertIn("storeOperationalDateKey", script)


if __name__ == "__main__":
    unittest.main()
