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


CURRENT_SCHEMA_STATEMENTS = tuple(table.ddl() for table in CURRENT_TABLES) + tuple(
    index.ddl() for index in CURRENT_INDEXES
)

CURRENT_TABLE_NAMES = frozenset(table.name for table in CURRENT_TABLES)
CURRENT_INDEX_NAMES = frozenset(index.name for index in CURRENT_INDEXES)
