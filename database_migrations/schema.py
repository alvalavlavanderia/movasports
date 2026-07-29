from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ColumnSpec:
    name: str
    sql_type: str
    not_null: bool = False
    default: str | None = None
    primary_key: bool = False

    def ddl(self) -> str:
        parts = [self.name, self.sql_type]
        if self.primary_key:
            parts.append("PRIMARY KEY")
        if self.not_null:
            parts.append("NOT NULL")
        if self.default is not None:
            parts.extend(("DEFAULT", self.default))
        return " ".join(parts)


@dataclass(frozen=True)
class ForeignKeySpec:
    column: str
    target_table: str
    target_column: str = "id"
    on_delete: str = "NO ACTION"

    def ddl(self) -> str:
        clause = f"FOREIGN KEY ({self.column}) REFERENCES {self.target_table}({self.target_column})"
        if self.on_delete != "NO ACTION":
            clause += f" ON DELETE {self.on_delete}"
        return clause


@dataclass(frozen=True)
class TableSpec:
    name: str
    columns: tuple[ColumnSpec, ...]
    foreign_keys: tuple[ForeignKeySpec, ...] = ()
    checks: tuple[str, ...] = ()

    def ddl(self) -> str:
        definitions = [column.ddl() for column in self.columns]
        definitions.extend(foreign_key.ddl() for foreign_key in self.foreign_keys)
        definitions.extend(f"CHECK ({check})" for check in self.checks)
        body = ",\n    ".join(definitions)
        return f"CREATE TABLE {self.name} (\n    {body}\n)"


@dataclass(frozen=True)
class IndexSpec:
    name: str
    table: str
    columns: tuple[str, ...]
    unique: bool = False
    predicate: str = ""

    def ddl(self) -> str:
        uniqueness = "UNIQUE " if self.unique else ""
        sql = f"CREATE {uniqueness}INDEX {self.name} ON {self.table}({', '.join(self.columns)})"
        if self.predicate:
            sql += f" WHERE {self.predicate}"
        return sql


def col(
    name: str,
    sql_type: str = "TEXT",
    *,
    not_null: bool = False,
    default: str | None = None,
    primary_key: bool = False,
) -> ColumnSpec:
    return ColumnSpec(name, sql_type, not_null, default, primary_key)


STORE_FK = ForeignKeySpec("store_id", "stores")

CURRENT_TABLES = (
    TableSpec("stores", (
        col("id", primary_key=True), col("name", not_null=True), col("created_at", not_null=True),
    )),
    TableSpec("app_state", (
        col("id", "INTEGER", primary_key=True), col("data", not_null=True), col("updated_at", not_null=True),
    ), checks=("id = 1",)),
    TableSpec("users", (
        col("id", primary_key=True), col("store_id", not_null=True), col("name", not_null=True),
        col("login", not_null=True), col("password_hash", not_null=True),
        col("role", not_null=True, default="'operator'"), col("active", "INTEGER", not_null=True, default="1"),
        col("updated_at", not_null=True),
    ), (STORE_FK,)),
    TableSpec("audit_logs", (
        col("id", primary_key=True), col("store_id", not_null=True), col("user_id"), col("user_name"),
        col("user_role"), col("action", not_null=True), col("module", not_null=True), col("ref_id"),
        col("details"), col("created_at", not_null=True),
    ), (STORE_FK,)),
    TableSpec("brands", (
        col("id", primary_key=True), col("store_id", not_null=True), col("name", not_null=True),
        col("updated_at", not_null=True),
    ), (STORE_FK,)),
    TableSpec("categories", (
        col("id", primary_key=True), col("store_id", not_null=True), col("name", not_null=True),
        col("updated_at", not_null=True),
    ), (STORE_FK,)),
    TableSpec("suppliers", (
        col("id", primary_key=True), col("store_id", not_null=True), col("name", not_null=True),
        col("cnpj"), col("phone"), col("email"), col("address"), col("updated_at", not_null=True),
    ), (STORE_FK,)),
    TableSpec("customers", (
        col("id", primary_key=True), col("store_id", not_null=True), col("code"), col("name", not_null=True),
        col("cpf"), col("rg"), col("birth"), col("whatsapp"), col("email"), col("address"),
        col("city"), col("district"), col("zip"),
        col("credit_limit", "REAL", not_null=True, default="0"),
        col("status", not_null=True, default="'active'"), col("updated_at", not_null=True),
    ), (STORE_FK,)),
    TableSpec("products", (
        col("id", primary_key=True), col("store_id", not_null=True), col("barcode"), col("name", not_null=True),
        col("size"), col("color"), col("gender"), col("category_name"), col("brand_name"),
        col("stock", "INTEGER", not_null=True, default="0"),
        col("min_stock", "INTEGER", not_null=True, default="0"), col("description"),
        col("active", "INTEGER", not_null=True, default="1"),
        col("cost", "REAL", not_null=True, default="0"), col("price", "REAL", not_null=True, default="0"),
        col("photo"), col("updated_at", not_null=True),
    ), (STORE_FK,)),
    TableSpec("sales", (
        col("id", primary_key=True), col("store_id", not_null=True), col("customer_id"),
        col("customer_name", not_null=True), col("subtotal", "REAL", not_null=True, default="0"),
        col("discount", "REAL", not_null=True, default="0"), col("total", "REAL", not_null=True, default="0"),
        col("cost_total", "REAL", not_null=True, default="0"),
        col("status", not_null=True, default="'completed'"), col("created_at", not_null=True),
        col("updated_at", not_null=True),
    ), (STORE_FK,)),
    TableSpec("sale_items", (
        col("id", primary_key=True), col("sale_id", not_null=True), col("product_id"), col("barcode"),
        col("name", not_null=True), col("brand"), col("quantity", "INTEGER", not_null=True, default="1"),
        col("unit_cost", "REAL", not_null=True, default="0"),
        col("unit_price", "REAL", not_null=True, default="0"), col("total", "REAL", not_null=True, default="0"),
    ), (ForeignKeySpec("sale_id", "sales", on_delete="CASCADE"),)),
    TableSpec("sale_payments", (
        col("id", primary_key=True), col("sale_id", not_null=True), col("method", not_null=True),
        col("amount", "REAL", not_null=True, default="0"),
        col("installments", "INTEGER", not_null=True, default="1"),
        col("status", not_null=True, default="'registered'"), col("created_at", not_null=True),
    ), (ForeignKeySpec("sale_id", "sales", on_delete="CASCADE"),)),
    TableSpec("cash_movements", (
        col("id", primary_key=True), col("store_id", not_null=True), col("direction", not_null=True),
        col("type"), col("description"), col("method"), col("amount", "REAL", not_null=True, default="0"),
        col("ref_id"), col("created_at", not_null=True),
    ), (STORE_FK,)),
    TableSpec("cash_closings", (
        col("id", primary_key=True), col("store_id", not_null=True), col("date", not_null=True),
        col("expected_cash", "REAL", not_null=True, default="0"),
        col("informed_cash", "REAL", not_null=True, default="0"),
        col("difference", "REAL", not_null=True, default="0"),
        col("total_balance", "REAL", not_null=True, default="0"),
        col("cash_in", "REAL", not_null=True, default="0"),
        col("cash_out", "REAL", not_null=True, default="0"),
        col("notes"), col("user_id"), col("user_name"), col("created_at", not_null=True),
    ), (STORE_FK,)),
    TableSpec("receivables", (
        col("id", primary_key=True), col("store_id", not_null=True), col("sale_id"), col("customer_id"),
        col("customer_name"), col("method", not_null=True), col("amount", "REAL", not_null=True, default="0"),
        col("received", "REAL", not_null=True, default="0"),
        col("status", not_null=True, default="'open'"), col("due_date"), col("paid_at"),
        col("last_payment_at"), col("installment"), col("created_at", not_null=True),
        col("updated_at", not_null=True),
    ), (STORE_FK,)),
    TableSpec("receivable_payments", (
        col("id", primary_key=True), col("store_id", not_null=True), col("receivable_id", not_null=True),
        col("sale_id"), col("customer_id"), col("method", not_null=True),
        col("amount", "REAL", not_null=True, default="0"), col("created_at", not_null=True), col("note"),
    ), (STORE_FK, ForeignKeySpec("receivable_id", "receivables", on_delete="CASCADE"))),
    TableSpec("sale_returns", (
        col("id", primary_key=True), col("store_id", not_null=True), col("sale_id", not_null=True),
        col("customer_name"), col("total", "REAL", not_null=True, default="0"), col("reason"), col("notes"),
        col("created_at", not_null=True),
    ), (STORE_FK,)),
    TableSpec("sale_return_items", (
        col("id", primary_key=True), col("return_id", not_null=True), col("product_id"), col("product_name"),
        col("action", not_null=True), col("quantity", "INTEGER", not_null=True, default="1"),
        col("unit_price", "REAL", not_null=True, default="0"), col("total", "REAL", not_null=True, default="0"),
    ), (ForeignKeySpec("return_id", "sale_returns", on_delete="CASCADE"),)),
    TableSpec("payables", (
        col("id", primary_key=True), col("store_id", not_null=True), col("supplier"), col("category", not_null=True),
        col("amount", "REAL", not_null=True, default="0"), col("issue_date"), col("due_date", not_null=True),
        col("notes"), col("paid_amount", "REAL", not_null=True, default="0"),
        col("fee", "REAL", not_null=True, default="0"),
        col("discount", "REAL", not_null=True, default="0"),
        col("status", not_null=True, default="'pending'"), col("paid_at"),
        col("created_at", not_null=True), col("updated_at", not_null=True),
    ), (STORE_FK,)),
)


CURRENT_INDEXES = (
    IndexSpec("idx_users_store_login", "users", ("store_id", "login"), True),
    IndexSpec("idx_audit_store_created", "audit_logs", ("store_id", "created_at")),
    IndexSpec("idx_audit_module", "audit_logs", ("module",)),
    IndexSpec("idx_brands_store_name", "brands", ("store_id", "name"), True),
    IndexSpec("idx_categories_store_name", "categories", ("store_id", "name"), True),
    IndexSpec("idx_customers_store_name", "customers", ("store_id", "name")),
    IndexSpec("idx_customers_store_cpf", "customers", ("store_id", "cpf"), True, "cpf IS NOT NULL AND cpf <> ''"),
    IndexSpec("idx_products_store_barcode", "products", ("store_id", "barcode"), True, "barcode IS NOT NULL AND barcode <> ''"),
    IndexSpec("idx_sales_store_created", "sales", ("store_id", "created_at")),
    IndexSpec("idx_sales_customer", "sales", ("customer_id",)),
    IndexSpec("idx_sale_items_sale", "sale_items", ("sale_id",)),
    IndexSpec("idx_sale_items_product", "sale_items", ("product_id",)),
    IndexSpec("idx_sale_payments_sale", "sale_payments", ("sale_id",)),
    IndexSpec("idx_sale_payments_method", "sale_payments", ("method",)),
    IndexSpec("idx_cash_store_created", "cash_movements", ("store_id", "created_at")),
    IndexSpec("idx_cash_method", "cash_movements", ("method",)),
    IndexSpec("idx_cash_ref", "cash_movements", ("ref_id",)),
    IndexSpec("idx_cash_closings_store_date", "cash_closings", ("store_id", "date")),
    IndexSpec("idx_receivables_store_due", "receivables", ("store_id", "due_date")),
    IndexSpec("idx_receivables_status", "receivables", ("status",)),
    IndexSpec("idx_receivables_sale", "receivables", ("sale_id",)),
    IndexSpec("idx_receivables_customer", "receivables", ("customer_id",)),
    IndexSpec("idx_receivable_payments_receivable", "receivable_payments", ("receivable_id",)),
    IndexSpec("idx_receivable_payments_customer", "receivable_payments", ("store_id", "customer_id", "created_at")),
    IndexSpec("idx_returns_store_created", "sale_returns", ("store_id", "created_at")),
    IndexSpec("idx_returns_sale", "sale_returns", ("sale_id",)),
    IndexSpec("idx_return_items_return", "sale_return_items", ("return_id",)),
    IndexSpec("idx_payables_store_due", "payables", ("store_id", "due_date")),
    IndexSpec("idx_payables_status", "payables", ("status",)),
    IndexSpec("idx_payables_supplier", "payables", ("supplier",)),
)


