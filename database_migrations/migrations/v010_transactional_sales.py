from __future__ import annotations

from ..models import Migration


ALTER_STATEMENTS = (
    "ALTER TABLE sales ADD COLUMN sale_number INTEGER",
    "ALTER TABLE sales ADD COLUMN addition REAL NOT NULL DEFAULT 0",
    "ALTER TABLE sales ADD COLUMN change_amount REAL NOT NULL DEFAULT 0",
    "ALTER TABLE sales ADD COLUMN user_id TEXT",
    "ALTER TABLE sales ADD COLUMN user_name TEXT",
    "ALTER TABLE sales ADD COLUMN idempotency_key TEXT",
    "ALTER TABLE sales ADD COLUMN request_hash TEXT",
    "ALTER TABLE sales ADD COLUMN response_json TEXT",
    "ALTER TABLE sale_items ADD COLUMN brand_id TEXT",
    "ALTER TABLE sale_items ADD COLUMN category_id TEXT",
    "ALTER TABLE sale_items ADD COLUMN category TEXT",
    "ALTER TABLE sale_items ADD COLUMN size_id TEXT",
    "ALTER TABLE sale_items ADD COLUMN size TEXT",
    "ALTER TABLE sale_items ADD COLUMN color_id TEXT",
    "ALTER TABLE sale_items ADD COLUMN color TEXT",
    "ALTER TABLE sale_items ADD COLUMN gender TEXT",
    "ALTER TABLE sale_items ADD COLUMN original_unit_price REAL NOT NULL DEFAULT 0",
    "ALTER TABLE sale_items ADD COLUMN practiced_unit_price REAL NOT NULL DEFAULT 0",
    "ALTER TABLE sale_items ADD COLUMN unit_discount REAL NOT NULL DEFAULT 0",
    "ALTER TABLE sale_items ADD COLUMN unit_addition REAL NOT NULL DEFAULT 0",
    "ALTER TABLE sale_items ADD COLUMN final_unit_price REAL NOT NULL DEFAULT 0",
    "ALTER TABLE sale_items ADD COLUMN allocated_global_discount REAL NOT NULL DEFAULT 0",
    "ALTER TABLE sale_items ADD COLUMN allocated_global_addition REAL NOT NULL DEFAULT 0",
    "ALTER TABLE sale_items ADD COLUMN net_total REAL NOT NULL DEFAULT 0",
    "ALTER TABLE sale_items ADD COLUMN stock_before INTEGER",
    "ALTER TABLE sale_items ADD COLUMN stock_after INTEGER",
    "ALTER TABLE sale_payments ADD COLUMN tendered_amount REAL NOT NULL DEFAULT 0",
    "ALTER TABLE sale_payments ADD COLUMN change_amount REAL NOT NULL DEFAULT 0",
    "ALTER TABLE sale_payments ADD COLUMN card_modality_id TEXT",
    "ALTER TABLE sale_payments ADD COLUMN card_modality_version_id TEXT",
    "ALTER TABLE sale_payments ADD COLUMN modality_name TEXT",
    "ALTER TABLE sale_payments ADD COLUMN tax_percent REAL NOT NULL DEFAULT 0",
    "ALTER TABLE sale_payments ADD COLUMN receivable_days INTEGER NOT NULL DEFAULT 0",
    "ALTER TABLE sale_payments ADD COLUMN gross_amount REAL NOT NULL DEFAULT 0",
    "ALTER TABLE sale_payments ADD COLUMN fee_amount REAL NOT NULL DEFAULT 0",
    "ALTER TABLE sale_payments ADD COLUMN net_amount REAL NOT NULL DEFAULT 0",
    "ALTER TABLE receivables ADD COLUMN sale_payment_id TEXT",
    "ALTER TABLE receivables ADD COLUMN card_modality_id TEXT",
    "ALTER TABLE receivables ADD COLUMN card_modality_version_id TEXT",
    "ALTER TABLE receivables ADD COLUMN modality_name TEXT",
    "ALTER TABLE receivables ADD COLUMN card_installments INTEGER NOT NULL DEFAULT 1",
    "ALTER TABLE receivables ADD COLUMN tax_percent REAL NOT NULL DEFAULT 0",
    "ALTER TABLE receivables ADD COLUMN receivable_days INTEGER NOT NULL DEFAULT 0",
    "ALTER TABLE receivables ADD COLUMN gross_amount REAL NOT NULL DEFAULT 0",
    "ALTER TABLE receivables ADD COLUMN fee_amount REAL NOT NULL DEFAULT 0",
    "ALTER TABLE receivables ADD COLUMN net_amount REAL NOT NULL DEFAULT 0",
)

TABLE_STATEMENTS = (
    """
    CREATE TABLE sale_sequences (
        store_id TEXT PRIMARY KEY,
        next_number INTEGER NOT NULL DEFAULT 1,
        FOREIGN KEY (store_id) REFERENCES stores(id),
        CHECK (next_number > 0)
    )
    """,
)

INDEX_STATEMENTS = (
    "CREATE UNIQUE INDEX idx_sales_store_number ON sales(store_id, sale_number) WHERE sale_number IS NOT NULL",
    "CREATE UNIQUE INDEX idx_sales_store_idempotency ON sales(store_id, idempotency_key) WHERE idempotency_key IS NOT NULL",
    "CREATE INDEX idx_sale_payments_card_modality ON sale_payments(card_modality_id)",
    "CREATE INDEX idx_receivables_sale_payment ON receivables(sale_payment_id)",
)


MIGRATION_010 = Migration(
    version=10,
    description="Add transactional sales and immutable snapshots",
    sqlite_statements=(*ALTER_STATEMENTS, *TABLE_STATEMENTS, *INDEX_STATEMENTS),
    postgresql_statements=(*ALTER_STATEMENTS, *TABLE_STATEMENTS, *INDEX_STATEMENTS),
    code_id="mova-sports-transactional-sales-v10",
)
