from __future__ import annotations

import gc
import json
import os
import sqlite3
import tempfile
import unittest
from unittest import mock

from database_migrations.migrations.v011_store_credit_business_rules import (
    MIGRATION_011,
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


class StoreCreditBusinessRulesTest(unittest.TestCase):
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
        server.DB_PATH = os.path.join(self.temp_dir.name, "store-credit.db")
        run_database_migrations(
            environ=AUTHORIZED_ENV,
            sqlite_path=server.DB_PATH,
            create_database=True,
        )
        state = server.default_state()
        state["customers"] = [{
            "id": "customer-1",
            "name": "Cliente Teste",
            "cpf": "52998224725",
            "limit": 500,
            "status": "active",
            "isDefault": False,
        }]
        with server.connect_db() as connection:
            connection.execute(
                "INSERT INTO stores (id, name, created_at) VALUES (?, ?, ?)",
                ("matriz", "Matriz", "2026-07-25T10:00:00+00:00"),
            )
            connection.execute(
                "INSERT INTO app_state (id, data, updated_at) VALUES (1, ?, ?)",
                (
                    json.dumps(state, ensure_ascii=False),
                    "2026-07-25T10:00:00+00:00",
                ),
            )
            connection.execute(
                """
                INSERT INTO users (
                    id, store_id, name, login, password_hash,
                    role, active, updated_at
                ) VALUES ('operator', 'matriz', 'Operador', 'operator',
                          'not-used', 'operator', 1, ?)
                """,
                ("2026-07-25T10:00:00+00:00",),
            )
            connection.execute(
                """
                INSERT INTO customers (
                    id, store_id, name, cpf, status, credit_limit, is_default,
                    created_at, updated_at
                ) VALUES (?, 'matriz', ?, ?, 'active', 500, 0, ?, ?)
                """,
                (
                    "customer-1",
                    "Cliente Teste",
                    "52998224725",
                    "2026-07-25T10:00:00+00:00",
                    "2026-07-25T10:00:00+00:00",
                ),
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
        self.insert_receivable()

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

    def insert_receivable(
        self,
        identifier: str = "parcel-1",
        amount: float = 100,
        due_date: str = "2026-08-25",
        installment: str = "1/2",
    ):
        receivable = {
            "id": identifier,
            "saleId": "VENDA001",
            "salePaymentId": "sale-payment-1",
            "customerId": "customer-1",
            "customerName": "Cliente Teste",
            "method": "storeCredit",
            "amount": amount,
            "received": 0,
            "openAmount": amount,
            "discountTotal": 0,
            "interestTotal": 0,
            "fineTotal": 0,
            "additionTotal": 0,
            "status": "open",
            "dueDate": due_date,
            "originalDueDate": due_date,
            "paidAt": "",
            "lastPaymentAt": "",
            "installment": installment,
            "version": 0,
            "createdAt": "2026-07-25T10:00:00+00:00",
            "updatedAt": "2026-07-25T10:00:00+00:00",
        }
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
                VALUES (?, 'matriz', ?, ?, ?, 'storeCredit', ?, 0, 'open', ?,
                        NULL, NULL, ?, ?, ?, ?, ?, 0, ?, ?, ?, 0, 0, 0, 0, 0)
                """,
                (
                    identifier,
                    receivable["saleId"],
                    receivable["customerId"],
                    receivable["customerName"],
                    amount,
                    due_date,
                    installment,
                    receivable["createdAt"],
                    receivable["updatedAt"],
                    receivable["salePaymentId"],
                    amount,
                    amount,
                    due_date,
                    amount,
                ),
            )
            state = server.locked_app_state(connection)
            state["receivables"] = [
                receivable,
                *(state.get("receivables") or []),
            ]
            server.persist_product_app_state(
                connection,
                state,
                receivable["updatedAt"],
            )
        return receivable

    def scalar(self, sql: str, params=()):
        with sqlite3.connect(server.DB_PATH) as connection:
            return connection.execute(sql, params).fetchone()[0]

    def row(self, sql: str, params=()):
        with sqlite3.connect(server.DB_PATH) as connection:
            connection.row_factory = sqlite3.Row
            return connection.execute(sql, params).fetchone()

    def post_payment(self, key: str, **overrides):
        payload = {
            "customerId": "customer-1",
            "method": "cash",
            "payments": [{"receivableId": "parcel-1", "amount": 100}],
            "discountType": "value",
            "discountValue": 0,
            "interest": 0,
            "fine": 0,
            "addition": 0,
            "description": "Recebimento teste",
        }
        payload.update(overrides)
        return self.client.post(
            "/api/receivables/payments",
            headers={"Idempotency-Key": key},
            json=payload,
        )

    def test_migration_is_additive_and_cross_database(self):
        self.assertEqual(MIGRATION_011.version, 11)
        self.assertEqual(
            MIGRATION_011.sqlite_statements,
            MIGRATION_011.postgresql_statements,
        )
        self.assertFalse(any(
            statement.lstrip().upper().startswith(("DROP ", "DELETE "))
            for statement in MIGRATION_011.sqlite_statements
        ))
        self.assertEqual(
            self.scalar("SELECT MAX(version) FROM schema_migrations"),
            18,
        )

    def test_payment_with_discount_and_manual_charges_is_atomic(self):
        with (
            mock.patch.object(server, "write_state", side_effect=AssertionError),
            mock.patch.object(
                server, "sync_business_tables", side_effect=AssertionError
            ),
        ):
            response = self.post_payment(
                "payment-adjusted",
                discountType="percent",
                discountValue=10,
                interest=3,
                fine=2,
                addition=1,
            )
        self.assertEqual(response.status_code, 200, response.get_json())
        row = self.row("SELECT * FROM receivables WHERE id = 'parcel-1'")
        self.assertEqual(row["open_amount"], 0)
        self.assertEqual(row["received"], 90)
        self.assertEqual(row["discount_total"], 10)
        self.assertEqual(row["interest_total"], 3)
        self.assertEqual(row["fine_total"], 2)
        self.assertEqual(row["addition_total"], 1)
        self.assertEqual(row["status"], "paid")
        payment = self.row(
            "SELECT * FROM receivable_payments WHERE receivable_id = 'parcel-1'"
        )
        self.assertEqual(payment["principal_amount"], 90)
        self.assertEqual(payment["settled_amount"], 100)
        self.assertEqual(payment["amount"], 96)
        self.assertEqual(
            self.scalar(
                "SELECT amount FROM cash_movements WHERE ref_id = 'parcel-1'"
            ),
            96,
        )
        self.assertEqual(
            self.scalar(
                "SELECT COUNT(*) FROM audit_logs "
                "WHERE module = 'receivable' AND action = 'pay'"
            ),
            1,
        )
        state = json.loads(
            self.scalar("SELECT data FROM app_state WHERE id = 1")
        )
        stored = next(
            item for item in state["receivables"] if item["id"] == "parcel-1"
        )
        self.assertEqual(stored["openAmount"], 0)

    def test_full_discount_closes_without_cash_and_negative_is_rejected(self):
        response = self.post_payment(
            "payment-full-discount",
            discountType="percent",
            discountValue=100,
        )
        self.assertEqual(response.status_code, 200, response.get_json())
        self.assertEqual(
            self.scalar("SELECT COUNT(*) FROM cash_movements"),
            0,
        )
        self.assertEqual(
            self.scalar(
                "SELECT status FROM receivables WHERE id = 'parcel-1'"
            ),
            "paid",
        )

        self.insert_receivable("parcel-2", 50, "2026-09-25", "2/2")
        rejected = self.post_payment(
            "payment-negative",
            payments=[{"receivableId": "parcel-2", "amount": 50}],
            discountValue=51,
        )
        self.assertEqual(rejected.status_code, 409)
        self.assertEqual(
            rejected.get_json()["code"],
            "DISCOUNT_EXCEEDS_BALANCE",
        )
        self.assertEqual(
            self.scalar(
                "SELECT open_amount FROM receivables WHERE id = 'parcel-2'"
            ),
            50,
        )

    def test_partial_payment_idempotency_and_conflict(self):
        first = self.post_payment(
            "payment-partial",
            payments=[{"receivableId": "parcel-1", "amount": 40}],
        )
        replay = self.post_payment(
            "payment-partial",
            payments=[{"receivableId": "parcel-1", "amount": 40}],
        )
        self.assertEqual(first.status_code, 200, first.get_json())
        self.assertTrue(replay.get_json()["replayed"])
        self.assertEqual(
            self.scalar(
                "SELECT COUNT(*) FROM receivable_payments "
                "WHERE receivable_id = 'parcel-1'"
            ),
            1,
        )
        self.assertEqual(
            self.scalar(
                "SELECT open_amount FROM receivables WHERE id = 'parcel-1'"
            ),
            60,
        )
        conflict = self.post_payment(
            "payment-partial",
            payments=[{"receivableId": "parcel-1", "amount": 20}],
        )
        self.assertEqual(conflict.status_code, 409)
        self.assertEqual(conflict.get_json()["code"], "IDEMPOTENCY_CONFLICT")

    def test_card_payment_creates_net_pending_receivable(self):
        with server.connect_db() as connection:
            modality = server.normalize_card_modality_payload({
                "method": "credit",
                "installments": 2,
                "taxPercent": 5,
                "receivableDays": 2,
                "validFrom": "2020-01-01T00:00:00+00:00",
                "status": "active",
            })
            server.insert_card_modality(connection, modality)
        response = self.post_payment(
            "payment-card",
            method="credit",
            cardModalityId=modality["cardModalityId"],
        )
        self.assertEqual(response.status_code, 200, response.get_json())
        card = self.row(
            "SELECT * FROM receivables WHERE method = 'credit'"
        )
        self.assertEqual(card["gross_amount"], 100)
        self.assertEqual(card["fee_amount"], 5)
        self.assertEqual(card["net_amount"], 95)
        self.assertEqual(card["open_amount"], 95)
        self.assertEqual(card["installment"], "origin:parcel-1")
        self.assertEqual(
            self.scalar("SELECT COUNT(*) FROM cash_movements"),
            0,
        )

    def test_renegotiation_preserves_original_history_and_is_idempotent(self):
        payload = {
            "newDueDate": "2026-10-25",
            "paymentAmount": 20,
            "discount": 5,
            "interest": 3,
            "fine": 2,
            "addition": 0,
            "method": "pix",
            "reason": "Acordo com o cliente",
        }
        first = self.client.post(
            "/api/receivables/parcel-1/renegotiations",
            headers={"Idempotency-Key": "renegotiate-1"},
            json=payload,
        )
        replay = self.client.post(
            "/api/receivables/parcel-1/renegotiations",
            headers={"Idempotency-Key": "renegotiate-1"},
            json=payload,
        )
        self.assertEqual(first.status_code, 200, first.get_json())
        self.assertTrue(replay.get_json()["replayed"])
        row = self.row("SELECT * FROM receivables WHERE id = 'parcel-1'")
        self.assertEqual(row["original_due_date"], "2026-08-25")
        self.assertEqual(row["due_date"], "2026-10-25")
        self.assertEqual(row["open_amount"], 80)
        self.assertEqual(
            self.scalar("SELECT COUNT(*) FROM receivable_renegotiations"),
            1,
        )
        history = self.row("SELECT * FROM receivable_renegotiations")
        self.assertEqual(history["previous_open_amount"], 100)
        self.assertEqual(history["new_open_amount"], 80)
        self.assertEqual(history["user_id"], "operator")
        self.assertEqual(
            self.scalar(
                "SELECT amount FROM cash_movements WHERE ref_id = 'parcel-1'"
            ),
            20,
        )

    def test_audit_failure_rolls_back_every_payment_effect(self):
        with mock.patch.object(
            server,
            "record_audit",
            side_effect=RuntimeError("audit failed"),
        ):
            response = self.post_payment("payment-rollback")
        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            self.scalar(
                "SELECT open_amount FROM receivables WHERE id = 'parcel-1'"
            ),
            100,
        )
        self.assertEqual(
            self.scalar("SELECT COUNT(*) FROM receivable_payments"),
            0,
        )
        self.assertEqual(
            self.scalar("SELECT COUNT(*) FROM cash_movements"),
            0,
        )

    def test_postgresql_path_uses_row_locks_and_transactional_helpers(self):
        adapters = []

        def connect():
            adapter = _PostgresPathOnSQLite(server.DB_PATH)
            adapters.append(adapter)
            return adapter

        with (
            mock.patch.object(server, "USE_POSTGRES", True),
            mock.patch.object(server, "connect_db", side_effect=connect),
            server.app.test_request_context(),
        ):
            from flask import session

            session["user"] = {
                "id": "operator",
                "name": "Operador",
                "role": "operator",
                "active": True,
            }
            result, replayed = server.persist_receivable_payment(
                {
                    "customerId": "customer-1",
                    "method": "cash",
                    "payments": [{
                        "receivableId": "parcel-1",
                        "amount": 30,
                    }],
                },
                "postgres-payment",
            )
        self.assertFalse(replayed)
        self.assertEqual(result["totalReceived"], 30)
        statements = "\n".join(
            statement
            for adapter in adapters
            for statement in adapter.statements
        )
        self.assertIn("FOR UPDATE", statements)

    def test_calendar_months_preserve_base_day_and_month_end(self):
        self.assertEqual(
            server.store_credit_due_dates("2026-01-31", 3),
            ["2026-01-31", "2026-02-28", "2026-03-31"],
        )
        with self.assertRaises(server.SaleOperationError):
            server.store_credit_due_dates("invalid", 2)


if __name__ == "__main__":
    unittest.main()