V001_TABLES = CURRENT_TABLES
V001_INDEXES = CURRENT_INDEXES
V001_SCHEMA_STATEMENTS = tuple(table.ddl() for table in V001_TABLES) + tuple(
    index.ddl() for index in V001_INDEXES
)
# Historical compatibility name imported by migration v1. Keep it bound to
# the frozen v1 schema rather than the latest schema.
CURRENT_SCHEMA_STATEMENTS = V001_SCHEMA_STATEMENTS

_V002_CUSTOMER_COLUMNS = (
    col("address_number"),
    col("state"),
    col("notes"),
    col("is_default", "INTEGER", not_null=True, default="0"),
    col("created_at"),
)

CURRENT_TABLES = tuple(
    TableSpec(
        table.name,
        (*table.columns, *_V002_CUSTOMER_COLUMNS),
        table.foreign_keys,
        table.checks,
    )
    if table.name == "customers"
    else table
    for table in V001_TABLES
) + (
    TableSpec("customer_status_history", (
        col("id", primary_key=True), col("store_id", not_null=True),
        col("customer_id", not_null=True), col("previous_status", not_null=True),
        col("new_status", not_null=True), col("reason"), col("user_id"),
        col("user_name"), col("created_at", not_null=True),
    ), (STORE_FK, ForeignKeySpec("customer_id", "customers"))),
    TableSpec("customer_credit_limit_history", (
        col("id", primary_key=True), col("store_id", not_null=True),
        col("customer_id", not_null=True), col("previous_limit", "REAL", not_null=True),
        col("new_limit", "REAL", not_null=True), col("user_id"),
        col("user_name"), col("created_at", not_null=True),
    ), (STORE_FK, ForeignKeySpec("customer_id", "customers"))),
)

CURRENT_INDEXES = (*V001_INDEXES,
    IndexSpec(
        "idx_customer_status_history_customer",
        "customer_status_history",
        ("store_id", "customer_id", "created_at"),
    ),
    IndexSpec(
        "idx_customer_limit_history_customer",
        "customer_credit_limit_history",
        ("store_id", "customer_id", "created_at"),
    ),
    IndexSpec(
        "idx_customers_store_default",
        "customers",
        ("store_id",),
        True,
        "is_default = 1",
    ),
)

V002_TABLES = CURRENT_TABLES
V002_INDEXES = CURRENT_INDEXES
V002_SCHEMA_STATEMENTS = tuple(table.ddl() for table in V002_TABLES) + tuple(
    index.ddl() for index in V002_INDEXES
)

_V003_NAMED_CATALOG_COLUMNS = (
    col("normalized_name"),
    col("status", not_null=True, default="'active'"),
    col("created_at"),
)

_V003_SUPPLIER_COLUMNS = (
    col("trade_name"),
    col("document_normalized"),
    col("whatsapp"),
    col("zip"),
    col("address_number"),
    col("district"),
    col("city"),
    col("state"),
    col("notes"),
    col("status", not_null=True, default="'active'"),
    col("created_at"),
)

_V003_PRODUCT_LINK_COLUMNS = (
    col("brand_id"),
    col("category_id"),
    col("size_id"),
    col("color_id"),
    col("supplier_id"),
)

_V003_PAYABLE_LINK_COLUMNS = (
    col("supplier_id"),
    col("expense_category_id"),
)

_V003_CASH_LINK_COLUMNS = (col("expense_category_id"),)

CURRENT_TABLES = tuple(
    TableSpec(
        table.name,
        (
            (*table.columns, *_V003_NAMED_CATALOG_COLUMNS)
            if table.name in {"brands", "categories"}
            else (*table.columns, *_V003_SUPPLIER_COLUMNS)
            if table.name == "suppliers"
            else (*table.columns, *_V003_PRODUCT_LINK_COLUMNS)
            if table.name == "products"
            else (*table.columns, *_V003_PAYABLE_LINK_COLUMNS)
            if table.name == "payables"
            else (*table.columns, *_V003_CASH_LINK_COLUMNS)
            if table.name == "cash_movements"
            else table.columns
        ),
        table.foreign_keys,
        table.checks,
    )
    for table in V002_TABLES
) + (
    TableSpec("sizes", (
        col("id", primary_key=True), col("store_id", not_null=True), col("name", not_null=True),
        col("normalized_name"), col("status", not_null=True, default="'active'"),
        col("created_at"), col("updated_at", not_null=True),
    ), (STORE_FK,)),
    TableSpec("colors", (
        col("id", primary_key=True), col("store_id", not_null=True), col("name", not_null=True),
        col("normalized_name"), col("status", not_null=True, default="'active'"),
        col("created_at"), col("updated_at", not_null=True),
    ), (STORE_FK,)),
    TableSpec("expense_categories", (
        col("id", primary_key=True), col("store_id", not_null=True), col("name", not_null=True),
        col("normalized_name"), col("status", not_null=True, default="'active'"),
        col("created_at"), col("updated_at", not_null=True),
    ), (STORE_FK,)),
    TableSpec("supplier_status_history", (
        col("id", primary_key=True), col("store_id", not_null=True),
        col("supplier_id", not_null=True), col("previous_status", not_null=True),
        col("new_status", not_null=True), col("reason"), col("user_id"),
        col("user_name"), col("created_at", not_null=True),
    ), (STORE_FK, ForeignKeySpec("supplier_id", "suppliers"))),
)

CURRENT_INDEXES = (*V002_INDEXES,
    IndexSpec(
        "idx_brands_store_normalized_name",
        "brands",
        ("store_id", "normalized_name"),
        True,
        "normalized_name IS NOT NULL AND normalized_name <> ''",
    ),
    IndexSpec(
        "idx_categories_store_normalized_name",
        "categories",
        ("store_id", "normalized_name"),
        True,
        "normalized_name IS NOT NULL AND normalized_name <> ''",
    ),
    IndexSpec(
        "idx_suppliers_store_document",
        "suppliers",
        ("store_id", "document_normalized"),
        True,
        "document_normalized IS NOT NULL AND document_normalized <> ''",
    ),
    IndexSpec("idx_suppliers_store_status", "suppliers", ("store_id", "status")),
    IndexSpec(
        "idx_sizes_store_normalized_name",
        "sizes",
        ("store_id", "normalized_name"),
        True,
        "normalized_name IS NOT NULL AND normalized_name <> ''",
    ),
    IndexSpec(
        "idx_colors_store_normalized_name",
        "colors",
        ("store_id", "normalized_name"),
        True,
        "normalized_name IS NOT NULL AND normalized_name <> ''",
    ),
    IndexSpec(
        "idx_expense_categories_store_normalized_name",
        "expense_categories",
        ("store_id", "normalized_name"),
        True,
        "normalized_name IS NOT NULL AND normalized_name <> ''",
    ),
    IndexSpec(
        "idx_supplier_status_history_supplier",
        "supplier_status_history",
        ("store_id", "supplier_id", "created_at"),
    ),
    IndexSpec("idx_products_brand_id", "products", ("store_id", "brand_id")),
    IndexSpec("idx_products_category_id", "products", ("store_id", "category_id")),
    IndexSpec("idx_products_size_id", "products", ("store_id", "size_id")),
    IndexSpec("idx_products_color_id", "products", ("store_id", "color_id")),
    IndexSpec("idx_products_supplier_id", "products", ("store_id", "supplier_id")),
    IndexSpec("idx_payables_supplier_id", "payables", ("store_id", "supplier_id")),
    IndexSpec(
        "idx_payables_expense_category_id",
        "payables",
        ("store_id", "expense_category_id"),
    ),
    IndexSpec(
        "idx_cash_expense_category_id",
        "cash_movements",
        ("store_id", "expense_category_id"),
    ),
)

V003_TABLES = CURRENT_TABLES
V003_INDEXES = CURRENT_INDEXES
V003_SCHEMA_STATEMENTS = tuple(table.ddl() for table in V003_TABLES) + tuple(
    index.ddl() for index in V003_INDEXES
)

_V004_PRODUCT_COLUMNS = (
    col("barcode_normalized"),
    col("created_at"),
    col("stock_entered_at"),
)

V004_TABLES = tuple(
    TableSpec(
        table.name,
        (*table.columns, *_V004_PRODUCT_COLUMNS),
        table.foreign_keys,
        table.checks,
    )
    if table.name == "products"
    else table
    for table in V003_TABLES
) + (
    TableSpec("stock_entry_sequences", (
        col("store_id", primary_key=True),
        col("next_number", "INTEGER", not_null=True, default="1"),
    ), (STORE_FK,), checks=("next_number > 0",)),
    TableSpec("stock_entries", (
        col("id", primary_key=True), col("store_id", not_null=True),
        col("entry_number", "INTEGER", not_null=True),
        col("supplier_id", not_null=True), col("supplier_name", not_null=True),
        col("status", not_null=True, default="'confirmed'"),
        col("total_quantity", "INTEGER", not_null=True),
        col("total_cost", "REAL", not_null=True),
        col("idempotency_key", not_null=True), col("request_hash", not_null=True),
        col("response_json", not_null=True),
        col("user_id"), col("user_name"),
        col("created_at", not_null=True), col("updated_at", not_null=True),
    ), (STORE_FK, ForeignKeySpec("supplier_id", "suppliers")), checks=(
        "entry_number > 0",
        "total_quantity > 0",
        "total_cost > 0",
        "status = 'confirmed'",
    )),
    TableSpec("stock_entry_items", (
        col("id", primary_key=True), col("entry_id", not_null=True),
        col("product_id", not_null=True), col("barcode", not_null=True),
        col("product_name", not_null=True), col("brand_id"), col("brand_name"),
        col("category_id"), col("category_name"), col("size_id"), col("size_name"),
        col("color_id"), col("color_name"), col("supplier_id", not_null=True),
        col("supplier_name", not_null=True), col("quantity", "INTEGER", not_null=True),
        col("unit_cost", "REAL", not_null=True), col("total_cost", "REAL", not_null=True),
        col("sale_price", "REAL", not_null=True),
        col("stock_before", "INTEGER", not_null=True),
        col("stock_after", "INTEGER", not_null=True),
    ), (
        ForeignKeySpec("entry_id", "stock_entries", on_delete="CASCADE"),
        ForeignKeySpec("product_id", "products"),
        ForeignKeySpec("supplier_id", "suppliers"),
    ), checks=(
        "quantity > 0",
        "unit_cost > 0",
        "total_cost > 0",
        "sale_price >= 0",
        "stock_before >= 0",
        "stock_after = stock_before + quantity",
    )),
    TableSpec("stock_movements", (
        col("id", primary_key=True), col("store_id", not_null=True),
        col("product_id", not_null=True), col("movement_type", not_null=True),
        col("direction", not_null=True), col("quantity", "INTEGER", not_null=True),
        col("balance_before", "INTEGER", not_null=True),
        col("balance_after", "INTEGER", not_null=True),
        col("reference_type", not_null=True), col("reference_id", not_null=True),
        col("user_id"), col("user_name"), col("created_at", not_null=True),
    ), (STORE_FK, ForeignKeySpec("product_id", "products")), checks=(
        "movement_type = 'entry'",
        "direction = 'in'",
        "quantity > 0",
        "balance_before >= 0",
        "balance_after = balance_before + quantity",
    )),
)

