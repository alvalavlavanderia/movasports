from __future__ import annotations

from datetime import date
import gc
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest import mock

from database_migrations.migrations.v017_alert_user_states import MIGRATION_017
from database_migrations.registry import MIGRATIONS
from database_migrations.runner import run_database_migrations
from environment_config import EnvironmentConfig
import server


AUTHORIZED_ENV = {
    "APP_ENV": "development",
    "MOVA_ALLOW_MIGRATIONS": "true",
}


class PostgreSQLPathOnSQLite:
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


class AlertScoreDashboardBusinessRulesTest(unittest.TestCase):
    TODAY = date(2026, 7, 29)
    NOW = "2026-07-29T15:00:00+00:00"

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
        server.DB_PATH = os.path.join(self.temp_dir.name, "business-17.db")
        server.app.config["TESTING"] = True
        run_database_migrations(
            environ=AUTHORIZED_ENV,
            sqlite_path=server.DB_PATH,
            create_database=True,
        )
        state = server.default_state()
        with server.connect_db() as connection:
            connection.execute(
                "INSERT INTO stores (id, name, created_at) VALUES (?, ?, ?)",
                ("matriz", "Mova Sports", self.NOW),
            )
            connection.execute(
                "INSERT INTO app_state (id, data, updated_at) VALUES (1, ?, ?)",
                (json.dumps(state, ensure_ascii=False), self.NOW),
            )
            for identifier, role in (
                ("admin", "admin"),
                ("operator", "operator"),
                ("operator-2", "operator"),
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
                        self.NOW,
                    ),
                )
            connection.execute(
                """
                INSERT INTO customers (
                    id, store_id, name, cpf, status, credit_limit,
                    is_default, created_at, updated_at
                ) VALUES (
                    'customer-1', 'matriz', 'Cliente Etapa 17',
                    '52998224725', 'active', 1000, 0, ?, ?
                )
                """,
                (self.NOW, self.NOW),
            )
        self.client = server.app.test_client()
        self.authenticate("admin")
        self.today_patch = mock.patch.object(
            server,
            "operational_today",
            return_value=self.TODAY,
        )
        self.today_patch.start()

    def tearDown(self):
        self.today_patch.stop()
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

    def insert_product(
        self,
        identifier: str,
        *,
        stock: int,
        cost: float = 10,
        entered_at: str = "2026-01-01T12:00:00+00:00",
    ):
        with server.connect_db() as connection:
            connection.execute(
                """
                INSERT INTO products (
                    id, store_id, barcode, name, brand_name, stock,
                    min_stock, active, cost, price, updated_at,
                    created_at, stock_entered_at
                ) VALUES (?, 'matriz', ?, ?, 'Marca Atual', ?, 0, 1, ?, 25, ?, ?, ?)
                """,
                (
                    identifier,
                    f"789{identifier[-3:]:0>3}",
                    f"Produto {identifier}",
                    stock,
                    cost,
                    self.NOW,
                    entered_at,
                    entered_at,
                ),
            )

    def insert_receivable(
        self,
        identifier: str,
        *,
        amount: float = 100,
        received: float = 0,
        open_amount: float | None = None,
        status: str = "open",
        due_date: str = "2026-07-20",
        created_at: str = "2026-06-20T15:00:00+00:00",
    ):
        if open_amount is None:
            open_amount = max(0, amount - received)
        with server.connect_db() as connection:
            connection.execute(
                """
                INSERT INTO receivables (
                    id, store_id, sale_id, customer_id, customer_name, method,
                    amount, received, status, due_date, paid_at,
                    last_payment_at, installment, created_at, updated_at,
                    sale_payment_id, gross_amount, fee_amount, net_amount,
                    original_due_date, open_amount, discount_total,
                    interest_total, fine_total, addition_total, version
                )
                VALUES (
                    ?, 'matriz', ?, 'customer-1', 'Cliente Etapa 17',
                    'storeCredit', ?, ?, ?, ?, NULL, NULL, '1/1', ?, ?,
                    ?, ?, 0, ?, ?, ?, 0, 0, 0, 0, 0
                )
                """,
                (
                    identifier,
                    f"sale-{identifier}",
                    amount,
                    received,
                    status,
                    due_date,
                    created_at,
                    created_at,
                    f"payment-{identifier}",
                    amount,
                    amount,
                    due_date,
                    open_amount,
                ),
            )

    def insert_receivable_payment(
        self,
        receivable_id: str,
        *,
        principal: float,
        settled: float,
        paid_at: str,
        discount: float = 0,
    ):
        with server.connect_db() as connection:
            connection.execute(
                """
                INSERT INTO receivable_payments (
                    id, store_id, receivable_id, sale_id, customer_id,
                    method, amount, created_at, principal_amount,
                    settled_amount, discount_amount, status
                ) VALUES (?, 'matriz', ?, ?, 'customer-1', 'cash', ?, ?, ?, ?, ?, 'active')
                """,
                (
                    f"receipt-{receivable_id}",
                    receivable_id,
                    f"sale-{receivable_id}",
                    principal,
                    paid_at,
                    principal,
                    settled,
                    discount,
                ),
            )

    def insert_sale(
        self,
        identifier: str,
        *,
        created_at: str = "2026-07-29T15:00:00+00:00",
        status: str = "completed",
        total: float = 100,
        cost: float = 40,
        quantity: int = 2,
        brand: str = "Marca Histórica",
        payments: tuple[tuple[str, float], ...] = (("cash", 40), ("pix", 60)),
    ):
        with server.connect_db() as connection:
            connection.execute(
                """
                INSERT INTO sales (
                    id, store_id, customer_id, customer_name, subtotal,
                    discount, total, cost_total, status, created_at, updated_at
                ) VALUES (?, 'matriz', 'customer-1', 'Cliente Etapa 17', ?, 0, ?, ?, ?, ?, ?)
                """,
                (
                    identifier,
                    total,
                    total,
                    cost,
                    status,
                    created_at,
                    created_at,
                ),
            )
            connection.execute(
                """
                INSERT INTO sale_items (
                    id, sale_id, product_id, barcode, name, brand,
                    quantity, unit_cost, unit_price, total, net_total
                ) VALUES (?, ?, NULL, NULL, 'Item vendido', ?, ?, ?, ?, ?, ?)
                """,
                (
                    f"item-{identifier}",
                    identifier,
                    brand,
                    quantity,
                    cost / quantity,
                    total / quantity,
                    total,
                    total,
                ),
            )
            for index, (method, amount) in enumerate(payments):
                connection.execute(
                    """
                    INSERT INTO sale_payments (
                        id, sale_id, method, amount, installments,
                        status, created_at, gross_amount, net_amount
                    ) VALUES (?, ?, ?, ?, 1, 'registered', ?, ?, ?)
                    """,
                    (
                        f"sale-payment-{identifier}-{index}",
                        identifier,
                        method,
                        amount,
                        created_at,
                        amount,
                        amount,
                    ),
                )

    def insert_return(
        self,
        sale_id: str,
        *,
        amount: float = 30,
        cost: float = 10,
        quantity: int = 1,
        brand: str = "Marca Histórica",
        created_at: str = "2026-07-29T18:00:00+00:00",
    ):
        with server.connect_db() as connection:
            connection.execute(
                """
                INSERT INTO sale_returns (
                    id, store_id, sale_id, customer_name, total, reason,
                    created_at, status, origin, gross_total, net_total, cost_total
                ) VALUES (
                    'return-1', 'matriz', ?, 'Cliente Etapa 17', ?,
                    'Devolução de teste', ?, 'completed', 'commercial', ?, ?, ?
                )
                """,
                (sale_id, amount, created_at, amount, amount, cost),
            )
            connection.execute(
                """
                INSERT INTO sale_return_items (
                    id, return_id, product_id, product_name, action,
                    quantity, unit_price, total, brand, gross_total,
                    net_total, unit_cost, cost_total
                ) VALUES (
                    'return-item-1', 'return-1', NULL, 'Item vendido',
                    'return', ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    quantity,
                    amount / quantity,
                    amount,
                    brand,
                    amount,
                    amount,
                    cost / quantity,
                    cost,
                ),
            )
            for index, (method, returned) in enumerate(
                (("cash", amount / 2), ("pix", amount / 2))
            ):
                connection.execute(
                    """
                    INSERT INTO sale_return_allocations (
                        id, store_id, return_id, sale_payment_id, method,
                        gross_amount, pending_reduction, refunded_amount,
                        status, reconciliation_required, created_at
                    ) VALUES (?, 'matriz', 'return-1', ?, ?, ?, 0, ?, 'refunded', 0, ?)
                    """,
                    (
                        f"return-allocation-{index}",
                        f"sale-payment-{sale_id}-{index}",
                        method,
                        returned,
                        returned,
                        created_at,
                    ),
                )

    def test_migration_17_is_additive_registered_and_cross_database(self):
        self.assertIn(MIGRATION_017, MIGRATIONS)
        self.assertEqual(MIGRATION_017.version, 17)
        self.assertEqual(
            MIGRATION_017.sqlite_statements,
            MIGRATION_017.postgresql_statements,
        )
        self.assertFalse(any(
            statement.lstrip().upper().startswith(("DROP ", "DELETE ", "UPDATE "))
            for statement in MIGRATION_017.sqlite_statements
        ))
        with sqlite3.connect(server.DB_PATH) as connection:
            self.assertEqual(
                connection.execute(
                    "SELECT MAX(version) FROM schema_migrations"
                ).fetchone()[0],
                18,
            )

    def test_alerts_cover_official_types_and_exclude_zero_stock(self):
        self.insert_product("product-last", stock=1)
        self.insert_product("product-zero", stock=0)
        self.insert_receivable("overdue-credit", due_date="2026-07-20")
        with server.connect_db() as connection:
            connection.execute(
                """
                INSERT INTO payables (
                    id, store_id, supplier, category, amount, issue_date,
                    due_date, paid_amount, fee, discount, status,
                    created_at, updated_at, open_amount
                ) VALUES
                    ('payable-today', 'matriz', 'Fornecedor Hoje', 'Despesa', 30,
                     '2026-07-01', '2026-07-29', 0, 0, 0, 'pending', ?, ?, 30),
                    ('payable-overdue', 'matriz', 'Fornecedor Atrasado', 'Despesa', 40,
                     '2026-07-01', '2026-07-18', 0, 0, 0, 'pending', ?, ?, 40)
                """,
                (self.NOW, self.NOW, self.NOW, self.NOW),
            )
            connection.execute(
                """
                INSERT INTO conditionals (
                    id, store_id, conditional_number, customer_id,
                    customer_name, status, checked_out_at,
                    expected_return_date, created_at, updated_at
                ) VALUES (
                    'conditional-overdue', 'matriz', 1, 'customer-1',
                    'Cliente Etapa 17', 'open', ?, '2026-07-20', ?, ?
                )
                """,
                (self.NOW, self.NOW, self.NOW),
            )
            connection.execute(
                """
                INSERT INTO conditional_items (
                    id, conditional_id, product_id, name, original_quantity,
                    returned_quantity, sold_quantity, pending_sale_quantity,
                    created_at, updated_at
                ) VALUES (
                    'conditional-item', 'conditional-overdue', 'product-zero',
                    'Produto condicional', 1, 0, 0, 0, ?, ?
                )
                """,
                (self.NOW, self.NOW),
            )

        response = self.client.get("/api/alerts?pageSize=100")

        self.assertEqual(response.status_code, 200, response.get_json())
        alerts = response.get_json()["data"]["items"]
        types = {item["type"] for item in alerts}
        self.assertEqual(types, {
            "store_credit_overdue",
            "conditional_overdue",
            "payable_due_today",
            "payable_overdue",
            "last_available_unit",
        })
        last_units = [
            item for item in alerts if item["type"] == "last_available_unit"
        ]
        self.assertEqual([item["entityId"] for item in last_units], ["product-last"])
        credit_alert = next(
            item for item in alerts if item["type"] == "store_credit_overdue"
        )
        self.assertEqual(credit_alert["count"], 1)
        self.assertEqual(credit_alert["amount"], 100)

    def test_alert_read_and_pin_states_are_isolated_per_user_and_resolve(self):
        self.insert_receivable("overdue-credit", due_date="2026-07-20")
        initial = self.client.get("/api/alerts").get_json()["data"]
        alert = initial["items"][0]
        self.assertFalse(alert["read"])
        self.assertEqual(initial["summary"]["unread"], 1)

        marked = self.client.post(
            f"/api/alerts/{alert['id']}/read",
            json={"read": True},
        )
        pinned = self.client.post(
            f"/api/alerts/{alert['id']}/pin",
            json={"pinned": True},
        )
        self.assertEqual(marked.status_code, 200, marked.get_json())
        self.assertEqual(pinned.status_code, 200, pinned.get_json())
        admin_state = self.client.get("/api/alerts").get_json()["data"]
        self.assertEqual(admin_state["summary"]["unread"], 0)
        self.assertTrue(admin_state["items"][0]["pinned"])

        self.authenticate("operator-2")
        operator_state = self.client.get("/api/alerts").get_json()["data"]
        self.assertEqual(operator_state["summary"]["unread"], 1)
        self.assertFalse(operator_state["items"][0]["pinned"])

        with server.connect_db() as connection:
            connection.execute(
                """
                UPDATE receivables
                SET open_amount = 0, received = amount, status = 'paid'
                WHERE id = 'overdue-credit'
                """
            )
        resolved = self.client.get("/api/alerts").get_json()["data"]
        self.assertEqual(resolved["summary"]["active"], 0)
        self.assertEqual(resolved["items"], [])

    def test_alert_filters_pagination_and_invalid_values_are_controlled(self):
        self.insert_product("product-last", stock=1)
        self.insert_receivable("overdue-credit", due_date="2026-07-20")
        filtered = self.client.get(
            "/api/alerts?priority=critical&module=store_credit&state=unread&pageSize=5"
        )
        self.assertEqual(filtered.status_code, 200, filtered.get_json())
        data = filtered.get_json()["data"]
        self.assertEqual(data["filteredTotal"], 1)
        self.assertEqual(data["pagination"]["page"], 1)
        self.assertEqual(data["items"][0]["type"], "store_credit_overdue")
        invalid = self.client.get("/api/alerts?priority=unknown")
        self.assertEqual(invalid.status_code, 400)

    def test_score_is_unavailable_without_credit_history(self):
        response = self.client.get("/api/customers/customer-1/score")
        self.assertEqual(response.status_code, 200, response.get_json())
        score = response.get_json()["data"]
        self.assertFalse(score["available"])
        self.assertIsNone(score["score"])
        self.assertEqual(score["directPurchases"], 0)

    def test_score_combines_payment_behavior_discount_and_direct_frequency(self):
        self.insert_receivable(
            "paid-credit",
            amount=100,
            received=80,
            open_amount=0,
            status="paid",
            due_date="2026-07-10",
        )
        self.insert_receivable_payment(
            "paid-credit",
            principal=80,
            settled=100,
            discount=20,
            paid_at="2026-07-10T15:00:00+00:00",
        )
        self.insert_sale(
            "direct-1",
            created_at="2026-07-01T15:00:00+00:00",
            quantity=1,
            payments=(("cash", 100),),
        )
        self.insert_sale(
            "direct-2",
            created_at="2026-07-02T15:00:00+00:00",
            quantity=1,
            payments=(("pix", 100),),
        )

        score = self.client.get(
            "/api/customers/customer-1/score"
        ).get_json()["data"]

        self.assertTrue(score["available"])
        self.assertEqual(score["creditPoints"], 80)
        self.assertEqual(score["directPurchasePoints"], 10)
        self.assertEqual(score["score"], 90)
        self.assertEqual(score["classification"], "Excelente")

    def test_current_overdue_credit_older_than_twelve_months_remains_in_score(self):
        self.insert_receivable(
            "old-overdue",
            amount=200,
            due_date="2025-01-15",
            created_at="2024-12-15T15:00:00+00:00",
        )

        score = self.client.get(
            "/api/customers/customer-1/score"
        ).get_json()["data"]

        self.assertTrue(score["available"])
        self.assertEqual(score["overdueBalance"], 200)
        self.assertEqual(score["overdueInstallments"], 1)
        self.assertEqual(score["overduePenalty"], 30)
        self.assertEqual(score["score"], 0)

    def test_score_preserves_overdue_history_before_renegotiation(self):
        self.insert_receivable(
            "renegotiated-credit",
            amount=100,
            due_date="2026-08-15",
        )
        with server.connect_db() as connection:
            connection.execute(
                """
                INSERT INTO receivable_renegotiations (
                    id, store_id, receivable_id, customer_id,
                    previous_due_date, new_due_date, previous_open_amount,
                    new_open_amount, reason, idempotency_key, request_hash,
                    response_json, created_at
                ) VALUES (
                    'renegotiation-score', 'matriz', 'renegotiated-credit',
                    'customer-1', '2026-06-01', '2026-08-15', 100, 100,
                    'Renegociacao de teste', 'score-renegotiation-key',
                    'score-renegotiation-hash', '{}',
                    '2026-07-01T15:00:00+00:00'
                )
                """
            )

        score = self.client.get(
            "/api/customers/customer-1/score"
        ).get_json()["data"]

        self.assertTrue(score["available"])
        self.assertEqual(score["creditPoints"], 24)
        self.assertEqual(score["score"], 24)
        self.assertEqual(score["factors"][0]["delayDays"], 30)

    def test_fully_returned_direct_sale_does_not_increase_score(self):
        self.insert_receivable(
            "paid-credit",
            amount=100,
            open_amount=0,
            received=100,
            status="paid",
            due_date="2026-07-10",
        )
        self.insert_receivable_payment(
            "paid-credit",
            principal=100,
            settled=100,
            paid_at="2026-07-10T15:00:00+00:00",
        )
        self.insert_sale(
            "returned-direct-sale",
            status="returned",
            created_at="2026-07-05T15:00:00+00:00",
            payments=(("cash", 100),),
        )

        score = self.client.get(
            "/api/customers/customer-1/score"
        ).get_json()["data"]

        self.assertTrue(score["available"])
        self.assertEqual(score["directPurchases"], 0)
        self.assertEqual(score["directPurchasePoints"], 0)
        self.assertEqual(score["score"], 80)

    def test_dashboard_uses_liquid_period_values_and_protects_operator(self):
        self.insert_sale("sale-valid")
        self.insert_return("sale-valid")
        self.insert_sale("sale-cancelled", status="cancelled", total=200, cost=80)

        admin_response = self.client.get("/api/dashboard?period=today")
        self.assertEqual(admin_response.status_code, 200, admin_response.get_json())
        admin = admin_response.get_json()["data"]
        self.assertEqual(admin["profile"], "admin")
        self.assertEqual(admin["metrics"]["todaySalesCount"], 1)
        self.assertEqual(admin["metrics"]["todayRevenue"], 70)
        self.assertEqual(admin["metrics"]["monthProfit"], 40)
        payment_rows = {
            item["method"]: item for item in admin["payments"]["rows"]
        }
        self.assertEqual(payment_rows["cash"]["gross"], 40)
        self.assertEqual(payment_rows["cash"]["returned"], 15)
        self.assertEqual(payment_rows["cash"]["net"], 25)
        self.assertEqual(payment_rows["pix"]["net"], 45)
        self.assertAlmostEqual(
            sum(
                item["percent"]
                for item in admin["payments"]["rows"]
                if item["chartValue"] > 0
            ),
            100,
        )
        self.assertEqual(admin["topBrands"], [{
            "name": "Marca Histórica",
            "qty": 1,
            "position": 1,
        }])

        self.authenticate("operator")
        operator_response = self.client.get("/api/dashboard?period=today")
        self.assertEqual(
            operator_response.status_code,
            200,
            operator_response.get_json(),
        )
        operator = operator_response.get_json()["data"]
        self.assertEqual(operator["profile"], "operator")
        for key in (
            "todayRevenue",
            "monthRevenue",
            "monthProfit",
            "stockValue",
            "creditOpen",
            "cashBalance",
            "payablesOpen",
        ):
            self.assertNotIn(key, operator["metrics"])
        for row in operator["payments"]["rows"]:
            self.assertNotIn("gross", row)
            self.assertNotIn("returned", row)
            self.assertNotIn("net", row)
        for row in operator["salesChart"]:
            self.assertNotIn("total", row)

    def test_dashboard_periods_empty_state_and_stopped_stock_use_available_units(self):
        self.insert_product("product-stopped", stock=5, cost=12)
        self.insert_product("product-reserved", stock=2, cost=20)
        with server.connect_db() as connection:
            connection.execute(
                """
                INSERT INTO conditionals (
                    id, store_id, conditional_number, customer_id,
                    customer_name, status, checked_out_at,
                    expected_return_date, created_at, updated_at
                ) VALUES (
                    'conditional-reservation', 'matriz', 2, 'customer-1',
                    'Cliente Etapa 17', 'open', ?, '2026-08-01', ?, ?
                )
                """,
                (self.NOW, self.NOW, self.NOW),
            )
            connection.execute(
                """
                INSERT INTO conditional_items (
                    id, conditional_id, product_id, name, original_quantity,
                    returned_quantity, sold_quantity, pending_sale_quantity,
                    created_at, updated_at
                ) VALUES (
                    'conditional-reserved-item', 'conditional-reservation',
                    'product-reserved', 'Produto reservado', 1, 0, 0, 0, ?, ?
                )
                """,
                (self.NOW, self.NOW),
            )
        self.insert_sale(
            "outside-period",
            created_at="2026-06-01T15:00:00+00:00",
            payments=(("cash", 100),),
        )

        response = self.client.get(
            "/api/dashboard?period=custom&start=2026-07-10&end=2026-07-12"
        )

        self.assertEqual(response.status_code, 200, response.get_json())
        data = response.get_json()["data"]
        self.assertEqual(data["period"]["start"], "2026-07-10")
        self.assertEqual(data["period"]["end"], "2026-07-12")
        self.assertTrue(all(row["salesCount"] == 0 for row in data["salesChart"]))
        self.assertFalse(data["payments"]["hasPositiveValues"])
        stopped = {item["id"]: item for item in data["stoppedProducts"]}
        self.assertEqual(stopped["product-stopped"]["availableStock"], 5)
        self.assertEqual(stopped["product-stopped"]["stoppedValue"], 60)
        self.assertEqual(stopped["product-reserved"]["availableStock"], 1)
        self.assertGreater(stopped["product-stopped"]["days"], 90)
        invalid = self.client.get(
            "/api/dashboard?period=custom&start=2026-07-12&end=2026-07-10"
        )
        self.assertEqual(invalid.status_code, 400)

    def test_dashboard_negative_payment_net_has_no_negative_chart_slice(self):
        self.insert_sale(
            "old-sale",
            created_at="2026-07-01T15:00:00+00:00",
            total=20,
            cost=10,
            quantity=1,
            payments=(("cash", 20),),
        )
        self.insert_return(
            "old-sale",
            amount=30,
            cost=10,
            created_at="2026-07-29T18:00:00+00:00",
        )

        result = self.client.get(
            "/api/dashboard?period=today"
        ).get_json()["data"]["payments"]
        cash = next(item for item in result["rows"] if item["method"] == "cash")

        self.assertLess(cash["net"], 0)
        self.assertEqual(cash["chartValue"], 0)
        self.assertEqual(cash["percent"], 0)
        self.assertTrue(result["hasNegativeValues"])
        self.assertFalse(result["hasPositiveValues"])

    def test_postgresql_adapter_path_supports_dashboard_alerts_and_user_state(self):
        self.insert_product("product-last", stock=1)
        self.insert_receivable("overdue-credit", due_date="2026-07-20")
        statements = []
        original_use_postgres = server.USE_POSTGRES
        server.USE_POSTGRES = True
        try:
            with mock.patch.object(
                server,
                "connect_db",
                side_effect=lambda: PostgreSQLPathOnSQLite(
                    server.DB_PATH,
                    statements,
                ),
            ), mock.patch.object(
                server,
                "refresh_session_user",
                side_effect=lambda: dict(server.session.get("user") or {}),
            ):
                dashboard = self.client.get("/api/dashboard?period=today")
                alerts = self.client.get("/api/alerts")
                alert_id = alerts.get_json()["data"]["items"][0]["id"]
                marked = self.client.post(
                    f"/api/alerts/{alert_id}/read",
                    json={"read": True},
                )
        finally:
            server.USE_POSTGRES = original_use_postgres
        self.assertEqual(dashboard.status_code, 200, dashboard.get_json())
        self.assertEqual(alerts.status_code, 200, alerts.get_json())
        self.assertEqual(marked.status_code, 200, marked.get_json())
        self.assertTrue(any("alert_user_states" in item for item in statements))
        self.assertTrue(any("ON CONFLICT" in item for item in statements))

    def test_frontend_exposes_official_states_actions_and_day_rollover(self):
        root = Path(__file__).resolve().parents[1]
        html = (root / "index.html").read_text(encoding="utf-8")
        script = (root / "script.js").read_text(encoding="utf-8")
        styles = (root / "style.css").read_text(encoding="utf-8")
        self.assertIn('id="alertBellButton"', html)
        self.assertIn('id="dashboardStatus"', html)
        self.assertIn('data-dashboard-action="sales-today"', html)
        self.assertIn('data-dashboard-action="alerts"', html)
        self.assertIn("startDashboardDayWatch()", script)
        self.assertIn("checkDashboardOperationalDay()", script)
        self.assertIn("data-alert-read", script)
        self.assertIn("Marcar como não lido", script)
        self.assertIn("Nenhuma venda no período selecionado.", script)
        self.assertIn("Nenhum pagamento no período selecionado.", script)
        self.assertNotIn("payment-menu-button", script)
        self.assertIn(".score-indicator", styles)
        self.assertIn(".dashboard-action-card", styles)


if __name__ == "__main__":
    unittest.main()
