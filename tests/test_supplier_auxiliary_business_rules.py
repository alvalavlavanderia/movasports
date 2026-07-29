from __future__ import annotations

import gc
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest

from database_migrations.migrations.v003_supplier_auxiliary_catalogs import (
    EXPENSE_CATEGORY_NAMES,
    MIGRATION_003,
)
from database_migrations.runner import run_database_migrations
from environment_config import EnvironmentConfig
import server


AUTHORIZED_ENV = {
    "APP_ENV": "development",
    "MOVA_ALLOW_MIGRATIONS": "true",
}


class SupplierAuxiliaryBusinessRulesTest(unittest.TestCase):
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
        server.DB_PATH = os.path.join(self.temp_dir.name, "supplier-business.db")
        run_database_migrations(
            environ=AUTHORIZED_ENV,
            sqlite_path=server.DB_PATH,
            create_database=True,
        )
        state = server.default_state()
        with server.connect_db() as conn:
            conn.execute(
                "INSERT INTO stores (id, name, created_at) VALUES (?, ?, ?)",
                ("matriz", "Matriz", "2026-07-23T10:00:00Z"),
            )
            conn.execute(
                "INSERT INTO app_state (id, data, updated_at) VALUES (1, ?, ?)",
                (json.dumps(state), "2026-07-23T10:00:00Z"),
            )
            conn.execute(
                """
                INSERT INTO users (
                    id, store_id, name, login, password_hash, role, active, updated_at
                )
                VALUES ('operator', 'matriz', 'Operador', 'operator', 'not-used',
                        'operator', 1, '2026-07-23T10:00:00Z')
                """
            )
            server.seed_default_expense_categories(conn)
        self.client = server.app.test_client()
        self.authenticate()

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

    def authenticate(self):
        with self.client.session_transaction() as flask_session:
            flask_session["user"] = {
                "id": "operator",
                "name": "Operador",
                "login": "operator",
                "role": "operator",
                "active": True,
            }

    @staticmethod
    def supplier_payload(**changes):
        payload = {
            "name": "Fornecedor Esportivo Ltda",
            "tradeName": "Esportivo",
            "document": "11.444.777/0001-61",
            "phone": "4833334444",
            "whatsapp": "48999998888",
            "email": "CONTATO@EXAMPLE.COM",
            "zip": "88000-000",
            "address": "Rua das Lojas",
            "addressNumber": "120",
            "district": "Centro",
            "city": "Florianopolis",
            "state": "sc",
            "notes": "Entrega semanal.",
        }
        payload.update(changes)
        return payload

    def create_supplier(self, **changes):
        response = self.client.post("/api/suppliers", json=self.supplier_payload(**changes))
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()["data"]

    def create_catalog(self, endpoint, name):
        response = self.client.post(endpoint, json={"name": name})
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()["data"]

    def test_migration_is_additive_and_has_sqlite_and_postgresql_paths(self):
        self.assertEqual(MIGRATION_003.version, 3)
        self.assertTrue(any("ALTER TABLE suppliers ADD COLUMN trade_name" in sql for sql in MIGRATION_003.sqlite_statements))
        self.assertTrue(any("CREATE TABLE sizes" in sql for sql in MIGRATION_003.sqlite_statements))
        self.assertTrue(any("UPDATE cash_movements" in sql for sql in MIGRATION_003.sqlite_statements))
        self.assertTrue(any("CREATE TABLE supplier_status_history" in sql for sql in MIGRATION_003.postgresql_statements))
        with sqlite3.connect(server.DB_PATH) as connection:
            tables = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
            product_columns = {
                row[1] for row in connection.execute("PRAGMA table_info(products)")
            }
            cash_columns = {
                row[1] for row in connection.execute("PRAGMA table_info(cash_movements)")
            }
        self.assertTrue({"sizes", "colors", "expense_categories", "supplier_status_history"} <= tables)
        self.assertTrue({"brand_id", "category_id", "size_id", "color_id", "supplier_id"} <= product_columns)
        self.assertIn("expense_category_id", cash_columns)

    def test_default_expense_categories_are_seeded_once_with_correct_names(self):
        with server.connect_db() as conn:
            server.seed_default_expense_categories(conn)
        response = self.client.get("/api/expense-categories")
        self.assertEqual(response.status_code, 200)
        names = [item["name"] for item in response.get_json()["data"]]
        self.assertEqual(set(names), set(EXPENSE_CATEGORY_NAMES))
        self.assertEqual(len(names), len(EXPENSE_CATEGORY_NAMES))
        self.assertIn("Água", names)
        self.assertIn("Salários", names)

    def test_supplier_full_record_is_normalized_persisted_audited_and_mirrored(self):
        supplier = self.create_supplier()
        self.assertEqual(supplier["document"], "11444777000161")
        self.assertEqual(supplier["email"], "contato@example.com")
        self.assertEqual(supplier["state"], "SC")
        self.assertEqual(supplier["status"], "active")
        with sqlite3.connect(server.DB_PATH) as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute(
                """
                SELECT trade_name, document_normalized, whatsapp, zip, address_number,
                       district, city, state, notes, status
                FROM suppliers WHERE id = ?
                """,
                (supplier["id"],),
            ).fetchone()
            audit = connection.execute(
                "SELECT action, module, user_id FROM audit_logs WHERE ref_id = ?",
                (supplier["id"],),
            ).fetchone()
            state = json.loads(
                connection.execute("SELECT data FROM app_state WHERE id = 1").fetchone()[0]
            )
        self.assertEqual(row["document_normalized"], "11444777000161")
        self.assertEqual(row["address_number"], "120")
        self.assertEqual(tuple(audit), ("create", "supplier", "operator"))
        self.assertEqual(
            next(item for item in state["suppliers"] if item["id"] == supplier["id"])["notes"],
            "Entrega semanal.",
        )

    def test_supplier_document_is_optional_validated_and_unique_including_legacy_rows(self):
        self.create_supplier()
        duplicate = self.client.post(
            "/api/suppliers",
            json=self.supplier_payload(name="Outro", document="11444777000161"),
        )
        self.assertEqual(duplicate.status_code, 409)
        invalid = self.client.post(
            "/api/suppliers",
            json=self.supplier_payload(name="Inválido", document="11111111111"),
        )
        self.assertEqual(invalid.status_code, 400)
        without_document = self.client.post(
            "/api/suppliers",
            json=self.supplier_payload(name="Sem documento", document=""),
        )
        self.assertEqual(without_document.status_code, 201)
        with server.connect_db() as conn:
            conn.execute(
                """
                INSERT INTO suppliers (
                    id, store_id, name, cnpj, phone, email, address, status, updated_at
                ) VALUES ('legacy', 'matriz', 'Legado', '529.982.247-25', '', '', '',
                          'deactivated', '2026-01-01T00:00:00Z')
                """
            )
        legacy_duplicate = self.client.post(
            "/api/suppliers",
            json=self.supplier_payload(name="CPF repetido", document="52998224725"),
        )
        self.assertEqual(legacy_duplicate.status_code, 409)

    def test_supplier_deactivation_preserves_payables_requires_confirmation_and_is_reversible(self):
        supplier = self.create_supplier()
        category = self.client.get("/api/expense-categories").get_json()["data"][0]
        payable_response = self.client.post("/api/payables", json={
            "supplierId": supplier["id"],
            "expenseCategoryId": category["id"],
            "amount": 250,
            "issueDate": "2026-07-23",
            "dueDate": "2026-07-30",
            "notes": "Mercadoria",
        })
        self.assertEqual(payable_response.status_code, 201, payable_response.get_json())
        blocked = self.client.post(
            f"/api/suppliers/{supplier['id']}/status",
            json={"status": "deactivated"},
        )
        self.assertEqual(blocked.status_code, 409)
        self.assertEqual(blocked.get_json()["code"], "confirmation_required")
        changed = self.client.post(
            f"/api/suppliers/{supplier['id']}/status",
            json={"status": "deactivated", "confirmed": True, "reason": "Encerrado"},
        )
        self.assertEqual(changed.status_code, 200)
        self.assertEqual(changed.get_json()["data"]["status"], "deactivated")
        detail = self.client.get(f"/api/suppliers/{supplier['id']}").get_json()["data"]
        self.assertEqual(len(detail["payables"]), 1)
        self.assertEqual(detail["statusHistory"][0]["newStatus"], "deactivated")
        reactivated = self.client.post(
            f"/api/suppliers/{supplier['id']}/status",
            json={"status": "active", "reason": "Retomado"},
        )
        self.assertEqual(reactivated.status_code, 200)
        self.assertEqual(reactivated.get_json()["data"]["status"], "active")

    def test_catalogs_use_stable_ids_normalized_uniqueness_and_status(self):
        brand = self.create_catalog("/api/brands", "Águia Fit")
        duplicate = self.client.post("/api/brands", json={"name": " aguia   fit "})
        self.assertEqual(duplicate.status_code, 409)
        renamed = self.client.put(
            f"/api/brands/{brand['id']}",
            json={"name": "Águia Sports"},
        )
        self.assertEqual(renamed.status_code, 200)
        self.assertEqual(renamed.get_json()["data"]["id"], brand["id"])
        deactivated = self.client.post(
            f"/api/brands/{brand['id']}/status",
            json={"status": "deactivated"},
        )
        self.assertEqual(deactivated.status_code, 200)
        self.assertEqual(deactivated.get_json()["data"]["status"], "deactivated")
        reactivated = self.client.post(
            f"/api/brands/{brand['id']}/status",
            json={"status": "active"},
        )
        self.assertEqual(reactivated.status_code, 200)

    def test_product_persists_catalog_and_supplier_ids_with_controlled_gender(self):
        supplier = self.create_supplier(document="")
        brand = self.create_catalog("/api/brands", "Mova")
        category = self.create_catalog("/api/categories", "Fitness")
        size = self.create_catalog("/api/sizes", "M")
        color = self.create_catalog("/api/colors", "Preto")
        product = self.client.post(
            "/api/stock-entries",
            headers={"Idempotency-Key": "supplier-test-product-1"},
            json={
                "quantity": 4,
                "product": {
                    "barcode": "789000000001",
                    "name": "Legging",
                    "gender": "Feminino",
                    "brandId": brand["id"],
                    "categoryId": category["id"],
                    "sizeId": size["id"],
                    "colorId": color["id"],
                    "supplierId": supplier["id"],
                    "cost": 50,
                    "price": 100,
                },
            },
        )
        self.assertEqual(product.status_code, 201, product.get_json())
        saved = product.get_json()["data"]["product"]
        self.assertEqual(saved["brandId"], brand["id"])
        self.assertEqual(saved["supplierId"], supplier["id"])
        invalid_gender = self.client.post(
            "/api/stock-entries",
            headers={"Idempotency-Key": "supplier-test-product-2"},
            json={
                "quantity": 1,
                "product": {
                    "barcode": "789000000002",
                    "name": "Produto",
                    "gender": "Outro",
                    "brandId": brand["id"],
                    "categoryId": category["id"],
                    "supplierId": supplier["id"],
                    "cost": 10,
                    "price": 20,
                },
            },
        )
        self.assertEqual(invalid_gender.status_code, 400)

    def test_brand_rename_updates_current_product_but_not_historical_sale_snapshot(self):
        brand = self.create_catalog("/api/brands", "Marca A")
        category = self.create_catalog("/api/categories", "Fitness")
        supplier = self.create_supplier(document="")
        response = self.client.post(
            "/api/stock-entries",
            headers={"Idempotency-Key": "supplier-brand-history-product"},
            json={
                "quantity": 2,
                "product": {
                    "barcode": "789000000003",
                    "name": "Top",
                    "gender": "Feminino",
                    "brandId": brand["id"],
                    "categoryId": category["id"],
                    "supplierId": supplier["id"],
                    "cost": 5,
                    "price": 10,
                },
            },
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        product = response.get_json()["data"]["product"]
        with server.connect_db() as conn:
            conn.execute(
                """
                INSERT INTO sales (
                    id, store_id, customer_id, customer_name, subtotal, discount,
                    total, cost_total, status, created_at, updated_at
                ) VALUES ('VENDA001', 'matriz', '', 'Venda simples', 10, 0, 10, 5,
                          'completed', '2026-07-23T10:00:00Z', '2026-07-23T10:00:00Z')
                """
            )
            conn.execute(
                """
                INSERT INTO sale_items (
                    id, sale_id, product_id, barcode, name, brand, quantity,
                    unit_cost, unit_price, total
                ) VALUES ('item-1', 'VENDA001', ?, ?, 'Top', 'Marca A', 1, 5, 10, 10)
                """,
                (product["id"], product["barcode"]),
            )
        response = self.client.put(f"/api/brands/{brand['id']}", json={"name": "Marca B"})
        self.assertEqual(response.status_code, 200)
        with sqlite3.connect(server.DB_PATH) as connection:
            current_brand = connection.execute(
                "SELECT brand_name FROM products WHERE id = ?", (product["id"],)
            ).fetchone()[0]
            historic_brand = connection.execute(
                "SELECT brand FROM sale_items WHERE id = 'item-1'"
            ).fetchone()[0]
        self.assertEqual(current_brand, "Marca B")
        self.assertEqual(historic_brand, "Marca A")

    def test_cash_outflow_requires_active_expense_category_and_persists_its_id(self):
        categories = self.client.get("/api/expense-categories").get_json()["data"]
        category = next(item for item in categories if item["name"] == "Gasolina")
        opening = self.client.post("/api/cash-movements", json={
            "direction": "in",
            "type": "opening",
            "description": "Saldo para teste",
            "method": "cash",
            "amount": 100,
        })
        self.assertEqual(opening.status_code, 201, opening.get_json())
        response = self.client.post("/api/cash-movements", json={
            "direction": "out",
            "type": category["name"],
            "expenseCategoryId": category["id"],
            "description": "Abastecimento",
            "method": "cash",
            "amount": 50,
        })
        self.assertEqual(response.status_code, 201, response.get_json())
        movement = response.get_json()["data"]["cash"][0]
        self.assertEqual(movement["expenseCategoryId"], category["id"])
        with sqlite3.connect(server.DB_PATH) as connection:
            row = connection.execute(
                "SELECT type, expense_category_id FROM cash_movements WHERE id = ?",
                (movement["id"],),
            ).fetchone()
            state = json.loads(
                connection.execute("SELECT data FROM app_state WHERE id = 1").fetchone()[0]
            )
        self.assertEqual(row, ("Gasolina", category["id"]))
        self.assertEqual(state["cash"][0]["expenseCategoryId"], category["id"])

        changed = self.client.post(
            f"/api/expense-categories/{category['id']}/status",
            json={"status": "deactivated"},
        )
        self.assertEqual(changed.status_code, 200)
        blocked = self.client.post("/api/cash-movements", json={
            "direction": "out",
            "type": category["name"],
            "expenseCategoryId": category["id"],
            "description": "Nova despesa",
            "method": "cash",
            "amount": 25,
        })
        self.assertEqual(blocked.status_code, 400)

    def test_frontend_exposes_stage_three_quick_actions_and_supplier_filters(self):
        project_root = Path(__file__).resolve().parents[1]
        html = (project_root / "index.html").read_text(encoding="utf-8")
        script = (project_root / "script.js").read_text(encoding="utf-8")
        for element_id in (
            "newProductBrandButton",
            "newProductCategoryButton",
            "newProductSizeButton",
            "newProductColorButton",
            "payableNewSupplierButton",
            "supplierFinancialFilter",
        ):
            self.assertIn(f'id="{element_id}"', html)
        self.assertIn("function openQuickProductCatalog", script)
        self.assertIn("function openSupplierFromPayable", script)
        self.assertIn('expenseCategoryId: expenseCategory?.id || ""', script)


if __name__ == "__main__":
    unittest.main()