V004_INDEXES = (*V003_INDEXES,
    IndexSpec(
        "idx_products_store_barcode_normalized",
        "products",
        ("store_id", "barcode_normalized"),
        True,
        "barcode_normalized IS NOT NULL AND barcode_normalized <> ''",
    ),
    IndexSpec(
        "idx_stock_entries_store_number",
        "stock_entries",
        ("store_id", "entry_number"),
        True,
    ),
    IndexSpec(
        "idx_stock_entries_store_idempotency",
        "stock_entries",
        ("store_id", "idempotency_key"),
        True,
    ),
    IndexSpec(
        "idx_stock_entries_store_created",
        "stock_entries",
        ("store_id", "created_at"),
    ),
    IndexSpec(
        "idx_stock_entries_supplier",
        "stock_entries",
        ("store_id", "supplier_id", "created_at"),
    ),
    IndexSpec("idx_stock_entry_items_entry", "stock_entry_items", ("entry_id",)),
    IndexSpec(
        "idx_stock_entry_items_product",
        "stock_entry_items",
        ("product_id", "entry_id"),
    ),
    IndexSpec(
        "idx_stock_movements_product_created",
        "stock_movements",
        ("store_id", "product_id", "created_at"),
    ),
    IndexSpec(
        "idx_stock_movements_reference",
        "stock_movements",
        ("reference_type", "reference_id"),
    ),
)

CURRENT_TABLES = (*V004_TABLES,
    TableSpec("stock_entry_payables", (
        col("id", primary_key=True), col("store_id", not_null=True),
        col("entry_id", not_null=True), col("payable_id", not_null=True),
        col("created_at", not_null=True),
    ), (
        STORE_FK, ForeignKeySpec("entry_id", "stock_entries"),
        ForeignKeySpec("payable_id", "payables"),
    )),
    TableSpec("stock_entry_cancellations", (
        col("id", primary_key=True), col("store_id", not_null=True),
        col("entry_id", not_null=True), col("reason", not_null=True), col("notes"),
        col("idempotency_key", not_null=True), col("request_hash", not_null=True),
        col("response_json", not_null=True), col("user_id"), col("user_name"),
        col("created_at", not_null=True),
    ), (STORE_FK, ForeignKeySpec("entry_id", "stock_entries"))),
    TableSpec("purchase_stock_movements", (
        col("id", primary_key=True), col("store_id", not_null=True),
        col("product_id", not_null=True), col("movement_type", not_null=True),
        col("direction", not_null=True), col("quantity", "INTEGER", not_null=True),
        col("balance_before", "INTEGER", not_null=True),
        col("balance_after", "INTEGER", not_null=True),
        col("reference_type", not_null=True), col("reference_id", not_null=True),
        col("user_id"), col("user_name"), col("created_at", not_null=True),
    ), (STORE_FK, ForeignKeySpec("product_id", "products")), checks=(
        "movement_type IN ('entry_cancellation', 'supplier_return', 'supplier_return_cancellation')",
        "direction IN ('in', 'out')", "quantity > 0",
        "balance_before >= 0", "balance_after >= 0",
    )),
    TableSpec("supplier_return_sequences", (
        col("store_id", primary_key=True),
        col("next_number", "INTEGER", not_null=True, default="1"),
    ), (STORE_FK,), checks=("next_number > 0",)),
    TableSpec("supplier_returns", (
        col("id", primary_key=True), col("store_id", not_null=True),
        col("return_number", "INTEGER", not_null=True),
        col("entry_id", not_null=True), col("supplier_id", not_null=True),
        col("supplier_name", not_null=True), col("reason", not_null=True),
        col("notes"), col("total_quantity", "INTEGER", not_null=True),
        col("total_value", "REAL", not_null=True),
        col("pending_value", "REAL", not_null=True),
        col("status", not_null=True, default="'confirmed'"),
        col("financial_status", not_null=True, default="'pending'"),
        col("idempotency_key", not_null=True), col("request_hash", not_null=True),
        col("response_json", not_null=True), col("user_id"), col("user_name"),
        col("created_at", not_null=True), col("updated_at", not_null=True),
    ), (
        STORE_FK, ForeignKeySpec("entry_id", "stock_entries"),
        ForeignKeySpec("supplier_id", "suppliers"),
    ), checks=(
        "return_number > 0", "total_quantity > 0", "total_value > 0",
        "pending_value >= 0", "status IN ('confirmed', 'cancelled')",
        "financial_status IN ('pending', 'partial', 'settled')",
    )),
    TableSpec("supplier_return_items", (
        col("id", primary_key=True), col("return_id", not_null=True),
        col("entry_item_id", not_null=True), col("product_id", not_null=True),
        col("product_name", not_null=True), col("barcode", not_null=True),
        col("quantity", "INTEGER", not_null=True),
        col("unit_cost", "REAL", not_null=True),
        col("total_cost", "REAL", not_null=True),
        col("stock_before", "INTEGER", not_null=True),
        col("stock_after", "INTEGER", not_null=True),
    ), (
        ForeignKeySpec("return_id", "supplier_returns"),
        ForeignKeySpec("entry_item_id", "stock_entry_items"),
        ForeignKeySpec("product_id", "products"),
    ), checks=(
        "quantity > 0", "unit_cost > 0", "total_cost > 0",
        "stock_before >= 0", "stock_after >= 0",
    )),
    TableSpec("supplier_credits", (
        col("id", primary_key=True), col("store_id", not_null=True),
        col("supplier_id", not_null=True), col("supplier_name", not_null=True),
        col("return_id", not_null=True),
        col("original_amount", "REAL", not_null=True),
        col("used_amount", "REAL", not_null=True, default="0"),
        col("status", not_null=True, default="'available'"),
        col("created_at", not_null=True), col("updated_at", not_null=True),
    ), (
        STORE_FK, ForeignKeySpec("supplier_id", "suppliers"),
        ForeignKeySpec("return_id", "supplier_returns"),
    ), checks=(
        "original_amount > 0", "used_amount >= 0",
        "used_amount <= original_amount",
        "status IN ('available', 'partially_used', 'used', 'reversed')",
    )),
    TableSpec("supplier_return_allocations", (
        col("id", primary_key=True), col("store_id", not_null=True),
        col("return_id", not_null=True), col("allocation_type", not_null=True),
        col("payable_id"), col("credit_id"), col("cash_movement_id"),
        col("amount", "REAL", not_null=True),
        col("status", not_null=True, default="'active'"),
        col("created_at", not_null=True),
    ), (
        STORE_FK, ForeignKeySpec("return_id", "supplier_returns"),
        ForeignKeySpec("payable_id", "payables"),
        ForeignKeySpec("credit_id", "supplier_credits"),
        ForeignKeySpec("cash_movement_id", "cash_movements"),
    ), checks=(
        "allocation_type IN ('payable_abatement', 'supplier_credit', 'cash_refund', 'pix_refund')",
        "amount > 0", "status IN ('active', 'reversed')",
    )),
    TableSpec("supplier_credit_usages", (
        col("id", primary_key=True), col("store_id", not_null=True),
        col("supplier_id", not_null=True), col("payable_id", not_null=True),
        col("amount", "REAL", not_null=True),
        col("status", not_null=True, default="'active'"),
        col("idempotency_key", not_null=True), col("request_hash", not_null=True),
        col("response_json", not_null=True), col("user_id"), col("user_name"),
        col("created_at", not_null=True), col("reversed_at"),
    ), (
        STORE_FK, ForeignKeySpec("supplier_id", "suppliers"),
        ForeignKeySpec("payable_id", "payables"),
    ), checks=("amount > 0", "status IN ('active', 'reversed')")),
    TableSpec("supplier_credit_allocations", (
        col("id", primary_key=True), col("usage_id", not_null=True),
        col("credit_id", not_null=True), col("amount", "REAL", not_null=True),
        col("status", not_null=True, default="'active'"),
        col("created_at", not_null=True),
    ), (
        ForeignKeySpec("usage_id", "supplier_credit_usages"),
        ForeignKeySpec("credit_id", "supplier_credits"),
    ), checks=("amount > 0", "status IN ('active', 'reversed')")),
)

CURRENT_INDEXES = (*V004_INDEXES,
    IndexSpec("idx_stock_entry_payables_entry", "stock_entry_payables", ("store_id", "entry_id")),
    IndexSpec("idx_stock_entry_payables_payable", "stock_entry_payables", ("payable_id",), True),
    IndexSpec("idx_purchase_stock_movements_reference", "purchase_stock_movements", ("reference_type", "reference_id")),
    IndexSpec("idx_purchase_stock_movements_product", "purchase_stock_movements", ("store_id", "product_id", "created_at")),
    IndexSpec("idx_supplier_returns_store_number", "supplier_returns", ("store_id", "return_number"), True),
    IndexSpec("idx_supplier_returns_store_idempotency", "supplier_returns", ("store_id", "idempotency_key"), True),
    IndexSpec("idx_supplier_returns_entry", "supplier_returns", ("store_id", "entry_id", "created_at")),
    IndexSpec("idx_supplier_returns_supplier", "supplier_returns", ("store_id", "supplier_id", "created_at")),
    IndexSpec("idx_supplier_return_items_return", "supplier_return_items", ("return_id",)),
    IndexSpec("idx_supplier_return_items_entry_item", "supplier_return_items", ("entry_item_id",)),
    IndexSpec("idx_supplier_credits_supplier", "supplier_credits", ("store_id", "supplier_id", "created_at")),
    IndexSpec("idx_supplier_credits_return", "supplier_credits", ("return_id",)),
    IndexSpec("idx_supplier_return_allocations_return", "supplier_return_allocations", ("return_id",)),
    IndexSpec("idx_supplier_return_allocations_payable", "supplier_return_allocations", ("payable_id",)),
    IndexSpec("idx_supplier_credit_usages_payable", "supplier_credit_usages", ("store_id", "payable_id", "created_at")),
    IndexSpec("idx_supplier_credit_allocations_usage", "supplier_credit_allocations", ("usage_id",)),
    IndexSpec("idx_supplier_credit_allocations_credit", "supplier_credit_allocations", ("credit_id",)),
)

