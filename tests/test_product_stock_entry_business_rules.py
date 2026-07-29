import gc
import json
import os
import sqlite3
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier
from unittest import mock

from flask import session

from database_migrations.migrations.v004_product_stock_entries import MIGRATION_004
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
        self.statements.append(sql)
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


class ProductStockEntryBusinessRulesTest(unittest.TestCase):
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
        server.DB_PATH = os.path.join(self.temp_dir.name, "product-entry.db")
        run_database_migrations(
            environ=AUTHORIZED_ENV,
            sqlite_path=server.DB_PATH,
            create_database=True,
        )
        state = server.default_state()
        with server.connect_db() as connection:
            connection.execute(
                "INSERT INTO stores (id, name, created_at) VALUES (?, ?, ?)",
                ("matriz", "Matriz", "2026-07-23T10:00:00Z"),
            )
            connection.execute(
                "INSERT INTO app_state (id, data, updated_at) VALUES (1, ?, ?)",
                (json.dumps(state), "2026-07-23T10:00:00Z"),
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
        self.authenticate()
        self.brand = self.create_catalog("/api/brands", "Mova")
        self.category = self.create_catalog("/api/categories", "Fitness")
        self.size = self.create_catalog("/api/sizes", "M")
        self.color = self.create_catalog("/api/colors", "Preto")
        self.supplier = self.create_supplier("Fornecedor A")

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

    def authenticate(self, role="operator"):
        with self.client.session_transaction() as flask_session:
            flask_session["user"] = {
                "id": "operator",
                "name": "Operador",
                "login": "operator",
                "role": role,
                "active": True,
            }

    def create_catalog(self, endpoint, name):
        response = self.client.post(endpoint, json={"name": name})
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()["data"]

    def create_supplier(self, name):
        response = self.client.post(
            "/api/suppliers",
            json={
                "name": name,
                "document": "",
                "phone": "48999990000",
                "whatsapp": "48999990000",
                "email": "supplier@example.test",
            },
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()["data"]

    def product_payload(self, barcode="789100000001", **changes):
        product = {
            "barcode": barcode,
            "name": "Legging Core",
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
        }
        product.update(changes)
        return {"quantity": 3, "product": product}

    def post_entry(self, key="entry-key-1", payload=None):
        return self.client.post(
            "/api/stock-entries",
            headers={"Idempotency-Key": key},
            json=payload or self.product_payload(),
        )

    def test_migration_004_is_additive_for_sqlite_and_postgresql(self):
        self.assertEqual(MIGRATION_004.version, 4)
        self.assertTrue(any("ALTER TABLE products ADD COLUMN created_at" in sql for sql in MIGRATION_004.sqlite_statements))
        self.assertTrue(any("CREATE TABLE stock_entries" in sql for sql in MIGRATION_004.sqlite_statements))
        self.assertTrue(any("CREATE TABLE stock_movements" in sql for sql in MIGRATION_004.postgresql_statements))
        with sqlite3.connect(server.DB_PATH) as connection:
            columns = {row[1] for row in connection.execute("PRAGMA table_info(products)")}
            tables = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
            version = connection.execute(
                "SELECT MAX(version) FROM schema_migrations"
            ).fetchone()[0]
        self.assertTrue({"barcode_normalized", "created_at", "stock_entered_at"} <= columns)
        self.assertTrue({"stock_entries", "stock_entry_items", "stock_movements"} <= tables)
        self.assertEqual(version, 18)

    def test_lookup_unknown_product_does_not_persist(self):
        response = self.client.get("/api/products/lookup?barcode=  abc-001 ")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.get_json()["data"]["exists"])
        self.assertEqual(response.get_json()["data"]["barcode"], "ABC-001")
        with sqlite3.connect(server.DB_PATH) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM products").fetchone()[0], 0)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM stock_entries").fetchone()[0], 0)

    def test_new_product_first_entry_is_atomic_and_audited(self):
        response = self.post_entry()
        self.assertEqual(response.status_code, 201, response.get_json())
        data = response.get_json()["data"]
        self.assertEqual(data["product"]["stock"], 3)
        self.assertEqual(data["product"]["availableStock"], 3)
        self.assertEqual(data["product"]["reservedStock"], 0)
        self.assertEqual(data["entry"]["entryNumber"], 1)
        self.assertEqual(data["entry"]["totalCost"], 150)
        self.assertEqual(data["movement"]["balanceBefore"], 0)
        self.assertEqual(data["movement"]["balanceAfter"], 3)
        self.assertRegex(data["product"]["createdAt"], r"(Z|\+00:00)$")
        self.assertRegex(data["product"]["stockEnteredAt"], r"(Z|\+00:00)$")
        with sqlite3.connect(server.DB_PATH) as connection:
            connection.row_factory = sqlite3.Row
            counts = {
                table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                for table in (
                    "products",
                    "stock_entries",
                    "stock_entry_items",
                    "stock_movements",
                )
            }
            audit = connection.execute(
                "SELECT module, action FROM audit_logs WHERE ref_id = ?",
                (data["entry"]["id"],),
            ).fetchone()
            state = json.loads(
                connection.execute("SELECT data FROM app_state WHERE id = 1").fetchone()[0]
            )
        self.assertEqual(set(counts.values()), {1})
        self.assertEqual(tuple(audit), ("stock_entry", "create"))
        self.assertEqual(state["products"][0]["stock"], 3)
        self.assertEqual(state["stockEntries"][0]["id"], data["entry"]["id"])
        self.assertEqual(state["stockMovements"][0]["id"], data["movement"]["id"])

    def test_existing_entry_increments_stock_and_preserves_snapshots(self):
        first = self.post_entry().get_json()["data"]
        supplier_b = self.create_supplier("Fornecedor B")
        payload = self.product_payload(
            name="Legging Atualizada",
            supplierId=supplier_b["id"],
            cost=60,
            price=120,
        )
        payload["quantity"] = 2
        second_response = self.post_entry("entry-key-2", payload)
        self.assertEqual(second_response.status_code, 201, second_response.get_json())
        second = second_response.get_json()["data"]
        self.assertEqual(second["product"]["id"], first["product"]["id"])
        self.assertEqual(second["product"]["stock"], 5)
        self.assertEqual(second["product"]["cost"], 60)
        self.assertEqual(second["movement"]["balanceBefore"], 3)
        self.assertEqual(second["movement"]["balanceAfter"], 5)
        with sqlite3.connect(server.DB_PATH) as connection:
            rows = connection.execute(
                """
                SELECT product_name, supplier_name, unit_cost, stock_before, stock_after
                FROM stock_entry_items
                ORDER BY rowid
                """
            ).fetchall()
        self.assertEqual(rows[0], ("Legging Core", "Fornecedor A", 50, 0, 3))
        self.assertEqual(rows[1], ("Legging Atualizada", "Fornecedor B", 60, 3, 5))

    def test_edit_only_preserves_stock_and_does_not_create_movement(self):
        created = self.post_entry().get_json()["data"]["product"]
        payload = {**created, "name": "Legging Editada", "stock": 999, "price": 110}
        response = self.client.put(f"/api/products/{created['id']}", json=payload)
        self.assertEqual(response.status_code, 200, response.get_json())
        self.assertEqual(response.get_json()["data"]["stock"], 3)
        self.assertEqual(response.get_json()["data"]["name"], "Legging Editada")
        with sqlite3.connect(server.DB_PATH) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM stock_entries").fetchone()[0], 1)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM stock_movements").fetchone()[0], 1)

    def test_quantity_cost_and_sale_price_are_strictly_validated(self):
        for index, quantity in enumerate((0, -1, 1.5, "abc"), start=1):
            with self.subTest(quantity=quantity):
                payload = self.product_payload(barcode=f"78910000001{index}")
                payload["quantity"] = quantity
                response = self.post_entry(
                    f"invalid-quantity-{index}",
                    payload,
                )
                self.assertEqual(response.status_code, 400)
        invalid_cost = self.post_entry(
            "invalid-cost",
            self.product_payload(barcode="789100000020", cost=0),
        )
        invalid_price = self.post_entry(
            "invalid-price",
            self.product_payload(barcode="789100000021", price=0),
        )
        invalid_text_cost = self.post_entry(
            "invalid-text-cost",
            self.product_payload(barcode="789100000022", cost="invalid"),
        )
        invalid_minimum = self.post_entry(
            "invalid-minimum",
            self.product_payload(barcode="789100000023", minStock=1.5),
        )
        self.assertEqual(invalid_cost.status_code, 400)
        self.assertEqual(invalid_price.status_code, 400)
        self.assertEqual(invalid_text_cost.status_code, 400)
        self.assertEqual(invalid_minimum.status_code, 400)

        created = self.post_entry(
            "valid-before-invalid-edit",
            self.product_payload(barcode="789100000024"),
        ).get_json()["data"]["product"]
        invalid_edit = self.client.put(
            f"/api/products/{created['id']}",
            json={**created, "price": "invalid", "stock": 999},
        )
        self.assertEqual(invalid_edit.status_code, 400)
        lookup = self.client.get(
            f"/api/products/lookup?barcode={created['barcode']}"
        ).get_json()["data"]["product"]
        self.assertEqual(lookup["stock"], 3)
        self.assertEqual(lookup["price"], 100)

    def test_active_catalogs_and_supplier_are_required(self):
        missing_brand = self.post_entry(
            "missing-brand",
            self.product_payload(barcode="789100000030", brandId="", brand=""),
        )
        self.assertEqual(missing_brand.status_code, 400)
        self.client.post(
            f"/api/suppliers/{self.supplier['id']}/status",
            json={"status": "deactivated", "reason": "Teste"},
        )
        inactive_supplier = self.post_entry(
            "inactive-supplier",
            self.product_payload(barcode="789100000031"),
        )
        self.assertEqual(inactive_supplier.status_code, 400)

    def test_available_stock_deducts_open_conditionals_without_changing_real_stock(self):
        product = self.post_entry().get_json()["data"]["product"]
        with server.connect_db() as connection:
            state = server.stored_app_state_from_connection(connection)
            state["conditionals"] = [{
                "id": "COND001",
                "status": "open",
                "items": [{"productId": product["id"], "quantity": 2}],
            }]
            connection.execute(
                "UPDATE app_state SET data = ? WHERE id = 1",
                (json.dumps(state),),
            )
        lookup = self.client.get(
            f"/api/products/lookup?barcode={product['barcode']}"
        ).get_json()["data"]["product"]
        self.assertEqual(lookup["stock"], 3)
        self.assertEqual(lookup["reservedStock"], 2)
        self.assertEqual(lookup["availableStock"], 1)

    def test_idempotency_replays_same_payload_and_rejects_different_payload(self):
        first = self.post_entry("same-key")
        second = self.post_entry("same-key")
        changed = self.product_payload()
        changed["quantity"] = 4
        conflict = self.post_entry("same-key", changed)
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.get_json()["data"], second.get_json()["data"])
        self.assertEqual(conflict.status_code, 409)
        self.assertEqual(conflict.get_json()["code"], "IDEMPOTENCY_CONFLICT")
        with sqlite3.connect(server.DB_PATH) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM stock_entries").fetchone()[0], 1)
            self.assertEqual(connection.execute("SELECT stock FROM products").fetchone()[0], 3)

    def test_normalized_code_reuses_the_existing_product(self):
        first = self.post_entry(
            "normalized-code-1",
            self.product_payload(barcode=" abc-001 "),
        )
        second = self.post_entry(
            "normalized-code-2",
            self.product_payload(barcode="abc-001", name="Nome Atualizado"),
        )
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 201)
        self.assertEqual(
            first.get_json()["data"]["product"]["id"],
            second.get_json()["data"]["product"]["id"],
        )
        with sqlite3.connect(server.DB_PATH) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM products").fetchone()[0], 1)
            self.assertEqual(connection.execute("SELECT stock FROM products").fetchone()[0], 6)

    def test_concurrent_entries_use_the_latest_persisted_stock(self):
        product = self.post_entry().get_json()["data"]["product"]
        barrier = Barrier(2)

        def register(key, quantity):
            payload = self.product_payload(barcode=product["barcode"])
            payload["quantity"] = quantity
            with server.app.test_request_context("/"):
                session["user"] = {
                    "id": "operator",
                    "name": "Operador",
                    "role": "operator",
                }
                barrier.wait()
                return server.persist_product_entry(payload, key)[0]

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(
                lambda item: register(*item),
                (("concurrent-1", 2), ("concurrent-2", 4)),
            ))
        observed_stocks = {item["product"]["stock"] for item in results}
        self.assertIn(observed_stocks, ({5, 9}, {7, 9}))
        with sqlite3.connect(server.DB_PATH) as connection:
            self.assertEqual(connection.execute("SELECT stock FROM products").fetchone()[0], 9)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM stock_entries").fetchone()[0], 3)

    def test_inactive_product_is_found_and_requires_explicit_reactivation(self):
        product = self.post_entry().get_json()["data"]["product"]
        disabled = self.client.put(
            f"/api/products/{product['id']}",
            json={**product, "active": False},
        )
        self.assertEqual(disabled.status_code, 200)
        lookup = self.client.get(
            f"/api/products/lookup?barcode={product['barcode']}"
        ).get_json()["data"]
        self.assertTrue(lookup["exists"])
        self.assertFalse(lookup["product"]["active"])
        blocked_payload = self.product_payload(active=False)
        blocked = self.post_entry("inactive-entry", blocked_payload)
        self.assertEqual(blocked.status_code, 409)
        self.assertEqual(blocked.get_json()["code"], "PRODUCT_DEACTIVATED")
        reactivated = self.post_entry(
            "reactivated-entry",
            self.product_payload(active=True),
        )
        self.assertEqual(reactivated.status_code, 201)
        self.assertTrue(reactivated.get_json()["data"]["product"]["active"])

    def test_entry_rollback_removes_all_effects_when_audit_fails(self):
        with mock.patch.object(server, "record_audit", side_effect=RuntimeError("audit failed")):
            with self.assertRaisesRegex(RuntimeError, "audit failed"):
                with server.app.test_request_context("/"):
                    session["user"] = {
                        "id": "operator",
                        "name": "Operador",
                        "role": "operator",
                    }
                    server.persist_product_entry(
                        self.product_payload(),
                        "rollback-key",
                    )
        with sqlite3.connect(server.DB_PATH) as connection:
            for table in (
                "products",
                "stock_entries",
                "stock_entry_items",
                "stock_movements",
                "inventory_movements",
            ):
                self.assertEqual(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0], 0)
            state = json.loads(
                connection.execute("SELECT data FROM app_state WHERE id = 1").fetchone()[0]
            )
        self.assertEqual(state["products"], [])
        self.assertEqual(state["stockEntries"], [])
        self.assertEqual(state["stockMovements"], [])
        self.assertEqual(state["inventoryMovements"], [])

    def test_postgresql_path_uses_transaction_locks_and_full_persistence(self):
        adapters = []

        def factory():
            adapter = _PostgresPathOnSQLite(server.DB_PATH)
            adapters.append(adapter)
            return adapter

        with server.app.test_request_context("/"):
            session["user"] = {
                "id": "operator",
                "name": "Operador",
                "role": "operator",
            }
            with mock.patch.object(server, "USE_POSTGRES", True), mock.patch.object(
                server, "connect_db", side_effect=factory
            ):
                result, replayed = server.persist_product_entry(
                    self.product_payload(),
                    "postgres-simulated-key",
                )
        self.assertFalse(replayed)
        self.assertEqual(result["product"]["stock"], 3)
        statements = "\n".join(adapters[0].statements)
        self.assertIn("pg_advisory_xact_lock", statements)
        self.assertIn("FOR UPDATE", statements)
        with sqlite3.connect(server.DB_PATH) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM stock_entries").fetchone()[0], 1)
            self.assertEqual(
                connection.execute(
                    "SELECT COUNT(*) FROM inventory_movements"
                ).fetchone()[0],
                1,
            )

    def test_permissions_history_and_product_deletion_protection(self):
        product = self.post_entry().get_json()["data"]["product"]
        history = self.client.get(
            f"/api/stock-entries?productId={product['id']}"
        )
        self.assertEqual(history.status_code, 200)
        self.assertEqual(len(history.get_json()["data"]), 1)
        deletion = self.client.delete(f"/api/products/{product['id']}")
        self.assertEqual(deletion.status_code, 409)
        anonymous = server.app.test_client()
        self.assertEqual(anonymous.get("/api/stock-entries").status_code, 401)
        self.assertEqual(
            anonymous.post(
                "/api/stock-entries",
                headers={"Idempotency-Key": "anonymous"},
                json=self.product_payload(barcode="789100000099"),
            ).status_code,
            401,
        )

    def test_frontend_uses_lookup_entry_actions_and_has_no_direct_stock_field(self):
        root = Path(__file__).resolve().parents[1]
        html = (root / "index.html").read_text(encoding="utf-8")
        script = (root / "script.js").read_text(encoding="utf-8")
        self.assertIn('id="productLookupButton"', html)
        self.assertIn('id="newProductSupplierButton"', html)
        self.assertIn('id="confirmProductEntryButton"', html)
        self.assertIn('id="productEntryHistory"', html)
        self.assertNotIn('id="productStock"', html)
        self.assertIn('fetch("/api/stock-entries"', script)
        self.assertIn("renderProductEntryHistory", script)


if __name__ == "__main__":
    unittest.main()
