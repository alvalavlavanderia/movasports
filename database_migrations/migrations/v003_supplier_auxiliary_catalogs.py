from __future__ import annotations

import re
import unicodedata

from ..models import Migration


ALTER_STATEMENTS = (
    "ALTER TABLE brands ADD COLUMN normalized_name TEXT",
    "ALTER TABLE brands ADD COLUMN status TEXT NOT NULL DEFAULT 'active'",
    "ALTER TABLE brands ADD COLUMN created_at TEXT",
    "ALTER TABLE categories ADD COLUMN normalized_name TEXT",
    "ALTER TABLE categories ADD COLUMN status TEXT NOT NULL DEFAULT 'active'",
    "ALTER TABLE categories ADD COLUMN created_at TEXT",
    "ALTER TABLE suppliers ADD COLUMN trade_name TEXT",
    "ALTER TABLE suppliers ADD COLUMN document_normalized TEXT",
    "ALTER TABLE suppliers ADD COLUMN whatsapp TEXT",
    "ALTER TABLE suppliers ADD COLUMN zip TEXT",
    "ALTER TABLE suppliers ADD COLUMN address_number TEXT",
    "ALTER TABLE suppliers ADD COLUMN district TEXT",
    "ALTER TABLE suppliers ADD COLUMN city TEXT",
    "ALTER TABLE suppliers ADD COLUMN state TEXT",
    "ALTER TABLE suppliers ADD COLUMN notes TEXT",
    "ALTER TABLE suppliers ADD COLUMN status TEXT NOT NULL DEFAULT 'active'",
    "ALTER TABLE suppliers ADD COLUMN created_at TEXT",
    "ALTER TABLE products ADD COLUMN brand_id TEXT",
    "ALTER TABLE products ADD COLUMN category_id TEXT",
    "ALTER TABLE products ADD COLUMN size_id TEXT",
    "ALTER TABLE products ADD COLUMN color_id TEXT",
    "ALTER TABLE products ADD COLUMN supplier_id TEXT",
    "ALTER TABLE payables ADD COLUMN supplier_id TEXT",
    "ALTER TABLE payables ADD COLUMN expense_category_id TEXT",
    "ALTER TABLE cash_movements ADD COLUMN expense_category_id TEXT",
)

TABLE_STATEMENTS = (
    """
    CREATE TABLE sizes (
        id TEXT PRIMARY KEY,
        store_id TEXT NOT NULL,
        name TEXT NOT NULL,
        normalized_name TEXT,
        status TEXT NOT NULL DEFAULT 'active',
        created_at TEXT,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (store_id) REFERENCES stores(id)
    )
    """,
    """
    CREATE TABLE colors (
        id TEXT PRIMARY KEY,
        store_id TEXT NOT NULL,
        name TEXT NOT NULL,
        normalized_name TEXT,
        status TEXT NOT NULL DEFAULT 'active',
        created_at TEXT,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (store_id) REFERENCES stores(id)
    )
    """,
    """
    CREATE TABLE expense_categories (
        id TEXT PRIMARY KEY,
        store_id TEXT NOT NULL,
        name TEXT NOT NULL,
        normalized_name TEXT,
        status TEXT NOT NULL DEFAULT 'active',
        created_at TEXT,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (store_id) REFERENCES stores(id)
    )
    """,
    """
    CREATE TABLE supplier_status_history (
        id TEXT PRIMARY KEY,
        store_id TEXT NOT NULL,
        supplier_id TEXT NOT NULL,
        previous_status TEXT NOT NULL,
        new_status TEXT NOT NULL,
        reason TEXT,
        user_id TEXT,
        user_name TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (store_id) REFERENCES stores(id),
        FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
    )
    """,
)

INDEX_STATEMENTS = (
    "CREATE UNIQUE INDEX idx_brands_store_normalized_name ON brands(store_id, normalized_name) WHERE normalized_name IS NOT NULL AND normalized_name <> ''",
    "CREATE UNIQUE INDEX idx_categories_store_normalized_name ON categories(store_id, normalized_name) WHERE normalized_name IS NOT NULL AND normalized_name <> ''",
    "CREATE UNIQUE INDEX idx_suppliers_store_document ON suppliers(store_id, document_normalized) WHERE document_normalized IS NOT NULL AND document_normalized <> ''",
    "CREATE INDEX idx_suppliers_store_status ON suppliers(store_id, status)",
    "CREATE UNIQUE INDEX idx_sizes_store_normalized_name ON sizes(store_id, normalized_name) WHERE normalized_name IS NOT NULL AND normalized_name <> ''",
    "CREATE UNIQUE INDEX idx_colors_store_normalized_name ON colors(store_id, normalized_name) WHERE normalized_name IS NOT NULL AND normalized_name <> ''",
    "CREATE UNIQUE INDEX idx_expense_categories_store_normalized_name ON expense_categories(store_id, normalized_name) WHERE normalized_name IS NOT NULL AND normalized_name <> ''",
    "CREATE INDEX idx_supplier_status_history_supplier ON supplier_status_history(store_id, supplier_id, created_at)",
    "CREATE INDEX idx_products_brand_id ON products(store_id, brand_id)",
    "CREATE INDEX idx_products_category_id ON products(store_id, category_id)",
    "CREATE INDEX idx_products_size_id ON products(store_id, size_id)",
    "CREATE INDEX idx_products_color_id ON products(store_id, color_id)",
    "CREATE INDEX idx_products_supplier_id ON products(store_id, supplier_id)",
    "CREATE INDEX idx_payables_supplier_id ON payables(store_id, supplier_id)",
    "CREATE INDEX idx_payables_expense_category_id ON payables(store_id, expense_category_id)",
    "CREATE INDEX idx_cash_expense_category_id ON cash_movements(store_id, expense_category_id)",
)