V005_TABLES = CURRENT_TABLES
V005_INDEXES = CURRENT_INDEXES

CURRENT_TABLES = (
    *V005_TABLES,
    TableSpec("inventory_movements", (
        col("id", primary_key=True), col("store_id", not_null=True),
        col("product_id", not_null=True), col("product_name", not_null=True),
        col("barcode", not_null=True), col("movement_type", not_null=True),
        col("direction", not_null=True),
        col("quantity", "INTEGER", not_null=True),
        col("real_delta", "INTEGER", not_null=True, default="0"),
        col("reserved_delta", "INTEGER", not_null=True, default="0"),
        col("real_before", "INTEGER", not_null=True),
        col("real_after", "INTEGER", not_null=True),
        col("reserved_before", "INTEGER", not_null=True),
        col("reserved_after", "INTEGER", not_null=True),
        col("available_before", "INTEGER", not_null=True),
        col("available_after", "INTEGER", not_null=True),
        col("reference_type", not_null=True),
        col("reference_id", not_null=True),
        col("source_key", not_null=True),
        col("user_id"), col("user_name"), col("notes"),
        col("created_at", not_null=True),
    ), (STORE_FK,), checks=(
        "direction IN ('in', 'out', 'reserve', 'release')",
        "quantity > 0",
        "real_before >= 0",
        "real_after >= 0",
        "reserved_before >= 0",
        "reserved_after >= 0",
        "available_before >= 0",
        "available_after >= 0",
        "real_after = real_before + real_delta",
        "reserved_after = reserved_before + reserved_delta",
        "available_before = real_before - reserved_before",
        "available_after = real_after - reserved_after",
        "real_delta <> 0 OR reserved_delta <> 0",
    )),
)

CURRENT_INDEXES = (
    *V005_INDEXES,
    IndexSpec(
        "idx_inventory_movements_store_source",
        "inventory_movements",
        ("store_id", "source_key"),
        True,
    ),
    IndexSpec(
        "idx_inventory_movements_product_created",
        "inventory_movements",
        ("store_id", "product_id", "created_at"),
    ),
    IndexSpec(
        "idx_inventory_movements_reference",
        "inventory_movements",
        ("store_id", "reference_type", "reference_id"),
    ),
    IndexSpec(
        "idx_inventory_movements_type_created",
        "inventory_movements",
        ("store_id", "movement_type", "created_at"),
    ),
)

V006_TABLES = CURRENT_TABLES
V006_INDEXES = CURRENT_INDEXES

CURRENT_TABLES = (
    *V006_TABLES,
    TableSpec("inventory_sequences", (
        col("store_id", primary_key=True),
        col("next_number", "INTEGER", not_null=True, default="1"),
    ), (STORE_FK,), checks=("next_number > 0",)),
    TableSpec("inventories", (
        col("id", primary_key=True), col("store_id", not_null=True),
        col("inventory_number", "INTEGER", not_null=True),
        col("inventory_type", not_null=True),
        col("scope_json", not_null=True), col("scope_label", not_null=True),
        col("status", not_null=True, default="'in_progress'"),
        col("product_count", "INTEGER", not_null=True),
        col("divergence_count", "INTEGER", not_null=True, default="0"),
        col("positive_item_count", "INTEGER", not_null=True, default="0"),
        col("negative_item_count", "INTEGER", not_null=True, default="0"),
        col("positive_quantity", "INTEGER", not_null=True, default="0"),
        col("negative_quantity", "INTEGER", not_null=True, default="0"),
        col("positive_impact", "REAL", not_null=True, default="0"),
        col("negative_impact", "REAL", not_null=True, default="0"),
        col("general_notes"), col("cancellation_reason"),
        col("idempotency_key", not_null=True), col("request_hash", not_null=True),
        col("response_json", not_null=True), col("finalization_key"),
        col("finalization_response_json"),
        col("started_by_id"), col("started_by_name", not_null=True),
        col("started_at", not_null=True), col("finalized_by_id"),
        col("finalized_by_name"), col("finalized_at"), col("cancelled_by_id"),
        col("cancelled_by_name"), col("cancelled_at"),
        col("updated_at", not_null=True),
    ), (STORE_FK,), checks=(
        "inventory_number > 0",
        "inventory_type IN ('general', 'partial')",
        "status IN ('in_progress', 'finalized', 'cancelled')",
        "product_count > 0",
        "divergence_count >= 0",
        "positive_item_count >= 0",
        "negative_item_count >= 0",
        "positive_quantity >= 0",
        "negative_quantity >= 0",
        "positive_impact >= 0",
        "negative_impact >= 0",
    )),
    TableSpec("inventory_items", (
        col("id", primary_key=True), col("inventory_id", not_null=True),
        col("store_id", not_null=True), col("product_id", not_null=True),
        col("barcode", not_null=True), col("product_name", not_null=True),
        col("brand_name", not_null=True), col("category_name", not_null=True),
        col("gender", not_null=True), col("color", not_null=True),
        col("size", not_null=True),
        col("initial_real", "INTEGER", not_null=True),
        col("initial_reserved", "INTEGER", not_null=True),
        col("initial_available", "INTEGER", not_null=True),
        col("initial_expected", "INTEGER", not_null=True),
        col("counted_quantity", "INTEGER"),
        col("count_version", "INTEGER", not_null=True, default="0"),
        col("counted_by_id"), col("counted_by_name"), col("counted_at"),
        col("final_real", "INTEGER"), col("final_reserved", "INTEGER"),
        col("final_expected", "INTEGER"), col("divergence", "INTEGER"),
        col("adjustment_type"), col("adjustment_quantity", "INTEGER", not_null=True, default="0"),
        col("cost_reference", "REAL"), col("impact_value", "REAL", not_null=True, default="0"),
        col("created_at", not_null=True), col("updated_at", not_null=True),
    ), (
        ForeignKeySpec("inventory_id", "inventories"), STORE_FK,
    ), checks=(
        "initial_real >= 0", "initial_reserved >= 0",
        "initial_available >= 0", "initial_expected >= 0",
        "initial_available = initial_real - initial_reserved",
        "initial_expected = initial_available",
        "counted_quantity IS NULL OR counted_quantity >= 0",
        "count_version >= 0",
        "final_real IS NULL OR final_real >= 0",
        "final_reserved IS NULL OR final_reserved >= 0",
        "final_expected IS NULL OR final_expected >= 0",
        "adjustment_type IS NULL OR adjustment_type IN ('in', 'out', 'none')",
        "adjustment_quantity >= 0",
        "cost_reference IS NULL OR cost_reference >= 0",
        "impact_value >= 0",
    )),
    TableSpec("inventory_count_events", (
        col("id", primary_key=True), col("inventory_id", not_null=True),
        col("inventory_item_id", not_null=True), col("store_id", not_null=True),
        col("previous_quantity", "INTEGER"),
        col("counted_quantity", "INTEGER", not_null=True),
        col("count_version", "INTEGER", not_null=True),
        col("user_id"), col("user_name", not_null=True),
        col("created_at", not_null=True),
    ), (
        ForeignKeySpec("inventory_id", "inventories"),
        ForeignKeySpec("inventory_item_id", "inventory_items"),
        STORE_FK,
    ), checks=(
        "previous_quantity IS NULL OR previous_quantity >= 0",
        "counted_quantity >= 0", "count_version > 0",
    )),
)

CURRENT_INDEXES = (
    *V006_INDEXES,
    IndexSpec(
        "idx_inventories_store_status_started",
        "inventories",
        ("store_id", "status", "started_at"),
    ),
    IndexSpec(
        "idx_inventories_store_type_started",
        "inventories",
        ("store_id", "inventory_type", "started_at"),
    ),
    IndexSpec(
        "idx_inventory_items_inventory",
        "inventory_items",
        ("inventory_id", "product_name"),
    ),
    IndexSpec(
        "idx_inventory_items_product",
        "inventory_items",
        ("store_id", "product_id", "inventory_id"),
    ),
    IndexSpec(
        "idx_inventory_items_barcode",
        "inventory_items",
        ("inventory_id", "barcode"),
    ),
    IndexSpec(
        "idx_inventory_count_events_item",
        "inventory_count_events",
        ("inventory_item_id", "count_version"),
    ),
    IndexSpec(
        "idx_inventory_count_events_inventory",
        "inventory_count_events",
        ("inventory_id", "created_at"),
    ),
)

V007_TABLES = CURRENT_TABLES
V007_INDEXES = CURRENT_INDEXES

V008_TABLES = (
    *V007_TABLES,
    TableSpec("card_modalities", (
        col("id", primary_key=True), col("store_id", not_null=True),
        col("name", not_null=True), col("method", not_null=True),
        col("installments", "INTEGER", not_null=True, default="1"),
        col("status", not_null=True, default="'active'"),
        col("tax_percent", "REAL", not_null=True, default="0"),
        col("receivable_days", "INTEGER", not_null=True, default="1"),
        col("valid_from", not_null=True), col("valid_until"),
        col("created_at", not_null=True), col("updated_at", not_null=True),
    ), (STORE_FK,), checks=(
        "method IN ('debit', 'credit')",
        "status IN ('active', 'inactive')",
        "installments >= 1 AND installments <= 10",
        "tax_percent >= 0",
        "receivable_days >= 0",
    )),
)
V008_INDEXES = (
    *V007_INDEXES,
    IndexSpec(
        "idx_card_modalities_store_status",
        "card_modalities",
        ("store_id", "status"),
    ),
    IndexSpec(
        "idx_card_modalities_store_method_installments",
        "card_modalities",
        ("store_id", "method", "installments"),
    ),
)

CURRENT_TABLES = tuple(
    TableSpec(
        table.name,
        (*table.columns, col("card_modality_id", not_null=True, default="''")),
        table.foreign_keys,
        table.checks,
    )
    if table.name == "card_modalities"
    else table
    for table in V008_TABLES
) + (
    TableSpec("card_modality_history", (
        col("id", primary_key=True), col("card_modality_id", not_null=True),
        col("store_id", not_null=True), col("name", not_null=True),
        col("method", not_null=True),
        col("installments", "INTEGER", not_null=True, default="1"),
        col("status", not_null=True, default="'active'"),
        col("tax_percent", "REAL", not_null=True, default="0"),
        col("receivable_days", "INTEGER", not_null=True, default="1"),
        col("valid_from", not_null=True), col("valid_until"),
        col("created_at", not_null=True), col("updated_at", not_null=True),
    ), (STORE_FK,), checks=(
        "method IN ('debit', 'credit')",
        "status IN ('active', 'inactive')",
        "installments >= 1 AND installments <= 10",
        "tax_percent >= 0",
        "receivable_days >= 0",
    )),
)
CURRENT_INDEXES = (
    *V008_INDEXES,
    IndexSpec(
        "idx_card_modalities_store_stable_id",
        "card_modalities",
        ("store_id", "card_modality_id"),
        True,
    ),
    IndexSpec(
        "idx_card_modality_history_store_modality",
        "card_modality_history",
        ("store_id", "card_modality_id"),
    ),
    IndexSpec(
        "idx_card_modality_history_store_created",
        "card_modality_history",
        ("store_id", "created_at"),
    ),
)

