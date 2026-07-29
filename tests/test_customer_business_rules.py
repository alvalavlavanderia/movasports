from __future__ import annotations

import gc
import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from environment_config import EnvironmentConfig
from database_migrations.runner import run_database_migrations
import server


AUTHORIZED_ENV = {
    "APP_ENV": "development",
    "MOVA_ALLOW_MIGRATIONS": "true",
}


class CustomerBusinessRulesTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original = {
            "environment": server.ENVIRONMENT,
            "use_postgres": server.USE_POSTGRES,
            "database_url": server.DATABASE_URL,
            "db_path": server.DB_PATH,
        }
        server.ENVIRONMENT = EnvironmentConfig(
            "development",
            "configured",
            False,
            False,
        )
        server.USE_POSTGRES = False
        server.DATABASE_URL = ""
        server.DB_PATH = os.path.join(self.temp_dir.name, "customers.db")
        run_database_migrations(
            environ=AUTHORIZED_ENV,
            sqlite_path=server.DB_PATH,
            create_database=True,
        )
        self.default_customer = server.default_customer_record(
            "2026-07-23T10:00:00+00:00"
        )
        state = server.default_state()
        state["customers"] = [self.default_customer]
        with server.connect_db() as conn:
            conn.execute(
                "INSERT INTO stores (id, name, created_at) VALUES (?, ?, ?)",
                ("matriz", "Matriz", "2026-07-23T10:00:00+00:00"),
            )
            conn.execute(
                "INSERT INTO app_state (id, data, updated_at) VALUES (1, ?, ?)",
                (
                    json.dumps(state, ensure_ascii=False),
                    "2026-07-23T10:00:00+00:00",
                ),
            )
            self.insert_user(conn, "admin", "Administrador", "admin")
            self.insert_user(conn, "operator", "Operador", "operator")
            server.upsert_customer(conn, self.default_customer)
        self.client = server.app.test_client()

    def tearDown(self):
        server.ENVIRONMENT = self.original["environment"]
        server.USE_POSTGRES = self.original["use_postgres"]
        server.DATABASE_URL = self.original["database_url"]
        server.DB_PATH = self.original["db_path"]
        self.client = None
        gc.collect()
        self.temp_dir.cleanup()

    @staticmethod
    def insert_user(conn, user_id: str, name: str, role: str) -> None:
        conn.execute(
            """
            INSERT INTO users (
                id, store_id, name, login, password_hash, role, active, updated_at
            )
            VALUES (?, 'matriz', ?, ?, 'not-used', ?, 1, ?)
            """,
            (user_id, name, user_id, role, "2026-07-23T10:00:00+00:00"),
        )

    def authenticate(self, role: str = "admin") -> None:
        user_id = "admin" if role == "admin" else "operator"
        name = "Administrador" if role == "admin" else "Operador"
        with self.client.session_transaction() as flask_session:
            flask_session["user"] = {
                "id": user_id,
                "name": name,
                "login": user_id,
                "role": role,
                "active": True,
            }

    @staticmethod
    def payload(**changes) -> dict:
        values = {
            "name": "Maria da Silva",
            "cpf": "529.982.247-25",
            "phone": "(48) 99999-1111",
            "birth": "1990-05-12",
            "email": "MARIA@EXAMPLE.COM",
            "address": "Rua Principal",
            "addressNumber": "100",
            "district": "Centro",
            "city": "Florianopolis",
            "state": "sc",
            "zip": "88000-000",
            "notes": "Prefere contato por mensagem.",
            "limit": 500,
        }
        values.update(changes)
        return values

    def create_customer(self, **changes) -> dict:
        self.authenticate("operator")
        response = self.client.post("/api/customers", json=self.payload(**changes))
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()["data"]

    def raw_state(self) -> dict:
        with sqlite3.connect(server.DB_PATH) as connection:
            row = connection.execute("SELECT data FROM app_state WHERE id = 1").fetchone()
        return json.loads(row[0])

    def test_customer_api_requires_authenticated_backend_session(self):
        response = self.client.post("/api/customers", json=self.payload())
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {
            "ok": False,
            "error": "Login obrigatório.",
        })

    def test_required_fields_and_formats_are_validated_by_backend(self):
        self.authenticate("operator")
        invalid_cases = (
            ({"name": "   "}, "Nome completo"),
            ({"phone": "   "}, "Telefone"),
            ({"limit": 0}, "Limite"),
            ({"limit": -1}, "Limite"),
            ({"limit": "NaN"}, "Limite"),
            ({"cpf": "111.111.111-11"}, "CPF"),
            ({"email": "email-invalido"}, "E-mail"),
            ({"birth": "2026-02-30"}, "Data de nascimento"),
            ({"state": "Santa Catarina"}, "Estado"),
        )
        for changes, expected in invalid_cases:
            with self.subTest(changes=changes):
                response = self.client.post("/api/customers", json=self.payload(**changes))
                self.assertEqual(response.status_code, 400)
                self.assertIn(expected, response.get_json()["error"])
        with sqlite3.connect(server.DB_PATH) as connection:
            self.assertEqual(
                connection.execute(
                    "SELECT COUNT(*) FROM customers WHERE is_default = 0"
                ).fetchone()[0],
                0,
            )

    def test_valid_customer_is_normalized_persisted_audited_and_mirrored(self):
        self.authenticate("operator")
        with (
            mock.patch.object(
                server,
                "write_state",
                side_effect=AssertionError("write_state chamado"),
            ) as write_state,
            mock.patch.object(
                server,
                "sync_business_tables",
                side_effect=AssertionError("sync_business_tables chamado"),
            ) as sync_business_tables,
        ):
            response = self.client.post("/api/customers", json=self.payload())

        self.assertEqual(response.status_code, 201, response.get_json())
        customer = response.get_json()["data"]
        self.assertEqual(customer["cpf"], "52998224725")
        self.assertEqual(customer["email"], "maria@example.com")
        self.assertEqual(customer["state"], "SC")
        self.assertEqual(customer["code"], "CLI00001")
        self.assertEqual(customer["status"], "active")
        self.assertFalse(customer["isDefault"])
        write_state.assert_not_called()
        sync_business_tables.assert_not_called()

        with sqlite3.connect(server.DB_PATH) as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute(
                """
                SELECT cpf, whatsapp, address_number, state, notes, credit_limit
                FROM customers
                WHERE id = ?
                """,
                (customer["id"],),
            ).fetchone()
            audit = connection.execute(
                """
                SELECT user_id, user_role, action, module
                FROM audit_logs
                WHERE ref_id = ?
                """,
                (customer["id"],),
            ).fetchone()
        self.assertEqual(row["cpf"], "52998224725")
        self.assertEqual(row["address_number"], "100")
        self.assertEqual(row["state"], "SC")
        self.assertEqual(row["notes"], "Prefere contato por mensagem.")
        self.assertEqual(row["credit_limit"], 500)
        self.assertEqual(tuple(audit), ("operator", "operator", "create", "customer"))
        mirrored = next(
            item
            for item in self.raw_state()["customers"]
            if item.get("id") == customer["id"]
        )
        self.assertEqual(mirrored["cpf"], "52998224725")
        self.assertEqual(mirrored["notes"], "Prefere contato por mensagem.")

    def test_cpf_is_optional_but_unique_even_for_deactivated_customer(self):
        first = self.create_customer()
        self.client.post(
            f"/api/customers/{first['id']}/status",
            json={"status": "deactivated", "reason": "Cadastro encerrado"},
        )
        response = self.client.post(
            "/api/customers",
            json=self.payload(name="Outra Pessoa", phone="48999992222"),
        )
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.get_json()["code"], "CPF_DUPLICATE")

        without_cpf = self.client.post(
            "/api/customers",
            json=self.payload(
                name="Cliente sem CPF",
                cpf="",
                phone="48999993333",
            ),
        )
        self.assertEqual(without_cpf.status_code, 201, without_cpf.get_json())

    def test_duplicate_name_and_phone_require_non_blocking_acknowledgement(self):
        first = self.create_customer()
        response = self.client.post(
            "/api/customers",
            json=self.payload(
                cpf="",
                name="  Maria   da Silva ",
                phone="(48) 99999-1111",
            ),
        )
        self.assertEqual(response.status_code, 409)
        payload = response.get_json()
        self.assertEqual(payload["code"], "POSSIBLE_DUPLICATE")
        self.assertEqual(payload["warnings"][0]["customerId"], first["id"])
        self.assertEqual(set(payload["warnings"][0]["fields"]), {"nome", "telefone"})

        confirmed_payload = self.payload(
            cpf="",
            name="Maria da Silva",
            phone="48999991111",
            duplicateAcknowledged=True,
        )
        confirmed = self.client.post("/api/customers", json=confirmed_payload)
        self.assertEqual(confirmed.status_code, 201, confirmed.get_json())

    def test_limit_change_preserves_history_and_operator_identity(self):
        customer = self.create_customer()
        self.authenticate("operator")
        response = self.client.put(
            f"/api/customers/{customer['id']}",
            json=self.payload(limit=1250, duplicateAcknowledged=True),
        )
        self.assertEqual(response.status_code, 200, response.get_json())
        with sqlite3.connect(server.DB_PATH) as connection:
            connection.row_factory = sqlite3.Row
            history = connection.execute(
                """
                SELECT previous_limit, new_limit, user_id, user_name
                FROM customer_credit_limit_history
                WHERE customer_id = ?
                """,
                (customer["id"],),
            ).fetchone()
        self.assertEqual(history["previous_limit"], 500)
        self.assertEqual(history["new_limit"], 1250)
        self.assertEqual(history["user_id"], "operator")
        self.assertEqual(history["user_name"], "Operador")

    def test_status_transitions_require_reason_and_preserve_history(self):
        customer = self.create_customer()
        missing_reason = self.client.post(
            f"/api/customers/{customer['id']}/status",
            json={"status": "blocked", "reason": "  "},
        )
        self.assertEqual(missing_reason.status_code, 400)

        for status, reason in (
            ("blocked", "Acordo comercial"),
            ("active", "Regularizado"),
            ("deactivated", "Cadastro sem uso"),
            ("active", "Cliente retornou"),
        ):
            response = self.client.post(
                f"/api/customers/{customer['id']}/status",
                json={"status": status, "reason": reason},
            )
            self.assertEqual(response.status_code, 200, response.get_json())

        same_status = self.client.post(
            f"/api/customers/{customer['id']}/status",
            json={"status": "active", "reason": ""},
        )
        self.assertEqual(same_status.status_code, 200)
        self.assertFalse(same_status.get_json()["changed"])
        with sqlite3.connect(server.DB_PATH) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                """
                SELECT previous_status, new_status, reason, user_id
                FROM customer_status_history
                WHERE customer_id = ?
                ORDER BY created_at
                """,
                (customer["id"],),
            ).fetchall()
        self.assertEqual(len(rows), 4)
        self.assertEqual(tuple(rows[0]), ("active", "blocked", "Acordo comercial", "operator"))
        self.assertEqual(tuple(rows[-1]), ("deactivated", "active", "Cliente retornou", "operator"))

    def test_default_customer_is_protected_and_physical_delete_is_rejected(self):
        self.authenticate("admin")
        default_id = self.default_customer["id"]
        edit = self.client.put(
            f"/api/customers/{default_id}",
            json=self.payload(),
        )
        status = self.client.post(
            f"/api/customers/{default_id}/status",
            json={"status": "deactivated", "reason": "Nao permitido"},
        )
        deletion = self.client.delete(f"/api/customers/{default_id}")
        self.assertEqual(edit.status_code, 409)
        self.assertEqual(status.status_code, 409)
        self.assertEqual(deletion.status_code, 409)
        self.assertEqual(deletion.get_json()["code"], "CUSTOMER_DELETION_NOT_ALLOWED")
        with sqlite3.connect(server.DB_PATH) as connection:
            self.assertEqual(
                connection.execute(
                    "SELECT COUNT(*) FROM customers WHERE id = ? AND is_default = 1",
                    (default_id,),
                ).fetchone()[0],
                1,
            )

    def test_detail_consolidates_financial_purchase_conditional_and_histories(self):
        customer = self.create_customer()
        self.authenticate("admin")
        timestamp = "2026-07-20T15:00:00+00:00"
        state = self.raw_state()
        state["conditionals"] = [{
            "id": "COND001",
            "customerId": customer["id"],
            "customerName": customer["name"],
            "items": [],
            "status": "open",
            "createdAt": timestamp,
            "updatedAt": timestamp,
        }]
        with server.connect_db() as conn:
            conn.execute(
                """
                INSERT INTO sales (
                    id, store_id, customer_id, customer_name, subtotal, discount,
                    total, cost_total, status, created_at, updated_at
                ) VALUES (?, 'matriz', ?, ?, 300, 0, 300, 100, 'completed', ?, ?)
                """,
                ("VENDA001", customer["id"], customer["name"], timestamp, timestamp),
            )
            conn.execute(
                """
                INSERT INTO sale_payments (
                    id, sale_id, method, amount, installments, status, created_at
                ) VALUES ('payment-1', 'VENDA001', 'storeCredit', 300, 3, 'registered', ?)
                """,
                (timestamp,),
            )
            conn.execute(
                """
                INSERT INTO receivables (
                    id, store_id, sale_id, customer_id, customer_name, method,
                    amount, received, status, due_date, paid_at, last_payment_at,
                    installment, created_at, updated_at
                ) VALUES (
                    'receivable-1', 'matriz', 'VENDA001', ?, ?, 'storeCredit',
                    300, 50, 'partial', '2026-07-01', '', ?, '1/3', ?, ?
                )
                """,
                (customer["id"], customer["name"], timestamp, timestamp, timestamp),
            )
            conn.execute(
                """
                INSERT INTO receivable_payments (
                    id, store_id, receivable_id, sale_id, customer_id, method,
                    amount, created_at, note
                ) VALUES (
                    'receipt-1', 'matriz', 'receivable-1', 'VENDA001', ?,
                    'pix', 50, ?, 'Pagamento parcial'
                )
                """,
                (customer["id"], timestamp),
            )
            conn.execute(
                "UPDATE app_state SET data = ?, updated_at = ? WHERE id = 1",
                (json.dumps(state, ensure_ascii=False), timestamp),
            )
        self.client.put(
            f"/api/customers/{customer['id']}",
            json=self.payload(limit=1000, duplicateAcknowledged=True),
        )
        self.client.post(
            f"/api/customers/{customer['id']}/status",
            json={"status": "blocked", "reason": "Parcela em atraso"},
        )

        response = self.client.get(f"/api/customers/{customer['id']}")

        self.assertEqual(response.status_code, 200, response.get_json())
        data = response.get_json()["data"]
        self.assertEqual(data["summary"]["totalPurchased"], 300)
        self.assertEqual(data["summary"]["openCredit"], 250)
        self.assertEqual(data["summary"]["overdueCredit"], 250)
        self.assertEqual(data["summary"]["availableCredit"], 750)
        self.assertEqual(data["sales"][0]["payments"][0]["method"], "storeCredit")
        self.assertEqual(data["receivables"][0]["payments"][0]["amount"], 50)
        self.assertEqual(data["conditionals"][0]["id"], "COND001")
        self.assertEqual(data["statusHistory"][0]["reason"], "Parcela em atraso")
        self.assertEqual(data["creditLimitHistory"][0]["newLimit"], 1000)

    def test_customer_creation_rolls_back_when_audit_fails(self):
        self.authenticate("admin")
        with (
            server.app.test_request_context("/api/customers", method="POST"),
            mock.patch.object(server, "record_audit", side_effect=RuntimeError("audit failure")),
        ):
            server.session["user"] = {
                "id": "admin",
                "name": "Administrador",
                "login": "admin",
                "role": "admin",
                "active": True,
            }
            with self.assertRaisesRegex(RuntimeError, "audit failure"):
                server.persist_customer_creation(self.payload())
        with sqlite3.connect(server.DB_PATH) as connection:
            self.assertEqual(
                connection.execute(
                    "SELECT COUNT(*) FROM customers WHERE is_default = 0"
                ).fetchone()[0],
                0,
            )
            self.assertEqual(
                connection.execute(
                    "SELECT COUNT(*) FROM audit_logs WHERE module = 'customer'"
                ).fetchone()[0],
                0,
            )
        self.assertEqual(
            [
                item
                for item in self.raw_state()["customers"]
                if not item.get("isDefault")
            ],
            [],
        )

    def seed_product(self) -> dict:
        product = {
            "id": "product-1",
            "barcode": "789000000001",
            "name": "Legging Teste",
            "size": "M",
            "color": "Preta",
            "gender": "Feminino",
            "category": "Legging",
            "brand": "Mova",
            "stock": 5,
            "minStock": 1,
            "description": "",
            "active": True,
            "cost": 40,
            "price": 100,
            "photo": "",
            "updatedAt": "2026-07-23T10:00:00+00:00",
        }
        state = self.raw_state()
        state["products"] = [product]
        with server.connect_db() as conn:
            conn.execute(
                """
                INSERT INTO products (
                    id, store_id, barcode, name, size, color, gender,
                    category_name, brand_name, stock, min_stock, description,
                    active, cost, price, photo, updated_at
                ) VALUES (
                    ?, 'matriz', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, '', ?
                )
                """,
                (
                    product["id"],
                    product["barcode"],
                    product["name"],
                    product["size"],
                    product["color"],
                    product["gender"],
                    product["category"],
                    product["brand"],
                    product["stock"],
                    product["minStock"],
                    product["description"],
                    product["cost"],
                    product["price"],
                    product["updatedAt"],
                ),
            )
            conn.execute(
                "UPDATE app_state SET data = ?, updated_at = ? WHERE id = 1",
                (json.dumps(state, ensure_ascii=False), product["updatedAt"]),
            )
        return product

    @staticmethod
    def sale_payload(product: dict, customer_id: str = "", method: str = "cash") -> dict:
        return {
            "customerId": customer_id,
            "items": [{
                "productId": product["id"],
                "quantity": 1,
                "unitPrice": 100,
                "unitCost": 40,
            }],
            "discount": 0,
            "payments": [{"method": method, "amount": 100}],
            "storeCreditInstallments": 1,
        }

    def test_sale_uses_default_customer_and_blocked_customer_only_loses_credit(self):
        self.authenticate("operator")
        product = self.seed_product()
        anonymous = self.client.post(
            "/api/sales",
            headers={"Idempotency-Key": "customer-default-sale"},
            json=self.sale_payload(product),
        )
        self.assertEqual(anonymous.status_code, 201, anonymous.get_json())
        sale = anonymous.get_json()["data"]["sale"]
        self.assertEqual(sale["customerId"], self.default_customer["id"])
        self.assertEqual(sale["customerName"], self.default_customer["name"])

        customer = self.create_customer(
            name="Cliente Bloqueado",
            cpf="",
            phone="48988887777",
        )
        self.client.post(
            f"/api/customers/{customer['id']}/status",
            json={"status": "blocked", "reason": "Analise comercial"},
        )
        blocked_credit = self.client.post(
            "/api/sales",
            headers={"Idempotency-Key": "customer-blocked-credit"},
            json=self.sale_payload(product, customer["id"], "storeCredit"),
        )
        self.assertEqual(blocked_credit.status_code, 409)
        self.assertIn("bloqueado", blocked_credit.get_json()["error"].lower())

        blocked_cash = self.client.post(
            "/api/sales",
            headers={"Idempotency-Key": "customer-blocked-cash"},
            json=self.sale_payload(product, customer["id"], "cash"),
        )
        self.assertEqual(blocked_cash.status_code, 201, blocked_cash.get_json())

    def test_deactivated_and_default_customers_cannot_receive_conditional(self):
        self.authenticate("operator")
        product = self.seed_product()
        customer = self.create_customer(
            name="Cliente Condicional",
            cpf="",
            phone="48977776666",
        )
        conditional_payload = {
            "customerId": customer["id"],
            "items": [{"productId": product["id"], "quantity": 1}],
        }
        created = self.client.post("/api/conditionals", json=conditional_payload)
        self.assertEqual(created.status_code, 201, created.get_json())

        self.client.post(
            f"/api/customers/{customer['id']}/status",
            json={"status": "deactivated", "reason": "Encerrado"},
        )
        deactivated = self.client.post("/api/conditionals", json=conditional_payload)
        default = self.client.post(
            "/api/conditionals",
            json={**conditional_payload, "customerId": self.default_customer["id"]},
        )
        self.assertEqual(deactivated.status_code, 409)
        self.assertEqual(default.status_code, 409)

    def test_reset_preserves_exactly_one_default_customer(self):
        self.create_customer()
        with server.app.test_request_context("/api/reset", method="POST"):
            server.session["user"] = {
                "id": "admin",
                "name": "Administrador",
                "login": "admin",
                "role": "admin",
                "active": True,
            }
            server.reset_business_data()
        with sqlite3.connect(server.DB_PATH) as connection:
            self.assertEqual(
                connection.execute(
                    "SELECT COUNT(*) FROM customers WHERE is_default = 1"
                ).fetchone()[0],
                1,
            )
            self.assertEqual(
                connection.execute(
                    "SELECT COUNT(*) FROM customers WHERE is_default = 0"
                ).fetchone()[0],
                0,
            )
        customers = self.raw_state()["customers"]
        self.assertEqual(len(customers), 1)
        self.assertTrue(customers[0]["isDefault"])


class CustomerFrontendContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1]
        cls.html = (root / "index.html").read_text(encoding="utf-8")
        cls.javascript = (root / "script.js").read_text(encoding="utf-8")

    def test_customer_screen_has_search_kpis_status_and_detail(self):
        expected_ids = (
            "newCustomerButton",
            "customerListSearch",
            "customerStatusFilter",
            "customerTotalKpi",
            "customerOpenKpi",
            "customerOverdueKpi",
            "customerReceivableKpi",
            "customerDetailModal",
            "customerStatusModal",
        )
        for element_id in expected_ids:
            with self.subTest(element_id=element_id):
                self.assertIn(f'id="{element_id}"', self.html)

    def test_customer_form_contains_official_fields(self):
        for element_id in (
            "customerName",
            "customerWhatsapp",
            "customerLimit",
            "customerCpf",
            "customerBirth",
            "customerEmail",
            "customerAddress",
            "customerAddressNumber",
            "customerDistrict",
            "customerCity",
            "customerState",
            "customerZip",
            "customerNotes",
        ):
            with self.subTest(element_id=element_id):
                self.assertIn(f'id="{element_id}"', self.html)

    def test_customer_interface_has_no_physical_delete_action(self):
        self.assertNotIn('fetch(`/api/customers/${customerId}`, { method: "DELETE"', self.javascript)
        self.assertNotIn("deleteCustomerButton", self.html)


if __name__ == "__main__":
    unittest.main()
