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

from database_migrations.runner import run_database_migrations
from environment_config import EnvironmentConfig
import server


AUTHORIZED_ENV = {
    "APP_ENV": "development",
    "MOVA_ALLOW_MIGRATIONS": "true",
}


class PostgresPathOnSQLite:
    def __init__(self, path: str, statements: list[str]):
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.statements = statements

    def execute(self, sql, params=()):
        self.statements.append(" ".join(sql.split()))
        return self.connection.execute(sql.replace(" FOR UPDATE", ""), params)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        if exc_type:
            self.connection.rollback()
        else:
            self.connection.commit()
        self.connection.close()


class ReportsBusinessRulesTest(unittest.TestCase):
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
        server.DB_PATH = os.path.join(self.temp_dir.name, "reports.db")
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
        self.authenticate("operator")
        self.brand = self.create_catalog("/api/brands", "Mova Histórica")
        self.category = self.create_catalog("/api/categories", "Fitness")
        self.size = self.create_catalog("/api/sizes", "M")
        self.color = self.create_catalog("/api/colors", "Preto")
        supplier = self.client.post(
            "/api/suppliers",
            json={
                "name": "Fornecedor Relatórios",
                "email": "reports-supplier@example.test",
            },
        )
        self.assertEqual(supplier.status_code, 201, supplier.get_json())
        self.supplier = supplier.get_json()["data"]
        customer = self.client.post(
            "/api/customers",
            json={
                "name": "Cliente Relatórios",
                "cpf": "52998224725",
                "phone": "48999991111",
                "limit": 1000,
            },
        )
        self.assertEqual(customer.status_code, 201, customer.get_json())
        self.customer = customer.get_json()["data"]
        self.product = self.create_product()
        self.sale = self.create_sale()
        self.create_operational_records()

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
            headers={"Idempotency-Key": "report-product-opening"},
            json={
                "quantity": 6,
                "product": {
                    "barcode": "789900001601",
                    "name": "Legging Relatório",
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

    def create_sale(self) -> dict:
        response = self.client.post(
            "/api/sales",
            headers={"Idempotency-Key": "report-sale"},
            json={
                "customerId": self.customer["id"],
                "items": [{
                    "productId": self.product["id"],
                    "quantity": 1,
                    "practicedUnitPrice": 100,
                    "unitDiscount": 0,
                    "unitAddition": 0,
                }],
                "discount": 0,
                "addition": 0,
                "payments": [
                    {"method": "cash", "amount": 40},
                    {"method": "pix", "amount": 60},
                ],
            },
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()["data"]["sale"]

    def create_operational_records(self):
        cash = self.client.post(
            "/api/cash-movements",
            headers={"Idempotency-Key": "report-cash-out"},
            json={
                "direction": "out",
                "type": "Gasolina",
                "description": "Despesa de teste",
                "method": "cash",
                "amount": 10,
            },
        )
        self.assertEqual(cash.status_code, 201, cash.get_json())
        payable = self.client.post(
            "/api/payables",
            json={
                "supplierId": self.supplier["id"],
                "category": "Mercadorias",
                "amount": 80,
                "issueDate": server.datetime.now(server.STORE_TIMEZONE).date().isoformat(),
                "dueDate": server.datetime.now(server.STORE_TIMEZONE).date().isoformat(),
            },
        )
        self.assertEqual(payable.status_code, 201, payable.get_json())
        conditional = self.client.post(
            "/api/conditionals",
            headers={"Idempotency-Key": "report-conditional"},
            json={
                "customerId": self.customer["id"],
                "items": [{
                    "productId": self.product["id"],
                    "quantity": 1,
                    "unitPrice": 100,
                    "unitCost": 50,
                }],
            },
        )
        self.assertEqual(conditional.status_code, 201, conditional.get_json())
        today = server.datetime.now(server.STORE_TIMEZONE).date().isoformat()
        now = server.utc_now()
        with server.connect_db() as connection:
            connection.execute(
                """
                INSERT INTO receivables (
                    id, store_id, sale_id, customer_id, customer_name,
                    method, amount, received, status, due_date,
                    installment, created_at, updated_at, open_amount,
                    original_due_date
                ) VALUES (?, 'matriz', ?, ?, ?, 'storeCredit', 120, 20,
                          'open', ?, '1/2', ?, ?, 100, ?)
                """,
                (
                    "report-credit",
                    self.sale["id"],
                    self.customer["id"],
                    self.customer["name"],
                    today,
                    now,
                    now,
                    today,
                ),
            )

    def test_catalog_and_sensitive_permissions_are_enforced_by_backend(self):
        with self.client.session_transaction() as flask_session:
            flask_session.clear()
        self.assertEqual(self.client.get("/api/reports/catalog").status_code, 401)
        self.assertEqual(self.client.get("/api/reports/sales").status_code, 401)

        self.authenticate("operator")
        catalog = self.client.get("/api/reports/catalog")
        self.assertEqual(catalog.status_code, 200)
        operator_keys = {item["key"] for item in catalog.get_json()["data"]}
        self.assertEqual(len(operator_keys), 7)
        self.assertNotIn("profit", operator_keys)
        self.assertEqual(
            self.client.get("/api/reports/profit?period=30days").status_code,
            403,
        )
        stock = self.client.get("/api/reports/stock")
        self.assertEqual(stock.status_code, 200, stock.get_json())
        stock_data = stock.get_json()["data"]
        self.assertNotIn("stockValue", {item["key"] for item in stock_data["summary"]})
        self.assertNotIn("stockValue", stock_data["rows"][0])
        sales_data = self.client.get("/api/reports/sales?period=30days").get_json()["data"]
        self.assertNotIn("profit", {item["key"] for item in sales_data["summary"]})
        self.assertNotIn("profit", {item["key"] for item in sales_data["columns"]})
        self.assertNotIn("profit", sales_data["rows"][0])

        self.authenticate("admin")
        admin_catalog = self.client.get("/api/reports/catalog").get_json()["data"]
        self.assertEqual(len(admin_catalog), 8)
        profit = self.client.get("/api/reports/profit?period=30days")
        self.assertEqual(profit.status_code, 200, profit.get_json())
        stock = self.client.get("/api/reports/stock").get_json()["data"]
        self.assertIn("stockValue", {item["key"] for item in stock["summary"]})

    def test_all_official_reports_use_relational_data_and_filters(self):
        self.authenticate("admin")
        for key in (
            "sales",
            "sold-products",
            "cash",
            "store-credit",
            "payables",
            "stock",
            "conditionals",
            "profit",
        ):
            response = self.client.get(f"/api/reports/{key}?period=30days")
            self.assertEqual(response.status_code, 200, (key, response.get_json()))
            data = response.get_json()["data"]
            self.assertEqual(data["key"], key)
            self.assertTrue(data["columns"])
            self.assertIn("pagination", data)
        sales = self.client.get(
            "/api/reports/sales?period=30days&method=pix&customer=Cliente"
        ).get_json()["data"]
        self.assertEqual(sales["pagination"]["total"], 1)
        self.assertIn("Dinheiro + PIX", sales["rows"][0]["payments"])
        stock = self.client.get(
            "/api/reports/stock?stockStatus=with_stock"
        ).get_json()["data"]
        self.assertEqual(stock["rows"][0]["reservedStock"], 1)
        self.assertEqual(
            stock["rows"][0]["availableStock"],
            stock["rows"][0]["realStock"] - 1,
        )

    def test_pagination_dates_empty_state_and_contract_validation(self):
        self.authenticate("operator")
        response = self.client.get("/api/reports/sales?period=30days&pageSize=5")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["data"]["pagination"]["pageSize"], 5)
        self.assertEqual(
            self.client.get(
                "/api/reports/sales?period=custom&start=2026-02-02&end=2026-01-01"
            ).status_code,
            400,
        )
        empty = self.client.get(
            "/api/reports/sales?period=custom&start=2000-01-01&end=2000-01-02"
        ).get_json()["data"]
        self.assertEqual(empty["rows"], [])
        self.assertEqual(empty["pagination"]["total"], 0)
        self.assertEqual(
            self.client.get("/api/reports/sales?period=invalid").status_code,
            400,
        )

    def test_returns_reduce_sales_products_and_profit_in_the_occurrence_period(self):
        self.authenticate("admin")
        supply = self.client.post(
            "/api/cash-movements",
            headers={"Idempotency-Key": "report-return-supply"},
            json={
                "direction": "in",
                "type": "Suprimento",
                "description": "Saldo para devolução de teste",
                "method": "cash",
                "amount": 20,
            },
        )
        self.assertEqual(supply.status_code, 201, supply.get_json())
        response = self.client.post(
            "/api/returns",
            headers={"Idempotency-Key": "report-return"},
            json={
                "saleId": self.sale["id"],
                "reason": "Desistência",
                "notes": "Devolução para validar relatório líquido",
                "items": [{
                    "saleItemId": self.sale["items"][0]["id"],
                    "quantity": 1,
                    "physicalCondition": "resellable",
                    "unitPrice": 0.01,
                }],
            },
        )
        self.assertEqual(response.status_code, 201, response.get_json())

        sales = self.client.get("/api/reports/sales?period=30days").get_json()["data"]
        sales_summary = {item["key"]: item["value"] for item in sales["summary"]}
        self.assertEqual(sales_summary["gross"], 100)
        self.assertEqual(sales_summary["returns"], 100)
        self.assertEqual(sales_summary["net"], 0)
        self.assertEqual(sales_summary["pieces"], 0)
        self.assertEqual(sales_summary["profit"], 0)

        products = self.client.get(
            "/api/reports/sold-products?period=30days"
        ).get_json()["data"]
        self.assertEqual(products["rows"][0]["quantity"], 0)
        self.assertEqual(products["rows"][0]["netTotal"], 0)
        products_summary = {
            item["key"]: item["value"] for item in products["summary"]
        }
        self.assertEqual(products_summary["pieces"], 0)
        self.assertEqual(products_summary["net"], 0)

    def test_legacy_payable_amount_is_preserved_without_relational_payments(self):
        self.authenticate("admin")
        with server.connect_db() as connection:
            payable = connection.execute(
                "SELECT id FROM payables ORDER BY created_at LIMIT 1"
            ).fetchone()
            connection.execute(
                """
                UPDATE payables
                SET paid_amount = 25, interest = 2, fine = 1,
                    discount = 3, open_amount = 53
                WHERE id = ?
                """,
                (payable["id"],),
            )
        report = self.client.get(
            "/api/reports/payables?period=30days"
        ).get_json()["data"]
        row = report["rows"][0]
        self.assertEqual(row["paidAmount"], 25)
        self.assertEqual(row["interest"], 2)
        self.assertEqual(row["fine"], 1)
        self.assertEqual(row["discount"], 3)
        self.assertEqual(row["openAmount"], 52)

    def test_pdf_xlsx_exports_are_server_side_and_profit_export_is_audited(self):
        self.authenticate("operator")
        pdf = self.client.get(
            "/api/reports/sales/export?period=30days&format=pdf"
        )
        self.assertEqual(pdf.status_code, 200)
        self.assertTrue(pdf.data.startswith(b"%PDF"))
        xlsx = self.client.get(
            "/api/reports/sales/export?period=30days&format=xlsx"
        )
        self.assertEqual(xlsx.status_code, 200)
        self.assertTrue(xlsx.data.startswith(b"PK"))
        self.assertEqual(
            self.client.get(
                "/api/reports/sales/export?period=30days&format=csv"
            ).status_code,
            400,
        )
        self.authenticate("admin")
        profit = self.client.get(
            "/api/reports/profit/export?period=30days&format=xlsx"
        )
        self.assertEqual(profit.status_code, 200)
        with server.connect_db() as connection:
            row = connection.execute(
                """
                SELECT details FROM audit_logs
                WHERE module = 'report_profit' AND action = 'export'
                ORDER BY created_at DESC LIMIT 1
                """
            ).fetchone()
        self.assertIsNotNone(row)
        details = json.loads(row["details"])
        self.assertEqual(details["format"], "xlsx")
        self.assertNotIn("rows", details)

    def test_report_reads_do_not_rebuild_state_and_postgresql_adapter_path_works(self):
        self.authenticate("admin")
        with mock.patch.object(
            server,
            "write_state",
            side_effect=AssertionError("write_state não pode ser chamado"),
        ), mock.patch.object(
            server,
            "sync_business_tables",
            side_effect=AssertionError("sync_business_tables não pode ser chamado"),
        ):
            response = self.client.get("/api/reports/cash?period=30days")
        self.assertEqual(response.status_code, 200, response.get_json())

        statements: list[str] = []
        original_use_postgres = server.USE_POSTGRES
        server.USE_POSTGRES = True
        try:
            with server.app.test_request_context("/api/reports/stock"):
                session["user"] = {
                    "id": "admin",
                    "name": "Admin",
                    "role": "admin",
                }
                with mock.patch.object(
                    server,
                    "connect_db",
                    side_effect=lambda: PostgresPathOnSQLite(
                        server.DB_PATH,
                        statements,
                    ),
                ):
                    report = server.build_report_document(
                        "stock",
                        {},
                        is_admin=True,
                    )
            self.assertEqual(report["key"], "stock")
        finally:
            server.USE_POSTGRES = original_use_postgres
        self.assertTrue(any("FROM products" in sql for sql in statements))

    def test_frontend_has_loading_error_empty_and_server_exports(self):
        script = Path(server.APP_DIR, "script.js").read_text(encoding="utf-8")
        markup = Path(server.APP_DIR, "index.html").read_text(encoding="utf-8")
        self.assertIn("renderReportLoading", script)
        self.assertIn("renderReportError", script)
        self.assertIn("Nenhum registro encontrado.", script)
        self.assertIn("/export?", script)
        self.assertIn('data-tab="relatorios"', markup)
        self.assertIn('id="reportNavigation"', markup)
        self.assertIn('id="reportTableBody"', markup)


if __name__ == "__main__":
    unittest.main()