V009_TABLES = CURRENT_TABLES
V009_INDEXES = CURRENT_INDEXES

_V010_TABLE_COLUMNS = {
    "sales": (
        col("sale_number", "INTEGER"),
        col("addition", "REAL", not_null=True, default="0"),
        col("change_amount", "REAL", not_null=True, default="0"),
        col("user_id"),
        col("user_name"),
        col("idempotency_key"),
        col("request_hash"),
        col("response_json"),
    ),
    "sale_items": (
        col("brand_id"),
        col("category_id"),
        col("category"),
        col("size_id"),
        col("size"),
        col("color_id"),
        col("color"),
        col("gender"),
        col("original_unit_price", "REAL", not_null=True, default="0"),
        col("practiced_unit_price", "REAL", not_null=True, default="0"),
        col("unit_discount", "REAL", not_null=True, default="0"),
        col("unit_addition", "REAL", not_null=True, default="0"),
        col("final_unit_price", "REAL", not_null=True, default="0"),
        col("allocated_global_discount", "REAL", not_null=True, default="0"),
        col("allocated_global_addition", "REAL", not_null=True, default="0"),
        col("net_total", "REAL", not_null=True, default="0"),
        col("stock_before", "INTEGER"),
        col("stock_after", "INTEGER"),
    ),
    "sale_payments": (
        col("tendered_amount", "REAL", not_null=True, default="0"),
        col("change_amount", "REAL", not_null=True, default="0"),
        col("card_modality_id"),
        col("card_modality_version_id"),
        col("modality_name"),
        col("tax_percent", "REAL", not_null=True, default="0"),
        col("receivable_days", "INTEGER", not_null=True, default="0"),
        col("gross_amount", "REAL", not_null=True, default="0"),
        col("fee_amount", "REAL", not_null=True, default="0"),
        col("net_amount", "REAL", not_null=True, default="0"),
    ),
    "receivables": (
        col("sale_payment_id"),
        col("card_modality_id"),
        col("card_modality_version_id"),
        col("modality_name"),
        col("card_installments", "INTEGER", not_null=True, default="1"),
        col("tax_percent", "REAL", not_null=True, default="0"),
        col("receivable_days", "INTEGER", not_null=True, default="0"),
        col("gross_amount", "REAL", not_null=True, default="0"),
        col("fee_amount", "REAL", not_null=True, default="0"),
        col("net_amount", "REAL", not_null=True, default="0"),
    ),
}

V010_TABLES = tuple(
    TableSpec(
        table.name,
        (*table.columns, *_V010_TABLE_COLUMNS.get(table.name, ())),
        table.foreign_keys,
        table.checks,
    )
    for table in V009_TABLES
) + (
    TableSpec("sale_sequences", (
        col("store_id", primary_key=True),
        col("next_number", "INTEGER", not_null=True, default="1"),
    ), (STORE_FK,), checks=("next_number > 0",)),
)

V010_INDEXES = (
    *V009_INDEXES,
    IndexSpec(
        "idx_sales_store_number",
        "sales",
        ("store_id", "sale_number"),
        True,
        "sale_number IS NOT NULL",
    ),
    IndexSpec(
        "idx_sales_store_idempotency",
        "sales",
        ("store_id", "idempotency_key"),
        True,
        "idempotency_key IS NOT NULL",
    ),
    IndexSpec(
        "idx_sale_payments_card_modality",
        "sale_payments",
        ("card_modality_id",),
    ),
    IndexSpec(
        "idx_receivables_sale_payment",
        "receivables",
        ("sale_payment_id",),
    ),
)

_V011_TABLE_COLUMNS = {
    "receivables": (
        col("original_due_date"),
        col("open_amount", "REAL"),
        col("discount_total", "REAL", not_null=True, default="0"),
        col("interest_total", "REAL", not_null=True, default="0"),
        col("fine_total", "REAL", not_null=True, default="0"),
        col("addition_total", "REAL", not_null=True, default="0"),
        col("version", "INTEGER", not_null=True, default="0"),
    ),
    "receivable_payments": (
        col("principal_amount", "REAL", not_null=True, default="0"),
        col("settled_amount", "REAL", not_null=True, default="0"),
        col("interest_amount", "REAL", not_null=True, default="0"),
        col("fine_amount", "REAL", not_null=True, default="0"),
        col("addition_amount", "REAL", not_null=True, default="0"),
        col("discount_amount", "REAL", not_null=True, default="0"),
        col("user_id"),
        col("user_name"),
        col("idempotency_key"),
        col("request_hash"),
        col("response_json"),
        col("card_modality_id"),
        col("card_modality_version_id"),
        col("modality_name"),
        col("tax_percent", "REAL", not_null=True, default="0"),
        col("receivable_days", "INTEGER", not_null=True, default="0"),
        col("gross_amount", "REAL", not_null=True, default="0"),
        col("fee_amount", "REAL", not_null=True, default="0"),
        col("net_amount", "REAL", not_null=True, default="0"),
    ),
}

CURRENT_TABLES = tuple(
    TableSpec(
        table.name,
        (*table.columns, *_V011_TABLE_COLUMNS.get(table.name, ())),
        table.foreign_keys,
        table.checks,
    )
    for table in V010_TABLES
) + (
    TableSpec("receivable_renegotiations", (
        col("id", primary_key=True),
        col("store_id", not_null=True),
        col("receivable_id", not_null=True),
        col("sale_id"),
        col("customer_id"),
        col("previous_due_date", not_null=True),
        col("new_due_date", not_null=True),
        col("previous_open_amount", "REAL", not_null=True),
        col("new_open_amount", "REAL", not_null=True),
        col("payment_amount", "REAL", not_null=True, default="0"),
        col("settled_amount", "REAL", not_null=True, default="0"),
        col("interest_amount", "REAL", not_null=True, default="0"),
        col("fine_amount", "REAL", not_null=True, default="0"),
        col("addition_amount", "REAL", not_null=True, default="0"),
        col("discount_amount", "REAL", not_null=True, default="0"),
        col("method"),
        col("payment_id"),
        col("reason"),
        col("user_id"),
        col("user_name"),
        col("idempotency_key"),
        col("request_hash"),
        col("response_json"),
        col("created_at", not_null=True),
    ), (
        STORE_FK,
        ForeignKeySpec("receivable_id", "receivables"),
    )),
)

CURRENT_INDEXES = (
    *V010_INDEXES,
    IndexSpec(
        "idx_receivable_payments_store_idempotency",
        "receivable_payments",
        ("store_id", "idempotency_key"),
        True,
        "idempotency_key IS NOT NULL",
    ),
    IndexSpec(
        "idx_receivable_payments_card_modality",
        "receivable_payments",
        ("card_modality_id",),
    ),
    IndexSpec(
        "idx_receivable_renegotiations_receivable",
        "receivable_renegotiations",
        ("store_id", "receivable_id", "created_at"),
    ),
    IndexSpec(
        "idx_receivable_renegotiations_store_idempotency",
        "receivable_renegotiations",
        ("store_id", "idempotency_key"),
        True,
        "idempotency_key IS NOT NULL",
    ),
)

V011_TABLES = CURRENT_TABLES
V011_INDEXES = CURRENT_INDEXES

_V012_TABLE_COLUMNS = {
    "sales": (
        col("conditional_id"),
    ),
    "sale_items": (
        col("conditional_item_id"),
    ),
}

CURRENT_TABLES = tuple(
    TableSpec(
        table.name,
        (*table.columns, *_V012_TABLE_COLUMNS.get(table.name, ())),
        table.foreign_keys,
        table.checks,
    )
    for table in V011_TABLES
) + (
    TableSpec("conditional_sequences", (
        col("store_id", primary_key=True),
        col("next_number", "INTEGER", not_null=True, default="1"),
    ), (STORE_FK,), checks=("next_number > 0",)),
    TableSpec("conditionals", (
        col("id", primary_key=True), col("store_id", not_null=True),
        col("conditional_number", "INTEGER", not_null=True),
        col("customer_id", not_null=True), col("customer_name", not_null=True),
        col("customer_cpf"), col("customer_phone"),
        col("status", not_null=True, default="'open'"),
        col("checked_out_at", not_null=True),
        col("expected_return_date", not_null=True),
        col("responsible_user_id"), col("responsible_user_name"),
        col("cancellation_reason"), col("cancelled_at"),
        col("cancelled_by_user_id"), col("cancelled_by_user_name"),
        col("finalized_at"), col("idempotency_key"), col("request_hash"),
        col("response_json"), col("created_at", not_null=True),
        col("updated_at", not_null=True),
    ), (
        STORE_FK,
        ForeignKeySpec("customer_id", "customers"),
    ), checks=(
        "conditional_number > 0",
        "status IN ('open', 'finalized', 'cancelled')",
    )),
    TableSpec("conditional_items", (
        col("id", primary_key=True), col("conditional_id", not_null=True),
        col("product_id", not_null=True), col("barcode"),
        col("name", not_null=True), col("brand"), col("size"), col("color"),
        col("original_quantity", "INTEGER", not_null=True),
        col("returned_quantity", "INTEGER", not_null=True, default="0"),
        col("sold_quantity", "INTEGER", not_null=True, default="0"),
        col("pending_sale_quantity", "INTEGER", not_null=True, default="0"),
        col("reference_unit_price", "REAL", not_null=True, default="0"),
        col("reference_unit_cost", "REAL", not_null=True, default="0"),
        col("created_at", not_null=True), col("updated_at", not_null=True),
    ), (
        ForeignKeySpec("conditional_id", "conditionals", on_delete="CASCADE"),
    ), checks=(
        "original_quantity > 0",
        "returned_quantity >= 0",
        "sold_quantity >= 0",
        "pending_sale_quantity >= 0",
        "returned_quantity + sold_quantity + pending_sale_quantity <= original_quantity",
        "reference_unit_price >= 0",
        "reference_unit_cost >= 0",
    )),
    TableSpec("conditional_returns", (
        col("id", primary_key=True), col("store_id", not_null=True),
        col("conditional_id", not_null=True),
        col("status", not_null=True, default="'completed'"),
        col("user_id"), col("user_name"), col("idempotency_key"),
        col("request_hash"), col("response_json"),
        col("created_at", not_null=True),
    ), (
        STORE_FK,
        ForeignKeySpec("conditional_id", "conditionals"),
    ), checks=("status IN ('completed', 'awaiting_sale')",)),
    TableSpec("conditional_return_items", (
        col("id", primary_key=True), col("return_id", not_null=True),
        col("conditional_item_id", not_null=True),
        col("product_id", not_null=True),
        col("returned_quantity", "INTEGER", not_null=True, default="0"),
        col("purchase_quantity", "INTEGER", not_null=True, default="0"),
        col("sale_id"), col("status", not_null=True, default="'completed'"),
    ), (
        ForeignKeySpec("return_id", "conditional_returns", on_delete="CASCADE"),
        ForeignKeySpec("conditional_item_id", "conditional_items"),
    ), checks=(
        "returned_quantity >= 0",
        "purchase_quantity >= 0",
        "returned_quantity + purchase_quantity > 0",
        "status IN ('completed', 'awaiting_sale')",
    )),
    TableSpec("conditional_sale_links", (
        col("id", primary_key=True), col("store_id", not_null=True),
        col("conditional_id", not_null=True), col("return_id", not_null=True),
        col("sale_id", not_null=True), col("created_at", not_null=True),
    ), (
        STORE_FK,
        ForeignKeySpec("conditional_id", "conditionals"),
        ForeignKeySpec("return_id", "conditional_returns"),
        ForeignKeySpec("sale_id", "sales"),
    )),
)