EXPENSE_CATEGORY_NAMES = (
    "Mercadorias",
    "Aluguel",
    "Energia",
    "Água",
    "Internet",
    "Impostos",
    "Salários",
    "Serviços",
    "Gasolina",
    "Lanches",
    "Estacionamento",
    "Material de limpeza",
    "Motoboy",
    "Acessórios",
    "Outros",
)


def _normalized_name(name: str) -> str:
    decomposed = unicodedata.normalize("NFKD", name)
    without_accents = "".join(char for char in decomposed if not unicodedata.combining(char))
    return " ".join(without_accents.casefold().split())


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", _normalized_name(name)).strip("-")


def _sqlite_expense_insert(name: str) -> str:
    slug = _slug(name)
    normalized = _normalized_name(name)
    return f"""
        INSERT INTO expense_categories (
            id, store_id, name, normalized_name, status, created_at, updated_at
        )
        SELECT
            stores.id || ':expense-category:{slug}', stores.id, '{name}', '{normalized}',
            'active', strftime('%Y-%m-%dT%H:%M:%fZ', 'now'),
            strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
        FROM stores
        WHERE NOT EXISTS (
            SELECT 1 FROM expense_categories
            WHERE expense_categories.store_id = stores.id
              AND expense_categories.normalized_name = '{normalized}'
        )
    """


def _postgresql_expense_insert(name: str) -> str:
    slug = _slug(name)
    normalized = _normalized_name(name)
    return f"""
        INSERT INTO expense_categories (
            id, store_id, name, normalized_name, status, created_at, updated_at
        )
        SELECT
            stores.id || ':expense-category:{slug}', stores.id, '{name}', '{normalized}',
            'active', CURRENT_TIMESTAMP::text, CURRENT_TIMESTAMP::text
        FROM stores
        WHERE NOT EXISTS (
            SELECT 1 FROM expense_categories
            WHERE expense_categories.store_id = stores.id
              AND expense_categories.normalized_name = '{normalized}'
        )
    """


LINK_BACKFILL_STATEMENTS = (
    """
    UPDATE products
    SET brand_id = (
        SELECT brands.id FROM brands
        WHERE brands.store_id = products.store_id
          AND brands.name = products.brand_name
        LIMIT 1
    )
    WHERE brand_id IS NULL AND brand_name IS NOT NULL AND brand_name <> ''
    """,
    """
    UPDATE products
    SET category_id = (
        SELECT categories.id FROM categories
        WHERE categories.store_id = products.store_id
          AND categories.name = products.category_name
        LIMIT 1
    )
    WHERE category_id IS NULL AND category_name IS NOT NULL AND category_name <> ''
    """,
    """
    UPDATE payables
    SET supplier_id = (
        SELECT suppliers.id FROM suppliers
        WHERE suppliers.store_id = payables.store_id
          AND suppliers.name = payables.supplier
        LIMIT 1
    )
    WHERE supplier_id IS NULL AND supplier IS NOT NULL AND supplier <> ''
    """,
    """
    UPDATE payables
    SET expense_category_id = (
        SELECT expense_categories.id FROM expense_categories
        WHERE expense_categories.store_id = payables.store_id
          AND expense_categories.name = payables.category
        LIMIT 1
    )
    WHERE expense_category_id IS NULL AND category IS NOT NULL AND category <> ''
    """,
    """
    UPDATE cash_movements
    SET expense_category_id = (
        SELECT expense_categories.id FROM expense_categories
        WHERE expense_categories.store_id = cash_movements.store_id
          AND expense_categories.name = cash_movements.type
        LIMIT 1
    )
    WHERE expense_category_id IS NULL
      AND direction = 'out'
      AND type IS NOT NULL
      AND type <> ''
    """,
)


MIGRATION_003 = Migration(
    version=3,
    description="Add supplier and auxiliary business rules",
    sqlite_statements=(
        *ALTER_STATEMENTS,
        *TABLE_STATEMENTS,
        *INDEX_STATEMENTS,
        *(_sqlite_expense_insert(name) for name in EXPENSE_CATEGORY_NAMES),
        *LINK_BACKFILL_STATEMENTS,
    ),
    postgresql_statements=(
        *ALTER_STATEMENTS,
        *TABLE_STATEMENTS,
        *INDEX_STATEMENTS,
        *(_postgresql_expense_insert(name) for name in EXPENSE_CATEGORY_NAMES),
        *LINK_BACKFILL_STATEMENTS,
    ),
    code_id="mova-sports-supplier-auxiliary-business-rules-v3",
)
