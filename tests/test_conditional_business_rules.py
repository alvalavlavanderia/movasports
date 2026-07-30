import gc
import json
import os
import sqlite3
import tempfile
import unittest
from unittest import mock

from database_migrations.migrations.v012_transactional_conditionals import (
    MIGRATION_012,
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
    def __init__(self, path):
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.statements = []

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


class ConditionalBusinessRulesTest(unittest.TestCase):
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
        server.DB_PATH = os.path.join(self.temp_dir.name, "conditionals.db")
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
            connection.execute(
                """
                INSERT INTO users (
                    id, store_id, name, login, password_hash,
                    role, active, updated_at
                )
                VALUES ('operator', 'matriz', 'Operador', 'operator',
                        'not-used', 'operator', 1, ?)
                """,
                ("2026-07-25T10:00:00+00:00",),
            )
        self.client = server.app.test_client()
        self.authenticate()
        self.brand = self.catalog("/api/brands", "Mova")
        self.category = self.catalog("/api/categories", "Fitness")
        self.size = self.catalog("/api/sizes", "M")
        self.color = self.catalog("/api/colors", "Preto")
        self.supplier = self.client.post(
            "/api/suppliers",
            json={
                "name": "Fornecedor Condicional",
                "email": "fornecedor-condicional@example.test",
            },
        ).get_json()["data"]
        self.customer = self.client.post(
            "/api/customers",
            json={
                "name": "Cliente Condicional",
                "cpf": "52998224725",
                "phone": "48999991111",
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

    def authenticate(self):
        with self.client.session_transaction() as flask_session:
            flask_session["user"] = {
                "id": "operator",
                "name": "Operador",
                "login": "operator",
                "role": "operator",
                "active": True,
            }

    def catalog(self, endpoint, name):
        response = self.client.post(endpoint, json={"name": name})
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()["data"]

    def create_product(self):
        response = self.client.post(
            "/api/stock-entries",
            headers={"Idempotency-Key": "conditional-product-opening"},
            json={
                "quantity": 5,
                "product": {
                    "barcode": "789900000501",
                    "name": "Legging Condicional",
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

    def conditional_payload(self, quantity=3):
        return {
            "customerId": self.customer["id"],
            "items": [{
                "productId": self.product["id"],
                "quantity": quantity,
                "unitPrice": 1,
                "unitCost": 1,
            }],
        }

    def create_conditional(self, key="conditional-create", quantity=3):
        response = self.client.post(
            "/api/conditionals",
            headers={"Idempotency-Key": key},
            json=self.conditional_payload(quantity),
        )
        self.assertIn(response.status_code, {200, 201}, response.get_json())
        return response

    def scalar(self, sql, params=()):
        with sqlite3.connect(server.DB_PATH) as connection:
            return connection.execute(sql, params).fetchone()[0]

    def row(self, sql, params=()):
        with sqlite3.connect(server.DB_PATH) as connection:
            connection.row_factory = sqlite3.Row
            return connection.execute(sql, params).fetchone()

    def state(self):
        with sqlite3.connect(server.DB_PATH) as connection:
            data = connection.execute(
                "SELECT data FROM app_state WHERE id = 1"
            ).fetchone()[0]
        return json.loads(data)

    def test_migration_is_additive_and_cross_database(self):
        self.assertEqual(MIGRATION_012.version, 12)
        self.assertEqual(
            MIGRATION_012.sqlite_statements,
            MIGRATION_012.postgresql_statements,
        )
        self.assertFalse(any(
            statement.lstrip().upper().startswith(("DROP ", "DELETE "))
            for statement in MIGRATION_012.sqlite_statements
        ))
        self.assertEqual(
            self.scalar("SELECT MAX(version) FROM schema_migrations"),
            18,
        )

    def test_creation_reserves_stock_with_server_snapshots_and_is_idempotent(self):
        with mock.patch.object(
            server,
            "write_state",
            side_effect=AssertionError("write_state called"),
        ), mock.patch.object(
            server,
            "sync_business_tables",
            side_effect=AssertionError("sync_business_tables called"),
        ):
            first = self.create_conditional()
            second = self.create_conditional()
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 200)
        conditional = first.get_json()["data"]
        self.assertEqual(conditional["id"], "COND001")
        self.assertEqual(conditional["status"], "open")
        self.assertEqual(conditional["items"][0]["unitPrice"], 100)
        self.assertEqual(conditional["items"][0]["unitCost"], 50)
        self.assertEqual(conditional["pendingPieces"], 3)
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM conditionals"), 1)
        movement = self.row(
            """
            SELECT real_before, real_after, reserved_before, reserved_after
            FROM inventory_movements
            WHERE movement_type = 'conditional_reserve'
            """
        )
        self.assertEqual(tuple(movement), (5, 5, 0, 3))
        self.assertEqual(
            self.state()["conditionals"][0]["id"],
            conditional["id"],
        )
        self.assertEqual(
            self.scalar(
                "SELECT COUNT(*) FROM audit_logs "
                "WHERE module = 'conditional' AND action = 'create'"
            ),
            1,
        )

    def test_return_partial_and_sale_conversion_preserve_reservation(self):
        conditional = self.create_conditional().get_json()["data"]
        item = conditional["items"][0]
        returned = self.client.post(
            f"/api/conditionals/{conditional['id']}/returns",
            headers={"Idempotency-Key": "conditional-return-1"},
            json={"items": [{
                "conditionalItemId": item["id"],
                "returnedQuantity": 1,
                "purchaseQuantity": 1,
            }]},
        )
        self.assertEqual(returned.status_code, 201, returned.get_json())
        result = returned.get_json()["data"]
        self.assertEqual(result["conditional"]["pendingPieces"], 2)
        self.assertEqual(
            result["conditional"]["items"][0]["pendingSaleQuantity"],
            1,
        )
        movement = self.row(
            """
            SELECT reserved_before, reserved_after
            FROM inventory_movements
            WHERE movement_type = 'conditional_return'
            """
        )
        self.assertEqual(tuple(movement), (3, 2))
        draft = result["saleDraft"]
        sale = self.client.post(
            "/api/sales",
            headers={"Idempotency-Key": "conditional-sale-1"},
            json={
                **draft,
                "discount": 0,
                "addition": 0,
                "payments": [{"method": "cash", "amount": 100}],
            },
        )
        self.assertEqual(sale.status_code, 201, sale.get_json())
        sale_data = sale.get_json()["data"]
        self.assertEqual(
            sale_data["sale"]["conditionalId"],
            conditional["id"],
        )
        self.assertEqual(sale_data["conditional"]["pendingPieces"], 1)
        sale_movement = self.row(
            """
            SELECT real_before, real_after, reserved_before, reserved_after
            FROM inventory_movements
            WHERE movement_type = 'sale'
            """
        )
        self.assertEqual(tuple(sale_movement), (5, 4, 2, 1))
        self.assertEqual(
            self.scalar(
                "SELECT COUNT(*) FROM conditional_sale_links WHERE sale_id = ?",
                (sale_data["sale"]["id"],),
            ),
            1,
        )

    def test_return_all_finalizes_and_cancellation_requires_reason(self):
        conditional = self.create_conditional(quantity=1).get_json()["data"]
        item = conditional["items"][0]
        response = self.client.post(
            f"/api/conditionals/{conditional['id']}/returns",
            headers={"Idempotency-Key": "conditional-return-all"},
            json={"items": [{
                "conditionalItemId": item["id"],
                "returnedQuantity": 1,
                "purchaseQuantity": 0,
            }]},
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        self.assertEqual(
            response.get_json()["data"]["conditional"]["status"],
            "finalized",
        )
        missing = self.client.post(
            f"/api/conditionals/{conditional['id']}/cancel",
            json={"reason": " "},
        )
        self.assertEqual(missing.status_code, 400)
        cancelled = self.client.post(
            f"/api/conditionals/{conditional['id']}/cancel",
            json={"reason": "Cliente desistiu após devolver todas as peças."},
        )
        self.assertEqual(cancelled.status_code, 200, cancelled.get_json())
        self.assertEqual(cancelled.get_json()["data"]["status"], "cancelled")

    def test_cannot_cancel_or_return_more_than_pending(self):
        conditional = self.create_conditional(quantity=1).get_json()["data"]
        blocked = self.client.post(
            f"/api/conditionals/{conditional['id']}/cancel",
            json={"reason": "Cancelamento indevido"},
        )
        self.assertEqual(blocked.status_code, 409)
        item = conditional["items"][0]
        excessive = self.client.post(
            f"/api/conditionals/{conditional['id']}/returns",
            headers={"Idempotency-Key": "conditional-return-excess"},
            json={"items": [{
                "conditionalItemId": item["id"],
                "returnedQuantity": 2,
                "purchaseQuantity": 0,
            }]},
        )
        self.assertEqual(excessive.status_code, 409)
        self.assertEqual(
            self.scalar(
                "SELECT returned_quantity FROM conditional_items WHERE id = ?",
                (item["id"],),
            ),
            0,
        )

    def test_multiple_partial_returns_are_historical_and_idempotent(self):
        conditional = self.create_conditional(quantity=3).get_json()["data"]
        item = conditional["items"][0]
        first = self.client.post(
            f"/api/conditionals/{conditional['id']}/returns",
            headers={"Idempotency-Key": "conditional-multiple-return-1"},
            json={"items": [{
                "conditionalItemId": item["id"],
                "returnedQuantity": 1,
                "purchaseQuantity": 0,
            }]},
        )
        replay = self.client.post(
            f"/api/conditionals/{conditional['id']}/returns",
            headers={"Idempotency-Key": "conditional-multiple-return-1"},
            json={"items": [{
                "conditionalItemId": item["id"],
                "returnedQuantity": 1,
                "purchaseQuantity": 0,
            }]},
        )
        second = self.client.post(
            f"/api/conditionals/{conditional['id']}/returns",
            headers={"Idempotency-Key": "conditional-multiple-return-2"},
            json={"items": [{
                "conditionalItemId": item["id"],
                "returnedQuantity": 2,
                "purchaseQuantity": 0,
            }]},
        )
        self.assertEqual(first.status_code, 201, first.get_json())
        self.assertEqual(replay.status_code, 200, replay.get_json())
        self.assertTrue(replay.get_json()["replayed"])
        self.assertEqual(second.status_code, 201, second.get_json())
        self.assertEqual(second.get_json()["data"]["conditional"]["status"], "finalized")
        self.assertEqual(
            self.scalar(
                "SELECT COUNT(*) FROM conditional_returns WHERE conditional_id = ?",
                (conditional["id"],),
            ),
            2,
        )
        self.assertEqual(
            len(second.get_json()["data"]["conditional"]["returns"]),
            2,
        )

    def test_routes_require_backend_session(self):
        conditional = self.create_conditional(quantity=1).get_json()["data"]
        with self.client.session_transaction() as flask_session:
            flask_session.clear()
        listed = self.client.get("/api/conditionals")
        created = self.client.post("/api/conditionals", json=self.conditional_payload(1))
        returned = self.client.post(
            f"/api/conditionals/{conditional['id']}/returns",
            json={"items": []},
        )
        cancelled = self.client.post(
            f"/api/conditionals/{conditional['id']}/cancel",
            json={"reason": "Sem sessão"},
        )
        for response in (listed, created, returned, cancelled):
            self.assertEqual(response.status_code, 401)
            self.assertEqual(
                response.get_json(),
                {"ok": False, "error": "Login obrigatório."},
            )

    def test_blocked_customer_and_unavailable_stock_are_rejected(self):
        blocked_customer = self.client.post(
            "/api/customers",
            json={
                "name": "Cliente Bloqueado Condicional",
                "cpf": "11144477735",
                "phone": "48999992222",
                "limit": 500,
            },
        ).get_json()["data"]
        with server.connect_db() as connection:
            connection.execute(
                """
                UPDATE customers SET status = 'blocked'
                WHERE id = ?
                """,
                (blocked_customer["id"],),
            )
        blocked = self.client.post(
            "/api/conditionals",
            headers={"Idempotency-Key": "conditional-blocked-customer"},
            json={
                **self.conditional_payload(1),
                "customerId": blocked_customer["id"],
            },
        )
        self.assertEqual(blocked.status_code, 409)
        self.create_conditional(quantity=5)
        unavailable = self.client.post(
            "/api/conditionals",
            headers={"Idempotency-Key": "conditional-no-stock"},
            json=self.conditional_payload(1),
        )
        self.assertEqual(unavailable.status_code, 409)

    def test_audit_failure_rolls_back_creation(self):
        with mock.patch.object(
            server,
            "record_audit",
            side_effect=RuntimeError("audit failure"),
        ):
            with self.assertRaises(RuntimeError):
                with server.app.test_request_context("/api/conditionals"):
                    server.session["user"] = {
                        "id": "operator",
                        "name": "Operador",
                        "role": "operator",
                    }
                    server.persist_conditional_creation(
                        self.conditional_payload(),
                        "conditional-audit-failure",
                    )
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM conditionals"), 0)
        self.assertEqual(
            self.scalar(
                "SELECT COUNT(*) FROM inventory_movements "
                "WHERE movement_type = 'conditional_reserve'"
            ),
            0,
        )

    def test_audit_failure_rolls_back_return_and_reservation_release(self):
        conditional = self.create_conditional(quantity=2).get_json()["data"]
        item = conditional["items"][0]
        with mock.patch.object(
            server,
            "record_audit",
            side_effect=RuntimeError("audit failure"),
        ):
            with self.assertRaises(RuntimeError):
                with server.app.test_request_context("/api/conditionals"):
                    server.session["user"] = {
                        "id": "operator",
                        "name": "Operador",
                        "role": "operator",
                    }
                    server.persist_conditional_return(
                        conditional["id"],
                        {"items": [{
                            "conditionalItemId": item["id"],
                            "returnedQuantity": 1,
                            "purchaseQuantity": 0,
                        }]},
                        "conditional-return-audit-failure",
                    )
        self.assertEqual(
            self.scalar(
                "SELECT returned_quantity FROM conditional_items WHERE id = ?",
                (item["id"],),
            ),
            0,
        )
        self.assertEqual(
            self.scalar(
                "SELECT COUNT(*) FROM conditional_returns WHERE conditional_id = ?",
                (conditional["id"],),
            ),
            0,
        )
        self.assertEqual(
            self.scalar(
                "SELECT COUNT(*) FROM inventory_movements "
                "WHERE movement_type = 'conditional_return'"
            ),
            0,
        )

    def test_frontend_exposes_operational_conditional_flow(self):
        root = os.path.dirname(os.path.dirname(__file__))
        with open(os.path.join(root, "index.html"), encoding="utf-8") as source:
            html = source.read()
        with open(os.path.join(root, "script.js"), encoding="utf-8") as source:
            javascript = source.read()
        with open(os.path.join(root, "style.css"), encoding="utf-8") as source:
            stylesheet = source.read()
        for element_id in (
            "conditionalOpenCount",
            "conditionalOverdueCount",
            "conditionalPieceCount",
            "conditionalValue",
            "conditionalStatusFilter",
            "conditionalStartFilter",
            "conditionalEndFilter",
        ):
            self.assertIn(f'id="{element_id}"', html)
        self.assertIn("/returns`", javascript)
        self.assertIn("conditionalReturnId", javascript)
        self.assertIn("pendingConditionalSaleDraft", javascript)
        self.assertIn("Continuar venda", javascript)
        self.assertNotIn("renderConditionalOpenListLegacy", javascript)
        self.assertIn("conditional-summary-grid operational-kpis", html)
        self.assertIn("card-reconciliation-summary operational-kpis", html)
        for element_id in (
            "cardOpenTotal",
            "cardDueToday",
            "cardReceivedMonth",
            "cardDivergenceTotal",
        ):
            self.assertIn(f'id="{element_id}"', html)
        self.assertIn(".operational-kpis article {", stylesheet)
        self.assertIn(".operational-kpis svg {", stylesheet)
        self.assertIn(".operational-kpis .green", stylesheet)
        self.assertIn(".operational-kpis .pink", stylesheet)

    def test_postgresql_adapter_path_uses_locks(self):
        server.USE_POSTGRES = True
        adapters = []

        def connect():
            adapter = _PostgresPathOnSQLite(server.DB_PATH)
            adapters.append(adapter)
            return adapter

        with mock.patch.object(server, "connect_db", side_effect=connect):
            with server.app.test_request_context("/api/conditionals"):
                server.session["user"] = {
                    "id": "operator",
                    "name": "Operador",
                    "role": "operator",
                }
                result, replayed = server.persist_conditional_creation(
                    self.conditional_payload(1),
                    "conditional-postgresql",
                )
        server.USE_POSTGRES = False
        self.assertFalse(replayed)
        self.assertEqual(result["conditional"]["id"], "COND001")
        joined = "\n".join(
            statement
            for adapter in adapters
            for statement in adapter.statements
        )
        self.assertIn("pg_advisory_xact_lock", joined)
        self.assertIn("FOR UPDATE", joined)


if __name__ == "__main__":
    unittest.main()