CURRENT_INDEXES = (
    *V011_INDEXES,
    IndexSpec("idx_conditionals_store_number", "conditionals", ("store_id", "conditional_number"), True),
    IndexSpec(
        "idx_conditionals_store_idempotency",
        "conditionals",
        ("store_id", "idempotency_key"),
        True,
        "idempotency_key IS NOT NULL",
    ),
    IndexSpec("idx_conditionals_customer_status", "conditionals", ("store_id", "customer_id", "status")),
    IndexSpec("idx_conditionals_expected_return", "conditionals", ("store_id", "expected_return_date", "status")),
    IndexSpec("idx_conditional_items_conditional", "conditional_items", ("conditional_id",)),
    IndexSpec("idx_conditional_items_product", "conditional_items", ("product_id",)),
    IndexSpec(
        "idx_conditional_returns_store_idempotency",
        "conditional_returns",
        ("store_id", "idempotency_key"),
        True,
        "idempotency_key IS NOT NULL",
    ),
    IndexSpec("idx_conditional_returns_conditional", "conditional_returns", ("store_id", "conditional_id", "created_at")),
    IndexSpec("idx_conditional_return_items_return", "conditional_return_items", ("return_id",)),
    IndexSpec("idx_conditional_sale_links_sale", "conditional_sale_links", ("store_id", "sale_id"), True),
    IndexSpec("idx_conditional_sale_links_conditional", "conditional_sale_links", ("store_id", "conditional_id", "created_at")),
    IndexSpec("idx_sales_conditional", "sales", ("conditional_id",)),
    IndexSpec("idx_sale_items_conditional_item", "sale_items", ("conditional_item_id",)),
)

_V013_TABLE_COLUMNS = {
    "sales": (col("exchange_id"), col("warranty_id")),
    "sale_items": (col("exchange_item_id"),),
    "sale_returns": (
        col("return_number", "INTEGER"),
        col("customer_id"),
        col("status", not_null=True, default="'completed'"),
        col("origin", not_null=True, default="'commercial'"),
        col("gross_total", "REAL", not_null=True, default="0"),
        col("discount_total", "REAL", not_null=True, default="0"),
        col("net_total", "REAL", not_null=True, default="0"),
        col("cost_total", "REAL", not_null=True, default="0"),
        col("user_id"),
        col("user_name"),
        col("idempotency_key"),
        col("request_hash"),
        col("response_json"),
        col("reconciliation_required", "INTEGER", not_null=True, default="0"),
        col("warranty_id"),
        col("exchange_id"),
    ),
    "sale_return_items": (
        col("sale_item_id"),
        col("barcode"),
        col("brand"),
        col("size"),
        col("color"),
        col("gross_total", "REAL", not_null=True, default="0"),
        col("allocated_discount", "REAL", not_null=True, default="0"),
        col("net_total", "REAL", not_null=True, default="0"),
        col("unit_cost", "REAL", not_null=True, default="0"),
        col("cost_total", "REAL", not_null=True, default="0"),
        col("physical_condition", not_null=True, default="'resellable'"),
        col("restocked", "INTEGER", not_null=True, default="1"),
    ),
    "receivables": (
        col("return_reduction_total", "REAL", not_null=True, default="0"),
    ),
    "stock_entries": (
        col("origin", not_null=True, default="'purchase'"),
        col("warranty_id"),
    ),
}

CURRENT_TABLES = tuple(
    TableSpec(
        table.name,
        (*table.columns, *_V013_TABLE_COLUMNS.get(table.name, ())),
        table.foreign_keys,
        table.checks,
    )
    for table in CURRENT_TABLES
) + (
    TableSpec("sale_return_sequences", (
        col("store_id", primary_key=True),
        col("next_number", "INTEGER", not_null=True, default="1"),
    ), (STORE_FK,), checks=("next_number > 0",)),
    TableSpec("sale_return_allocations", (
        col("id", primary_key=True), col("store_id", not_null=True),
        col("return_id", not_null=True), col("sale_payment_id"),
        col("receivable_id"), col("method", not_null=True),
        col("gross_amount", "REAL", not_null=True, default="0"),
        col("pending_reduction", "REAL", not_null=True, default="0"),
        col("refunded_amount", "REAL", not_null=True, default="0"),
        col("status", not_null=True), col("cash_movement_id"),
        col("reconciliation_required", "INTEGER", not_null=True, default="0"),
        col("created_at", not_null=True),
    ), (
        STORE_FK,
        ForeignKeySpec("return_id", "sale_returns", on_delete="CASCADE"),
    ), checks=(
        "gross_amount >= 0", "pending_reduction >= 0",
        "refunded_amount >= 0",
        "status IN ('pending_reduced', 'refunded', 'mixed', 'manual_reconciliation')",
    )),
    TableSpec("sale_return_receivable_reductions", (
        col("id", primary_key=True), col("store_id", not_null=True),
        col("return_id", not_null=True), col("sale_payment_id", not_null=True),
        col("receivable_id", not_null=True),
        col("amount", "REAL", not_null=True),
        col("open_amount_before", "REAL", not_null=True),
        col("open_amount_after", "REAL", not_null=True),
        col("status_before", not_null=True), col("status_after", not_null=True),
        col("created_at", not_null=True),
    ), (
        STORE_FK,
        ForeignKeySpec("return_id", "sale_returns", on_delete="CASCADE"),
        ForeignKeySpec("receivable_id", "receivables"),
    ), checks=(
        "amount > 0", "open_amount_before >= 0", "open_amount_after >= 0",
    )),
    TableSpec("exchange_sequences", (
        col("store_id", primary_key=True),
        col("next_number", "INTEGER", not_null=True, default="1"),
    ), (STORE_FK,), checks=("next_number > 0",)),
    TableSpec("exchanges", (
        col("id", primary_key=True), col("store_id", not_null=True),
        col("exchange_number", "INTEGER", not_null=True),
        col("sale_id", not_null=True), col("customer_id"),
        col("customer_name", not_null=True),
        col("status", not_null=True, default="'completed'"),
        col("origin", not_null=True, default="'commercial'"),
        col("warranty_id"), col("reason", not_null=True), col("notes"),
        col("credit_total", "REAL", not_null=True, default="0"),
        col("new_items_total", "REAL", not_null=True, default="0"),
        col("difference_amount", "REAL", not_null=True, default="0"),
        col("difference_direction", not_null=True, default="'none'"),
        col("linked_sale_id"), col("user_id"), col("user_name"),
        col("idempotency_key"), col("request_hash"), col("response_json"),
        col("reconciliation_required", "INTEGER", not_null=True, default="0"),
        col("created_at", not_null=True), col("updated_at", not_null=True),
    ), (STORE_FK, ForeignKeySpec("sale_id", "sales")), checks=(
        "exchange_number > 0",
        "status IN ('completed', 'cancelled')",
        "origin IN ('commercial', 'warranty')",
        "credit_total >= 0", "new_items_total >= 0",
        "difference_amount >= 0",
        "difference_direction IN ('pay', 'refund', 'none')",
    )),
    TableSpec("exchange_return_items", (
        col("id", primary_key=True), col("exchange_id", not_null=True),
        col("sale_item_id", not_null=True), col("product_id", not_null=True),
        col("barcode"), col("name", not_null=True), col("brand"),
        col("size"), col("color"), col("quantity", "INTEGER", not_null=True),
        col("unit_credit", "REAL", not_null=True, default="0"),
        col("credit_total", "REAL", not_null=True, default="0"),
        col("unit_cost", "REAL", not_null=True, default="0"),
        col("cost_total", "REAL", not_null=True, default="0"),
        col("physical_condition", not_null=True),
        col("restocked", "INTEGER", not_null=True, default="0"),
    ), (ForeignKeySpec("exchange_id", "exchanges", on_delete="CASCADE"),),
    checks=(
        "quantity > 0", "unit_credit >= 0", "credit_total >= 0",
        "unit_cost >= 0", "cost_total >= 0",
        "physical_condition IN ('resellable', 'damaged')",
    )),
    TableSpec("exchange_new_items", (
        col("id", primary_key=True), col("exchange_id", not_null=True),
        col("product_id", not_null=True), col("barcode"),
        col("name", not_null=True), col("brand"), col("size"), col("color"),
        col("quantity", "INTEGER", not_null=True),
        col("original_unit_price", "REAL", not_null=True, default="0"),
        col("practiced_unit_price", "REAL", not_null=True, default="0"),
        col("unit_discount", "REAL", not_null=True, default="0"),
        col("unit_addition", "REAL", not_null=True, default="0"),
        col("net_total", "REAL", not_null=True, default="0"),
        col("unit_cost", "REAL", not_null=True, default="0"),
        col("cost_total", "REAL", not_null=True, default="0"),
        col("stock_before", "INTEGER", not_null=True),
        col("stock_after", "INTEGER", not_null=True),
    ), (ForeignKeySpec("exchange_id", "exchanges", on_delete="CASCADE"),),
    checks=(
        "quantity > 0", "original_unit_price >= 0",
        "practiced_unit_price >= 0", "unit_discount >= 0",
        "unit_addition >= 0", "net_total >= 0", "unit_cost >= 0",
        "cost_total >= 0", "stock_before >= 0", "stock_after >= 0",
    )),
    TableSpec("exchange_payments", (
        col("id", primary_key=True), col("exchange_id", not_null=True),
        col("method", not_null=True),
        col("amount", "REAL", not_null=True, default="0"),
        col("direction", not_null=True), col("sale_payment_id"),
        col("cash_movement_id"), col("receivable_id"),
    ), (ForeignKeySpec("exchange_id", "exchanges", on_delete="CASCADE"),),
    checks=("amount >= 0", "direction IN ('in', 'out')")),
    TableSpec("exchange_cancellations", (
        col("id", primary_key=True), col("store_id", not_null=True),
        col("exchange_id", not_null=True), col("reason", not_null=True),
        col("idempotency_key", not_null=True),
        col("request_hash", not_null=True),
        col("response_json", not_null=True),
        col("user_id"), col("user_name"), col("created_at", not_null=True),
    ), (
        STORE_FK,
        ForeignKeySpec("exchange_id", "exchanges"),
    ), checks=("reason <> ''",)),
    TableSpec("warranty_sequences", (
        col("store_id", primary_key=True),
        col("next_number", "INTEGER", not_null=True, default="1"),
    ), (STORE_FK,), checks=("next_number > 0",)),
    TableSpec("warranties", (
        col("id", primary_key=True), col("store_id", not_null=True),
        col("warranty_number", "INTEGER", not_null=True),
        col("sale_id", not_null=True), col("sale_item_id", not_null=True),
        col("customer_id"), col("customer_name", not_null=True),
        col("contact_name"), col("contact_phone"),
        col("product_id", not_null=True), col("barcode"),
        col("product_name", not_null=True), col("brand"), col("size"),
        col("color"), col("quantity", "INTEGER", not_null=True),
        col("defect_category", not_null=True),
        col("defect_description", not_null=True),
        col("physical_location", not_null=True),
        col("status", not_null=True, default="'open'"), col("supplier_id"),
        col("supplier_name"), col("supplier_protocol"), col("solution_type"),
        col("solution_reference_id"),
        col("awaiting_customer_delivery", "INTEGER", not_null=True, default="0"),
        col("opened_by_user_id"), col("opened_by_user_name"),
        col("idempotency_key"), col("request_hash"), col("response_json"),
        col("created_at", not_null=True), col("updated_at", not_null=True),
        col("resolved_at"), col("cancelled_at"),
    ), (STORE_FK, ForeignKeySpec("sale_id", "sales")), checks=(
        "warranty_number > 0", "quantity > 0",
        "physical_location IN ('customer', 'store', 'supplier')",
        "status IN ('open', 'analysis', 'supplier', 'approved', 'rejected', 'resolved', 'cancelled')",
    )),
    TableSpec("warranty_photos", (
        col("id", primary_key=True), col("warranty_id", not_null=True),
        col("url", not_null=True), col("storage"),
        col("created_at", not_null=True),
    ), (ForeignKeySpec("warranty_id", "warranties", on_delete="CASCADE"),)),
    TableSpec("warranty_events", (
        col("id", primary_key=True), col("warranty_id", not_null=True),
        col("store_id", not_null=True), col("event_type", not_null=True),
        col("previous_status"), col("new_status"), col("notes"),
        col("supplier_id"), col("supplier_name"), col("protocol"),
        col("replacement_product_id"), col("replacement_product_name"),
        col("replacement_quantity", "INTEGER"),
        col("replacement_unit_cost", "REAL"),
        col("replacement_destination"), col("stock_entry_id"),
        col("user_id"), col("user_name"), col("created_at", not_null=True),
    ), (
        ForeignKeySpec("warranty_id", "warranties", on_delete="CASCADE"),
        STORE_FK,
    )),
)

