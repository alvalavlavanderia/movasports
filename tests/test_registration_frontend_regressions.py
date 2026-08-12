import unittest
from pathlib import Path

import server


class RegistrationFrontendRegressionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1]
        cls.html = (root / "index.html").read_text(encoding="utf-8")
        cls.script = (root / "script.js").read_text(encoding="utf-8")
        cls.styles = (root / "style.css").read_text(encoding="utf-8")

    def function_source(self, name, next_name):
        start = self.script.index(f"function {name}")
        end = self.script.index(f"function {next_name}", start)
        return self.script[start:end]

    def async_function_source(self, name, next_name):
        start = self.script.index(f"async function {name}")
        end = self.script.index(f"async function {next_name}", start)
        return self.script[start:end]

    def test_login_only_shows_validation_after_submit(self):
        self.assertIn('id="loginForm" class="login-panel" autocomplete="off" novalidate', self.html)
        login_source = self.async_function_source("login", "logout")
        self.assertIn('if (!loginName || !password)', login_source)
        self.assertIn('Informe o usu\u00e1rio e a senha.', login_source)

        unauthorized_source = self.function_source("handleUnauthorized", "isAdmin")
        self.assertIn("initialSessionSyncComplete", unauthorized_source)
        self.assertIn("hadAuthenticatedSession", unauthorized_source)
        self.assertNotIn("alert(", unauthorized_source)

    def test_product_draft_is_preserved_during_automatic_lookup(self):
        confirm_source = self.async_function_source("confirmProductEntry", "resolveProductPhoto")
        self.assertIn("lookupProductByCode({ preserveDraft: true })", confirm_source)

        lookup_source = self.async_function_source("lookupProductByCode", "confirmProductEntry")
        self.assertIn("if (preserveDraft)", lookup_source)
        self.assertIn("resetProductForm(barcode)", lookup_source)

        payload_source = self.async_function_source("productPayloadFromForm", "responsePayload")
        self.assertLess(payload_source.index("const draft ="), payload_source.index("await resolveProductPhoto"))
        self.assertIn("description: els.productDescription.value.trim()", payload_source)

    def test_all_registration_lists_use_ten_item_numeric_pagination(self):
        self.assertIn("const REGISTRATION_PAGE_SIZE = 10;", self.script)
        for element_id in (
            "productPagination",
            "customerPagination",
            "supplierPagination",
            "cardModalityPagination",
            "brandPagination",
            "categoryPagination",
            "userPagination",
        ):
            with self.subTest(element_id=element_id):
                self.assertIn(f'id="{element_id}"', self.html)
        self.assertIn('id="${config.prefix}Pagination"', self.script)
        for key in (
            "products",
            "customers",
            "suppliers",
            "brands",
            "categories",
            "sizes",
            "colors",
            "expenseCategories",
            "cardModalities",
            "users",
        ):
            with self.subTest(key=key):
                self.assertIn(f'"{key}"', self.script)
        self.assertIn("registrationPaginationWindow", self.script)
        self.assertIn('button(String(page)', self.script)

    def test_registration_order_prioritizes_creation_timestamp(self):
        order_source = self.function_source("newestRegistrationsFirst", "registrationPaginationWindow")
        self.assertIn('left.item.createdAt || left.item.updatedAt', order_source)
        self.assertIn('right.item.createdAt || right.item.updatedAt', order_source)
        self.assertIn("return rightTime - leftTime", order_source)

    def test_product_lookup_button_has_a_bounded_grid_column(self):
        self.assertIn(".field-with-action.product-code-action", self.styles)
        self.assertIn("grid-template-columns: minmax(0, 1fr) 92px;", self.styles)
        self.assertIn(".product-code-action .ghost", self.styles)
        self.assertIn("width: 92px;", self.styles)

    def test_user_ordering_timestamp_is_public_but_credentials_are_not(self):
        user = server.registration_user({
            "id": "operator",
            "name": "Operador",
            "login": "operator",
            "role": "operator",
            "active": 1,
            "blocked_at": None,
            "updated_at": "2026-08-12T12:00:00+00:00",
            "password_hash": "must-not-leak",
        })
        self.assertEqual(user["createdAt"], "2026-08-12T12:00:00+00:00")
        self.assertEqual(user["updatedAt"], "2026-08-12T12:00:00+00:00")
        self.assertNotIn("password", user)
        self.assertNotIn("password_hash", user)


if __name__ == "__main__":
    unittest.main()
