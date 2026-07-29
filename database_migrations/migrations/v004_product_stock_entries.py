from __future__ import annotations

from ..models import Migration


ALTER_STATEMENTS = (
    "ALTER TABLE products ADD COLUMN barcode_normalized TEXT",
    "ALTER TABLE products ADD COLUMN created_at TEXT",
    "ALTER TABLE products ADD COLUMN stock_entered_at TEXT",
)

BACKFILL_STATEMENTS = (
    """
    UPDATE products
    SET barcode_normalized = UPPER(TRIM(barcode))
    WHERE barcode IS NOT NULL AND TRIM(barcode) <> ''
      AND (barcode_normalized IS NULL OR barcode_normalized = '')
    """,
)

TABLE_STATEMENTS = (
    """
    CREATE TABLE stock_entry_sequences (
        store_id TEXT PRIMARY KEY,
        next_number INTEGER NOT NULL DEFAULT 1,
        FOREIGN KEY (store_id) REFERENCES stores(id),
        CHECK (next_number > 0)
    )
    """,
    """
    CREATE TABLE stock_entries (
        id TEXT PRIMARY KEY,
        store_id TEXT NOT NULL,
        entry_number INTEGER NOT NULL,
        supplier_id TEXT NOT NULL,
        supplier_name TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'confirmed',
        total_quantity INTEGER NOT NULL,
        total_cost REAL NOT NULL,
        idempotency_key TEXT NOT NULL,
        request_hash TEXT NOT NULL,
        response_json TEXT NOT NULL,
        user_id TEXT,
        user_name TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (store_id) REFERENCES stores(id),
        FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
        CHECK (entry_number > 0),
        CHECK (total_quantity > 0),
        CHECK (total_cost > 0),
        CHECK (status = 'confirmed')
    )
    """,
    """
    CREATE TABLE stock_entry_items (
        id TEXT PRIMARY KEY,
        entry_id TEXT NOT NULL,
        product_id TEXT NOT NULL,
        barcode TEXT NOT NULL,
        product_name TEXT NOT NULL,
        brand_id TEXT,
        brand_name TEXT,
        category_id TEXT,
        category_name TEXT,
        size_id TEXT,
        size_name TEXT,
        color_id TEXT,
        color_name TEXT,
        supplier_id TEXT NOT NULL,
        supplier_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        unit_cost REAL NOT NULL,
        total_cost REAL NOT NULL,
        sale_price REAL NOT NULL,
        stock_before INTEGER NOT NULL,
        stock_after INTEGER NOT NULL,
        FOREIGN KEY (entry_id) REFERENCES stock_entries(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(id),
        FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
        CHECK (quantity > 0),
        CHECK (unit_cost > 0),
        CHECK (total_cost > 0),
        CHECK (sale_price >= 0),
        CHECK (stock_before >= 0),
        CHECK (stock_after = stock_before + quantity)
    )
    """,
    """
    CREATE TABLE stock_movements (
        id TEXT PRIMARY KEY,
        store_id TEXT NOT NULL,
        product_id TEXT NOT NULL,
        movement_type TEXT NOT NULL,
        direction TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        balance_before INTEGER NOT NULL,
        balance_after INTEGER NOT NULL,
        reference_type TEXT NOT NULL,
        reference_id TEXT NOT NULL,
        user_id TEXT,
        user_name TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (store_id) REFERENCES stores(id),
        FOREIGN KEY (product_id) REFERENCES products(id),
        CHECK (movement_type = 'entry'),
        CHECK (direction = 'in'),
        CHECK (quantity > 0),
        CHECK (balance_before >= 0),
        CHECK (balance_after = balance_before + quantity)
    )
    """,
)

INDEX_STATEMENTS = (
    "CREATE UNIQUE INDEX idx_products_store_barcode_normalized ON products(store_id, barcode_normalized) WHERE barcode_normalized IS NOT NULL AND barcode_normalized <> ''",
    "CREATE UNIQUE INDEX idx_stock_entries_store_number ON stock_entries(store_id, entry_number)",
    "CREATE UNIQUE INDEX idx_stock_entries_store_idempotency ON stock_entries(store_id, idempotency_key)",
    "CREATE INDEX idx_stock_entries_store_created ON stock_entries(store_id, created_at)",
    "CREATE INDEX idx_stock_entries_supplier ON stock_entries(store_id, supplier_id, created_at)",
    "CREATE INDEX idx_stock_entry_items_entry ON stock_entry_items(entry_id)",
    "CREATE INDEX idx_stock_entry_items_product ON stock_entry_items(product_id, entry_id)",
    "CREATE INDEX idx_stock_movements_product_created ON stock_movements(store_id, product_id, created_at)",
    "CREATE INDEX idx_stock_movements_reference ON stock_movements(reference_type, reference_id)",
)


MIGRATION_004 = Migration(
    version=4,
    description="Add product stock entry core",
    sqlite_statements=(
        *ALTER_STATEMENTS,
        *BACKFILL_STATEMENTS,
        *TABLE_STATEMENTS,
        *INDEX_STATEMENTS,
    ),
    postgresql_statements=(
        *ALTER_STATEMENTS,
        *BACKFILL_STATEMENTS,
        *TABLE_STATEMENTS,
        *INDEX_STATEMENTS,
    ),
    code_id="mova-sports-product-stock-entry-core-v4",
)