CURRENT_INDEXES = (
    *CURRENT_INDEXES,
    IndexSpec("idx_sale_returns_store_number", "sale_returns", ("store_id", "return_number"), True, "return_number IS NOT NULL"),
    IndexSpec("idx_sale_returns_store_idempotency", "sale_returns", ("store_id", "idempotency_key"), True, "idempotency_key IS NOT NULL"),
    IndexSpec("idx_sale_return_items_sale_item", "sale_return_items", ("sale_item_id",)),
    IndexSpec("idx_sale_return_allocations_return", "sale_return_allocations", ("store_id", "return_id")),
    IndexSpec("idx_sale_return_allocations_receivable", "sale_return_allocations", ("receivable_id",)),
    IndexSpec("idx_sale_return_reductions_return", "sale_return_receivable_reductions", ("store_id", "return_id")),
    IndexSpec("idx_sale_return_reductions_receivable", "sale_return_receivable_reductions", ("receivable_id",)),
    IndexSpec("idx_exchanges_store_number", "exchanges", ("store_id", "exchange_number"), True),
    IndexSpec("idx_exchanges_store_idempotency", "exchanges", ("store_id", "idempotency_key"), True, "idempotency_key IS NOT NULL"),
    IndexSpec("idx_exchanges_sale", "exchanges", ("store_id", "sale_id", "created_at")),
    IndexSpec("idx_exchange_return_items_sale_item", "exchange_return_items", ("sale_item_id",)),
    IndexSpec("idx_exchange_new_items_product", "exchange_new_items", ("product_id",)),
    IndexSpec(
        "idx_exchange_cancellations_store_key",
        "exchange_cancellations",
        ("store_id", "idempotency_key"),
        True,
    ),
    IndexSpec(
        "idx_exchange_cancellations_exchange",
        "exchange_cancellations",
        ("exchange_id",),
        True,
    ),
    IndexSpec("idx_warranties_store_number", "warranties", ("store_id", "warranty_number"), True),
    IndexSpec("idx_warranties_store_idempotency", "warranties", ("store_id", "idempotency_key"), True, "idempotency_key IS NOT NULL"),
    IndexSpec("idx_warranties_sale", "warranties", ("store_id", "sale_id", "created_at")),
    IndexSpec("idx_warranties_customer_status", "warranties", ("store_id", "customer_id", "status")),
    IndexSpec("idx_warranties_supplier_status", "warranties", ("store_id", "supplier_id", "status")),
    IndexSpec("idx_warranties_product_status", "warranties", ("store_id", "product_id", "status")),
    IndexSpec("idx_warranty_events_warranty", "warranty_events", ("warranty_id", "created_at")),
    IndexSpec("idx_warranty_photos_warranty", "warranty_photos", ("warranty_id",)),
    IndexSpec("idx_sales_exchange", "sales", ("exchange_id",)),
    IndexSpec("idx_sales_warranty", "sales", ("warranty_id",)),
)

V013_TABLES = CURRENT_TABLES
V013_INDEXES = CURRENT_INDEXES

_V014_TABLE_COLUMNS = {
    "cash_movements": (
        col("origin_type", not_null=True, default="'legacy'"),
        col("origin_id"),
        col("user_id"),
        col("user_name"),
        col("resulting_balance", "REAL"),
        col("reversal_of_id"),
        col("reversed_at"),
        col("idempotency_key"),
        col("request_hash"),
        col("response_json"),
    ),
    "payables": (
        col("open_amount", "REAL"),
        col("interest", "REAL", not_null=True, default="0"),
        col("fine", "REAL", not_null=True, default="0"),
        col("recurring", "INTEGER", not_null=True, default="0"),
        col("recurring_day", "INTEGER"),
        col("recurring_series_id"),
        col("recurrence_month"),
        col("generated_from_id"),
        col("version", "INTEGER", not_null=True, default="0"),
        col("cancelled_at"),
        col("cancellation_reason"),
        col("cancelled_by_id"),
        col("cancelled_by_name"),
    ),
}

CURRENT_TABLES = tuple(
    TableSpec(
        table.name,
        (*table.columns, *_V014_TABLE_COLUMNS.get(table.name, ())),
        table.foreign_keys,
        table.checks,
    )
    for table in CURRENT_TABLES
) + (
    TableSpec("payable_payments", (
        col("id", primary_key=True), col("store_id", not_null=True),
        col("payable_id", not_null=True),
        col("cash_movement_id"),
        col("amount", "REAL", not_null=True),
        col("interest_amount", "REAL", not_null=True, default="0"),
        col("fine_amount", "REAL", not_null=True, default="0"),
        col("discount_amount", "REAL", not_null=True, default="0"),
        col("method", not_null=True), col("note"),
        col("status", not_null=True, default="'active'"),
        col("reversal_cash_movement_id"), col("reversed_at"),
        col("reversal_reason"), col("reversal_idempotency_key"),
        col("reversal_request_hash"), col("reversal_response_json"),
        col("user_id"), col("user_name"),
        col("idempotency_key", not_null=True),
        col("request_hash", not_null=True),
        col("response_json", not_null=True),
        col("created_at", not_null=True),
    ), (
        STORE_FK,
        ForeignKeySpec("payable_id", "payables"),
        ForeignKeySpec("cash_movement_id", "cash_movements"),
    ), checks=(
        "amount >= 0", "interest_amount >= 0", "fine_amount >= 0",
        "discount_amount >= 0",
        "method IN ('cash', 'pix', 'debit')",
        "status IN ('active', 'reversed')",
    )),
    TableSpec("payable_events", (
        col("id", primary_key=True), col("store_id", not_null=True),
        col("payable_id", not_null=True), col("event_type", not_null=True),
        col("payment_id"), col("previous_status"), col("new_status"),
        col("details_json", not_null=True), col("user_id"),
        col("user_name"), col("created_at", not_null=True),
    ), (
        STORE_FK,
        ForeignKeySpec("payable_id", "payables"),
    ), checks=(
        "event_type IN ('created', 'updated', 'payment', 'payment_reversal', 'cancelled', 'recurrence')",
    )),
    TableSpec("bank_receipts", (
        col("id", primary_key=True), col("store_id", not_null=True),
        col("description", not_null=True),
        col("credit_amount", "REAL", not_null=True, default="0"),
        col("debit_amount", "REAL", not_null=True, default="0"),
        col("total_amount", "REAL", not_null=True),
        col("status", not_null=True, default="'registered'"),
        col("user_id"), col("user_name"),
        col("idempotency_key", not_null=True),
        col("request_hash", not_null=True),
        col("response_json", not_null=True),
        col("created_at", not_null=True),
    ), (STORE_FK,), checks=(
        "credit_amount >= 0", "debit_amount >= 0", "total_amount > 0",
        "status IN ('registered', 'reversed')",
    )),
    TableSpec("sale_cancellations", (
        col("id", primary_key=True), col("store_id", not_null=True),
        col("sale_id", not_null=True), col("return_id", not_null=True),
        col("reason", not_null=True),
        col("reconciliation_required", "INTEGER", not_null=True, default="0"),
        col("user_id"), col("user_name"),
        col("idempotency_key", not_null=True),
        col("request_hash", not_null=True),
        col("response_json", not_null=True),
        col("created_at", not_null=True),
    ), (
        STORE_FK,
        ForeignKeySpec("sale_id", "sales"),
        ForeignKeySpec("return_id", "sale_returns"),
    ), checks=("reason <> ''",)),
)

