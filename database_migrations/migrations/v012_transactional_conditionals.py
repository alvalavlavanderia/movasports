from __future__ import annotations

from ..models import Migration


ALTER_STATEMENTS = (
    "ALTER TABLE sales ADD COLUMN conditional_id TEXT",
    "ALTER TABLE sale_items ADD COLUMN conditional_item_id TEXT",
)

TABLE_STATEMENTS = (
    """
    CREATE TABLE conditional_sequences (
        store_id TEXT PRIMARY KEY,
        next_number INTEGER NOT NULL DEFAULT 1,
        FOREIGN KEY (store_id) REFERENCES stores(id),
        CHECK (next_number > 0)
    )
    """,
    """
    CREATE TABLE conditionals (
        id TEXT PRIMARY KEY,
        store_id TEXT NOT NULL,
        conditional_number INTEGER NOT NULL,
        customer_id TEXT NOT NULL,
        customer_name TEXT NOT NULL,
        customer_cpf TEXT,
        customer_phone TEXT,
        status TEXT NOT NULL DEFAULT 'open',
        checked_out_at TEXT NOT NULL,
        expected_return_date TEXT NOT NULL,
        responsible_user_id TEXT,
        responsible_user_name TEXT,
        cancellation_reason TEXT,
        cancelled_at TEXT,
        cancelled_by_user_id TEXT,
        cancelled_by_user_name TEXT,
        finalized_at TEXT,
        idempotency_key TEXT,
        request_hash TEXT,
        response_json TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (store_id) REFERENCES stores(id),
        FOREIGN KEY (customer_id) REFERENCES customers(id),
        CHECK (conditional_number > 0),
        CHECK (status IN ('open', 'finalized', 'cancelled'))
    )
    """,
    """
    CREATE TABLE conditional_items (
        id TEXT PRIMARY KEY,
        conditional_id TEXT NOT NULL,
        product_id TEXT NOT NULL,
        barcode TEXT,
        name TEXT NOT NULL,
        brand TEXT,
        size TEXT,
        color TEXT,
        original_quantity INTEGER NOT NULL,
        returned_quantity INTEGER NOT NULL DEFAULT 0,
        sold_quantity INTEGER NOT NULL DEFAULT 0,
        pending_sale_quantity INTEGER NOT NULL DEFAULT 0,
        reference_unit_price REAL NOT NULL DEFAULT 0,
        reference_unit_cost REAL NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (conditional_id) REFERENCES conditionals(id) ON DELETE CASCADE,
        CHECK (original_quantity > 0),
        CHECK (returned_quantity >= 0),
        CHECK (sold_quantity >= 0),
        CHECK (pending_sale_quantity >= 0),
        CHECK (
            returned_quantity + sold_quantity + pending_sale_quantity
            <= original_quantity
        ),
        CHECK (reference_unit_price >= 0),
        CHECK (reference_unit_cost >= 0)
    )
    """,
    """
    CREATE TABLE conditional_returns (
        id TEXT PRIMARY KEY,
        store_id TEXT NOT NULL,
        conditional_id TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'completed',
        user_id TEXT,
        user_name TEXT,
        idempotency_key TEXT,
        request_hash TEXT,
        response_json TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (store_id) REFERENCES stores(id),
        FOREIGN KEY (conditional_id) REFERENCES conditionals(id),
        CHECK (status IN ('completed', 'awaiting_sale'))
    )
    """,
    """
    CREATE TABLE conditional_return_items (
        id TEXT PRIMARY KEY,
        return_id TEXT NOT NULL,
        conditional_item_id TEXT NOT NULL,
        product_id TEXT NOT NULL,
        returned_quantity INTEGER NOT NULL DEFAULT 0,
        purchase_quantity INTEGER NOT NULL DEFAULT 0,
        sale_id TEXT,
        status TEXT NOT NULL DEFAULT 'completed',
        FOREIGN KEY (return_id) REFERENCES conditional_returns(id) ON DELETE CASCADE,
        FOREIGN KEY (conditional_item_id) REFERENCES conditional_items(id),
        CHECK (returned_quantity >= 0),
        CHECK (purchase_quantity >= 0),
        CHECK (returned_quantity + purchase_quantity > 0),
        CHECK (status IN ('completed', 'awaiting_sale'))
    )
    """,
    """
    CREATE TABLE conditional_sale_links (
        id TEXT PRIMARY KEY,
        store_id TEXT NOT NULL,
        conditional_id TEXT NOT NULL,
        return_id TEXT NOT NULL,
        sale_id TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (store_id) REFERENCES stores(id),
        FOREIGN KEY (conditional_id) REFERENCES conditionals(id),
        FOREIGN KEY (return_id) REFERENCES conditional_returns(id),
        FOREIGN KEY (sale_id) REFERENCES sales(id)
    )
    """,
)

INDEX_STATEMENTS = (
    "CREATE UNIQUE INDEX idx_conditionals_store_number ON conditionals(store_id, conditional_number)",
    "CREATE UNIQUE INDEX idx_conditionals_store_idempotency ON conditionals(store_id, idempotency_key) WHERE idempotency_key IS NOT NULL",
    "CREATE INDEX idx_conditionals_customer_status ON conditionals(store_id, customer_id, status)",
    "CREATE INDEX idx_conditionals_expected_return ON conditionals(store_id, expected_return_date, status)",
    "CREATE INDEX idx_conditional_items_conditional ON conditional_items(conditional_id)",
    "CREATE INDEX idx_conditional_items_product ON conditional_items(product_id)",
    "CREATE UNIQUE INDEX idx_conditional_returns_store_idempotency ON conditional_returns(store_id, idempotency_key) WHERE idempotency_key IS NOT NULL",
    "CREATE INDEX idx_conditional_returns_conditional ON conditional_returns(store_id, conditional_id, created_at)",
    "CREATE INDEX idx_conditional_return_items_return ON conditional_return_items(return_id)",
    "CREATE UNIQUE INDEX idx_conditional_sale_links_sale ON conditional_sale_links(store_id, sale_id)",
    "CREATE INDEX idx_conditional_sale_links_conditional ON conditional_sale_links(store_id, conditional_id, created_at)",
    "CREATE INDEX idx_sales_conditional ON sales(conditional_id)",
    "CREATE INDEX idx_sale_items_conditional_item ON sale_items(conditional_item_id)",
)


MIGRATION_012 = Migration(
    version=12,
    description="Add transactional conditionals and sale conversion",
    sqlite_statements=(*ALTER_STATEMENTS, *TABLE_STATEMENTS, *INDEX_STATEMENTS),
    postgresql_statements=(*ALTER_STATEMENTS, *TABLE_STATEMENTS, *INDEX_STATEMENTS),
    code_id="mova-sports-transactional-conditionals-v12",
)
