from __future__ import annotations

import gc
import json
import os
import sqlite3
import tempfile
import unittest
from unittest import mock

from flask import session

from database_migrations.migrations.v015_card_reconciliation import MIGRATION_015
from database_migrations.registry import MIGRATIONS
from database_migrations.runner import run_database_migrations
from environment_config import EnvironmentConfig
import server


AUTHORIZED_ENV = {
    "APP_ENV": "development",
    "MOVA_ALLOW_MIGRATIONS": "true",
}


class PostgresPathOnSQLite:
    def __init__(self, path: str):
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.statements: list[str] = []
        self.committed = False
        self.rolled_back = False

    def execute(self, sql, params=()):
        self.statements.append(sql)
        return self.connection.execute(sql.replace(" FOR UPDATE", ""), params)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        if exc_type:
            self.connection.rollback()
            self.rolled_back = True
        else:
            self.connection.commit()
            self.committed = True
        self.connection.close()


class CardReconciliationBusinessRulesTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original = (
            server.ENVIRONMENT,
            server.USE_POSTGRES,
            server.DATABASE_URL,
            server.DB_PATH,
        )
        server.ENVIRONMENT = EnvironmentConfig(
            "development",
            "configured",
            False,
            False,
        )
        server.USE_POSTGRES = False
        server.DATABASE_URL = ""
        server.DB_PATH = os.path.join(
            self.temp_dir.name,
            "card-reconciliation.db",
        )
        run_database_migrations(
            environ=AUTHORIZED_ENV,
            sqlite_path=server.DB_PATH,
            create_database=True,
        )
        state = server.default_state()
        state["receivables"] = []
        state["cash"] = []
        with server.connect_db() as connection:
            connection.execute(
                "INSERT INTO stores (id, name, created_at) VALUES (?, ?, ?)",
                ("matriz", "Matriz", "2026-07-26T10:00:00+00:00"),
            )
            connection.execute(
                """
                INSERT INTO app_state (id, data, updated_at)
                VALUES (1, ?, ?)
                """,
                (
                    json.dumps(state, ensure_ascii=False),
                    "2026-07-26T10:00:00+00:00",
                ),
            )
            for identifier, role in (
                ("admin", "admin"),
                ("operator", "operator"),
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
                        "2026-07-26T10:00:00+00:00",
                    ),
                )
        self.client = server.app.test_client()

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

    def authenticate(self, identifier="operator"):
        role = "admin" if identifier == "admin" else "operator"
        with self.client.session_transaction() as flask_session:
            flask_session["user"] = {
                "id": identifier,
                "name": identifier.title(),
                "login": identifier,
                "role": role,
                "active": True,
            }

    def add_receivable(
        self,
        identifier: str,
        amount: float = 100,
        *,
        method: str = "credit",
        status: str = "cardPending",
        received: float = 0,
    ):
        open_amount = round(amount - received, 2)
        modality = "Débito" if method == "debit" else "Crédito 1x"
        with server.connect_db() as connection:
            connection.execute(
                """
                INSERT INTO receivables (
                    id, store_id, sale_id, customer_name, method, amount,
                    received, status, due_date, installment, created_at,
                    updated_at, modality_name, card_installments, tax_percent,
                    gross_amount, fee_amount, net_amount, original_due_date,
                    open_amount, version, difference_amount
                ) VALUES (?, 'matriz', ?, 'Cliente Teste', ?, ?, ?, ?, ?,
                          'origin:test', ?, ?, ?, 1, 2, ?, 2, ?, ?, ?, 0, 0)
                """,
                (
                    identifier,
                    f"VENDA-{identifier}",
                    method,
                    amount,
                    received,
                    status,
                    "2026-07-27",
                    "2026-07-26T12:00:00+00:00",
                    "2026-07-26T12:00:00+00:00",
                    modality,
                    amount + 2,
                    amount,
                    "2026-07-27",
                    open_amount,
                ),
            )
        return {
            "receivableId": identifier,
            "amount": open_amount,
            "expectedBalance": open_amount,
            "expectedVersion": 0,
            "closeWithDivergence": False,
            "divergenceNote": "",
        }

    @staticmethod
    def payload(items, total=None, **overrides):
        data = {
            "receiptDate": "2026-07-26",
            "totalReceived": (
                round(sum(float(item["amount"]) for item in items), 2)
                if total is None
                else total
            ),
            "note": "Depósito da operadora",
            "items": items,
        }
        data.update(overrides)
        return data

    def post_reconciliation(self, payload, key="reconciliation-key"):
        return self.client.post(
            "/api/card-reconciliations",
            json=payload,
            headers={"Idempotency-Key": key},
        )

    def scalar(self, sql, params=()):
        with sqlite3.connect(server.DB_PATH) as connection:
            return connection.execute(sql, params).fetchone()[0]

    def row(self, sql, params=()):
        with sqlite3.connect(server.DB_PATH) as connection:
            connection.row_factory = sqlite3.Row
            return connection.execute(sql, params).fetchone()

    def test_migration_is_additive_registered_and_cross_database(self):
        self.assertIn(MIGRATION_015, MIGRATIONS)
        self.assertEqual(MIGRATION_015.version, 15)
        self.assertEqual(
            MIGRATION_015.sqlite_statements,
            MIGRATION_015.postgresql_statements,
        )
        self.assertFalse(any(
            statement.lstrip().upper().startswith(("DROP ", "DELETE "))
            for statement in MIGRATION_015.sqlite_statements
        ))
        self.assertEqual(
            self.scalar("SELECT MAX(version) FROM schema_migrations"),
            18,
        )

    def test_requires_session_and_allows_operator_and_admin_listing(self):
        response = self.client.get("/api/card-reconciliations/receivables")
        self.assertEqual(response.status_code, 401)
        for identifier in ("operator", "admin"):
            self.authenticate(identifier)
            response = self.client.get(
                "/api/card-reconciliations/receivables"
            )
            self.assertEqual(response.status_code, 200, response.get_json())
            self.assertIn("summary", response.get_json()["data"])

    def test_listing_filters_paginates_and_summarizes_real_receivables(self):
        self.add_receivable("card-list-credit", amount=120, method="credit")
        self.add_receivable("card-list-debit", amount=80, method="debit")
        self.authenticate()

        response = self.client.get(
            "/api/card-reconciliations/receivables",
            query_string={
                "search": "VENDA-card-list-credit",
                "method": "credit:1",
                "status": "cardPending",
                "page": 1,
                "pageSize": 5,
            },
        )

        self.assertEqual(response.status_code, 200, response.get_json())
        data = response.get_json()["data"]
        self.assertEqual(data["pagination"]["total"], 1)
        self.assertEqual(len(data["items"]), 1)
        self.assertEqual(data["items"][0]["id"], "card-list-credit")
        self.assertEqual(data["items"][0]["differenceAmount"], 0)
        self.assertEqual(data["summary"]["openTotal"], 200)

    def test_individual_exact_reconciliation_is_atomic_idempotent_and_audited(self):
        item = self.add_receivable("card-exact")
        self.authenticate()
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
            first = self.post_reconciliation(self.payload([item]), "exact-key")
            replay = self.post_reconciliation(self.payload([item]), "exact-key")
        self.assertEqual(first.status_code, 201, first.get_json())
        self.assertEqual(replay.status_code, 200, replay.get_json())
        self.assertTrue(replay.get_json()["replayed"])
        self.assertEqual(
            replay.get_json()["data"],
            first.get_json()["data"],
        )
        receivable = self.row(
            "SELECT status, received, open_amount FROM receivables WHERE id = ?",
            ("card-exact",),
        )
        self.assertEqual(receivable["status"], "paid")
        self.assertEqual(receivable["received"], 100)
        self.assertEqual(receivable["open_amount"], 0)
        self.assertEqual(
            self.scalar(
                "SELECT COUNT(*) FROM cash_movements "
                "WHERE origin_type = 'card_reconciliation'"
            ),
            1,
        )
        self.assertEqual(
            self.scalar("SELECT COUNT(*) FROM card_reconciliations"),
            1,
        )
        self.assertEqual(
            self.scalar(
                "SELECT COUNT(*) FROM audit_logs "
                "WHERE module = 'card_reconciliation'"
            ),
            1,
        )

    def test_partial_then_explicit_divergence_preserves_difference(self):
        item = self.add_receivable("card-partial")
        self.authenticate()
        partial = {**item, "amount": 40}
        response = self.post_reconciliation(
            self.payload([partial], total=40),
            "partial-key",
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        current = self.row(
            "SELECT status, received, open_amount, version "
            "FROM receivables WHERE id = 'card-partial'"
        )
        self.assertEqual(current["status"], "cardPartial")
        self.assertEqual(current["open_amount"], 60)
        divergent = {
            "receivableId": "card-partial",
            "amount": 50,
            "expectedBalance": 60,
            "expectedVersion": current["version"],
            "closeWithDivergence": True,
            "divergenceNote": "Taxa divergente confirmada",
        }
        response = self.post_reconciliation(
            self.payload([divergent], total=50),
            "divergence-key",
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        current = self.row(
            "SELECT status, received, open_amount, difference_amount "
            "FROM receivables WHERE id = 'card-partial'"
        )
        self.assertEqual(current["status"], "cardDivergent")
        self.assertEqual(current["received"], 90)
        self.assertEqual(current["open_amount"], 0)
        self.assertEqual(current["difference_amount"], -10)

    def test_batch_creates_one_cash_entry_and_requires_exact_allocation_total(self):
        first = self.add_receivable("card-batch-a", 60, method="debit")
        second = self.add_receivable("card-batch-b", 90)
        self.authenticate()
        mismatch = self.post_reconciliation(
            self.payload([first, second], total=140),
            "batch-mismatch",
        )
        self.assertEqual(mismatch.status_code, 409)
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM cash_movements"), 0)
        response = self.post_reconciliation(
            self.payload([first, second]),
            "batch-key",
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        self.assertEqual(
            response.get_json()["data"]["reconciliation"]["itemCount"],
            2,
        )
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM cash_movements"), 1)
        self.assertEqual(
            self.scalar("SELECT COUNT(*) FROM card_reconciliation_items"),
            2,
        )

    def test_stale_version_rejects_whole_batch_without_side_effects(self):
        item = self.add_receivable("card-stale")
        item["expectedVersion"] = 9
        self.authenticate()
        response = self.post_reconciliation(
            self.payload([item]),
            "stale-key",
        )
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.get_json()["code"], "STALE_RECEIVABLE")
        for table in (
            "card_reconciliations",
            "card_reconciliation_items",
            "cash_movements",
            "receivable_payments",
        ):
            self.assertEqual(self.scalar(f"SELECT COUNT(*) FROM {table}"), 0)

    def test_reversal_is_whole_traceable_and_idempotent(self):
        first = self.add_receivable("card-reverse-a", 60)
        second = self.add_receivable("card-reverse-b", 40)
        self.authenticate()
        created = self.post_reconciliation(
            self.payload([first, second]),
            "reverse-origin",
        )
        reconciliation_id = created.get_json()["data"]["reconciliation"]["id"]
        headers = {"Idempotency-Key": "reverse-key"}
        payload = {"reason": "Depósito estornado pela operadora"}
        reversed_response = self.client.post(
            f"/api/card-reconciliations/{reconciliation_id}/reversal",
            json=payload,
            headers=headers,
        )
        replay = self.client.post(
            f"/api/card-reconciliations/{reconciliation_id}/reversal",
            json=payload,
            headers=headers,
        )
        self.assertEqual(
            reversed_response.status_code,
            201,
            reversed_response.get_json(),
        )
        self.assertEqual(replay.status_code, 200, replay.get_json())
        self.assertTrue(replay.get_json()["replayed"])
        statuses = {
            row["id"]: row["status"]
            for row in self.rows(
                "SELECT id, status FROM receivables ORDER BY id"
            )
        }
        self.assertEqual(statuses, {
            "card-reverse-a": "cardPending",
            "card-reverse-b": "cardPending",
        })
        self.assertEqual(
            self.scalar(
                "SELECT COUNT(*) FROM cash_movements "
                "WHERE origin_type = 'card_reconciliation_reversal'"
            ),
            1,
        )
        self.assertEqual(
            self.scalar(
                "SELECT COUNT(*) FROM receivable_payments "
                "WHERE status = 'reversed'"
            ),
            2,
        )

    def rows(self, sql, params=()):
        with sqlite3.connect(server.DB_PATH) as connection:
            connection.row_factory = sqlite3.Row
            return connection.execute(sql, params).fetchall()

    def test_audit_failure_rolls_back_everything(self):
        item = self.add_receivable("card-rollback")
        with server.app.test_request_context("/"):
            session["user"] = {
                "id": "operator",
                "name": "Operator",
                "login": "operator",
                "role": "operator",
                "active": True,
            }
            with mock.patch.object(
                server,
                "record_audit",
                side_effect=RuntimeError("audit failure"),
            ):
                with self.assertRaisesRegex(RuntimeError, "audit failure"):
                    server.persist_card_reconciliation(
                        self.payload([item]),
                        "rollback-key",
                    )
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM cash_movements"), 0)
        self.assertEqual(
            self.scalar("SELECT COUNT(*) FROM card_reconciliations"),
            0,
        )
        current = self.row(
            "SELECT status, received, open_amount FROM receivables "
            "WHERE id = 'card-rollback'"
        )
        self.assertEqual(tuple(current), ("cardPending", 0, 100))

    def test_postgresql_path_uses_row_locks_and_same_transaction(self):
        item = self.add_receivable("card-postgres")
        connections = []

        def connect():
            connection = PostgresPathOnSQLite(server.DB_PATH)
            connections.append(connection)
            return connection

        with server.app.test_request_context("/"):
            session["user"] = {
                "id": "operator",
                "name": "Operator",
                "login": "operator",
                "role": "operator",
                "active": True,
            }
            with (
                mock.patch.object(server, "USE_POSTGRES", True),
                mock.patch.object(server, "connect_db", side_effect=connect),
            ):
                result, replayed = server.persist_card_reconciliation(
                    self.payload([item]),
                    "postgres-key",
                )
        self.assertFalse(replayed)
        self.assertEqual(result["reconciliation"]["itemCount"], 1)
        self.assertEqual(len(connections), 1)
        self.assertTrue(connections[0].committed)
        self.assertFalse(connections[0].rolled_back)
        self.assertTrue(any(
            "FOR UPDATE" in statement
            for statement in connections[0].statements
        ))


if __name__ == "__main__":
    unittest.main()