CURRENT_INDEXES = (
    *CURRENT_INDEXES,
    IndexSpec(
        "idx_cash_store_idempotency",
        "cash_movements",
        ("store_id", "idempotency_key"),
        True,
        "idempotency_key IS NOT NULL",
    ),
    IndexSpec(
        "idx_cash_reversal_once",
        "cash_movements",
        ("reversal_of_id",),
        True,
        "reversal_of_id IS NOT NULL",
    ),
    IndexSpec(
        "idx_cash_origin",
        "cash_movements",
        ("store_id", "origin_type", "origin_id"),
    ),
    IndexSpec(
        "idx_payable_payments_store_key",
        "payable_payments",
        ("store_id", "idempotency_key"),
        True,
    ),
    IndexSpec(
        "idx_payable_payments_payable",
        "payable_payments",
        ("store_id", "payable_id", "created_at"),
    ),
    IndexSpec(
        "idx_payable_payment_reversal_key",
        "payable_payments",
        ("store_id", "reversal_idempotency_key"),
        True,
        "reversal_idempotency_key IS NOT NULL",
    ),
    IndexSpec(
        "idx_payable_events_payable",
        "payable_events",
        ("store_id", "payable_id", "created_at"),
    ),
    IndexSpec(
        "idx_payables_recurrence_month",
        "payables",
        ("store_id", "recurring_series_id", "recurrence_month"),
        True,
        "recurring_series_id IS NOT NULL AND recurrence_month IS NOT NULL",
    ),
    IndexSpec(
        "idx_bank_receipts_store_key",
        "bank_receipts",
        ("store_id", "idempotency_key"),
        True,
    ),
    IndexSpec(
        "idx_sale_cancellations_store_key",
        "sale_cancellations",
        ("store_id", "idempotency_key"),
        True,
    ),
    IndexSpec(
        "idx_sale_cancellations_sale",
        "sale_cancellations",
        ("sale_id",),
        True,
    ),
)

V014_TABLES = CURRENT_TABLES
V014_INDEXES = CURRENT_INDEXES

_V015_TABLE_COLUMNS = {
    "receivables": (
        col("difference_amount", "REAL", not_null=True, default="0"),
    ),
    "receivable_payments": (
        col("reconciliation_id"),
        col("status", not_null=True, default="'active'"),
        col("reversed_at"),
        col("reversal_reason"),
    ),
}

CURRENT_TABLES = tuple(
    TableSpec(
        table.name,
        (*table.columns, *_V015_TABLE_COLUMNS.get(table.name, ())),
        table.foreign_keys,
        table.checks,
    )
    for table in CURRENT_TABLES
) + (
    TableSpec("card_reconciliations", (
        col("id", primary_key=True), col("store_id", not_null=True),
        col("receipt_date", not_null=True),
        col("total_received", "REAL", not_null=True),
        col("item_count", "INTEGER", not_null=True),
        col("note"), col("status", not_null=True, default="'active'"),
        col("cash_movement_id", not_null=True),
        col("reversal_cash_movement_id"),
        col("user_id"), col("user_name"),
        col("idempotency_key", not_null=True),
        col("request_hash", not_null=True),
        col("response_json", not_null=True),
        col("reversed_at"), col("reversal_reason"),
        col("reversed_by_id"), col("reversed_by_name"),
        col("reversal_idempotency_key"),
        col("reversal_request_hash"), col("reversal_response_json"),
        col("created_at", not_null=True),
    ), (
        STORE_FK,
        ForeignKeySpec("cash_movement_id", "cash_movements"),
        ForeignKeySpec("reversal_cash_movement_id", "cash_movements"),
    ), checks=(
        "total_received > 0", "item_count > 0",
        "status IN ('active', 'reversed')",
    )),
    TableSpec("card_reconciliation_items", (
        col("id", primary_key=True), col("store_id", not_null=True),
        col("reconciliation_id", not_null=True),
        col("receivable_id", not_null=True),
        col("payment_id", not_null=True), col("sale_id"),
        col("method", not_null=True), col("modality_name"),
        col("expected_balance_before", "REAL", not_null=True),
        col("allocated_amount", "REAL", not_null=True),
        col("close_with_divergence", "INTEGER", not_null=True, default="0"),
        col("divergence_note"), col("difference_after", "REAL", not_null=True, default="0"),
        col("difference_before", "REAL", not_null=True, default="0"),
        col("received_before", "REAL", not_null=True),
        col("received_after", "REAL", not_null=True),
        col("open_amount_before", "REAL", not_null=True),
        col("open_amount_after", "REAL", not_null=True),
        col("status_before", not_null=True), col("status_after", not_null=True),
        col("version_before", "INTEGER", not_null=True),
        col("version_after", "INTEGER", not_null=True),
        col("paid_at_before"), col("last_payment_at_before"),
        col("created_at", not_null=True),
    ), (
        STORE_FK,
        ForeignKeySpec("reconciliation_id", "card_reconciliations"),
        ForeignKeySpec("receivable_id", "receivables"),
        ForeignKeySpec("payment_id", "receivable_payments"),
    ), checks=(
        "expected_balance_before >= 0", "allocated_amount >= 0",
        "received_before >= 0", "received_after >= 0",
        "open_amount_before >= 0", "open_amount_after >= 0",
        "version_after = version_before + 1",
    )),
)

CURRENT_INDEXES = (
    *CURRENT_INDEXES,
    IndexSpec(
        "idx_card_reconciliations_store_key",
        "card_reconciliations",
        ("store_id", "idempotency_key"),
        True,
    ),
    IndexSpec(
        "idx_card_reconciliation_reversal_key",
        "card_reconciliations",
        ("store_id", "reversal_idempotency_key"),
        True,
        "reversal_idempotency_key IS NOT NULL",
    ),
    IndexSpec(
        "idx_card_reconciliations_store_date",
        "card_reconciliations",
        ("store_id", "receipt_date", "created_at"),
    ),
    IndexSpec(
        "idx_card_reconciliation_items_group",
        "card_reconciliation_items",
        ("reconciliation_id", "created_at"),
    ),
    IndexSpec(
        "idx_card_reconciliation_items_receivable",
        "card_reconciliation_items",
        ("store_id", "receivable_id", "created_at"),
    ),
    IndexSpec(
        "idx_receivable_payments_reconciliation",
        "receivable_payments",
        ("reconciliation_id",),
    ),
)

V015_TABLES = CURRENT_TABLES
V015_INDEXES = CURRENT_INDEXES

CURRENT_TABLES = (
    *CURRENT_TABLES,
    TableSpec("generated_documents", (
        col("id", primary_key=True), col("store_id", not_null=True),
        col("document_type", not_null=True), col("source_type", not_null=True),
        col("source_id"), col("operation_number"),
        col("format", not_null=True), col("template_version", not_null=True),
        col("copy_number", "INTEGER", not_null=True, default="1"),
        col("filename", not_null=True), col("snapshot_json", not_null=True),
        col("generated_by_id"), col("generated_by_name"),
        col("idempotency_key", not_null=True),
        col("request_hash", not_null=True), col("generated_at", not_null=True),
    ), (STORE_FK,), checks=(
        "document_type IN ('sale_receipt', 'conditional', 'exchange', 'catalog', 'product_labels')",
        "source_type IN ('sale', 'conditional', 'exchange', 'catalog', 'product')",
        "format IN ('a4', 'thermal')",
        "copy_number > 0", "filename <> ''", "template_version <> ''",
    )),
)

CURRENT_INDEXES = (
    *CURRENT_INDEXES,
    IndexSpec(
        "idx_generated_documents_store_key",
        "generated_documents",
        ("store_id", "idempotency_key"),
        True,
    ),
    IndexSpec(
        "idx_generated_documents_source",
        "generated_documents",
        ("store_id", "source_type", "source_id", "document_type", "generated_at"),
    ),
    IndexSpec(
        "idx_generated_documents_store_created",
        "generated_documents",
        ("store_id", "generated_at"),
    ),
)

V016_TABLES = CURRENT_TABLES
V016_INDEXES = CURRENT_INDEXES

CURRENT_TABLES = (
    *CURRENT_TABLES,
    TableSpec("alert_user_states", (
        col("id", primary_key=True), col("store_id", not_null=True),
        col("user_id", not_null=True), col("alert_id", not_null=True),
        col("read_at"), col("pinned_at"),
        col("created_at", not_null=True), col("updated_at", not_null=True),
    ), (
        STORE_FK,
        ForeignKeySpec("user_id", "users", on_delete="CASCADE"),
    )),
)

CURRENT_INDEXES = (
    *CURRENT_INDEXES,
    IndexSpec(
        "idx_alert_user_states_identity",
        "alert_user_states",
        ("store_id", "user_id", "alert_id"),
        True,
    ),
    IndexSpec(
        "idx_alert_user_states_user_updated",
        "alert_user_states",
        ("store_id", "user_id", "updated_at"),
    ),
)

V017_TABLES = CURRENT_TABLES
V017_INDEXES = CURRENT_INDEXES

CURRENT_TABLES = tuple(
    TableSpec(
        table.name,
        (
            *table.columns,
            col("failed_login_attempts", "INTEGER", not_null=True, default="0"),
            col("blocked_at"),
            col("last_login_at"),
        ),
        table.foreign_keys,
        table.checks,
    )
    if table.name == "users"
    else table
    for table in CURRENT_TABLES
)

CURRENT_TABLES = (
    *CURRENT_TABLES,
    TableSpec("store_settings", (
        col("store_id", primary_key=True),
        col("legal_name"), col("trade_name"), col("document"), col("document_type"),
        col("phone"), col("whatsapp"), col("email"), col("zip"), col("address"),
        col("address_number"), col("complement"), col("district"), col("city"), col("state"),
        col("logo_url"),
        col("print_show_document", "INTEGER", not_null=True, default="1"),
        col("print_show_phone", "INTEGER", not_null=True, default="1"),
        col("print_show_whatsapp", "INTEGER", not_null=True, default="1"),
        col("print_show_address", "INTEGER", not_null=True, default="1"),
        col("print_show_email", "INTEGER", not_null=True, default="1"),
        col("receipt_footer"), col("pix_key"), col("pix_key_type"),
        col("pix_recipient_name"), col("pix_recipient_document"), col("pix_bank"),
        col("pix_enabled", "INTEGER", not_null=True, default="1"),
        col("debit_enabled", "INTEGER", not_null=True, default="1"),
        col("credit_enabled", "INTEGER", not_null=True, default="1"),
        col("store_credit_enabled", "INTEGER", not_null=True, default="1"),
        col("version", "INTEGER", not_null=True, default="1"),
        col("updated_by_id"), col("updated_by_name"),
        col("created_at", not_null=True), col("updated_at", not_null=True),
    ), (STORE_FK,)),
    TableSpec("user_preferences", (
        col("id", primary_key=True), col("store_id", not_null=True),
        col("user_id", not_null=True), col("theme", not_null=True, default="'system'"),
        col("version", "INTEGER", not_null=True, default="1"),
        col("created_at", not_null=True), col("updated_at", not_null=True),
    ), (
        STORE_FK,
        ForeignKeySpec("user_id", "users", on_delete="CASCADE"),
    ), checks=("theme IN ('light', 'dark', 'system')",)),
)

CURRENT_INDEXES = (
    *CURRENT_INDEXES,
    IndexSpec(
        "idx_user_preferences_identity",
        "user_preferences",
        ("store_id", "user_id"),
        True,
    ),
    IndexSpec(
        "idx_store_settings_updated",
        "store_settings",
        ("updated_at",),
    ),
)

V018_TABLES = CURRENT_TABLES
V018_INDEXES = CURRENT_INDEXES

LATEST_SCHEMA_STATEMENTS = tuple(table.ddl() for table in CURRENT_TABLES) + tuple(
    index.ddl() for index in CURRENT_INDEXES
)

CURRENT_TABLE_NAMES = frozenset(table.name for table in CURRENT_TABLES)
CURRENT_INDEX_NAMES = frozenset(index.name for index in CURRENT_INDEXES)
