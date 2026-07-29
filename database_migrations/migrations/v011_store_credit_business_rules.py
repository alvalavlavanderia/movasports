from __future__ import annotations

from ..models import Migration


ALTER_STATEMENTS = (
    "ALTER TABLE receivables ADD COLUMN original_due_date TEXT",
    "ALTER TABLE receivables ADD COLUMN open_amount REAL",
    "ALTER TABLE receivables ADD COLUMN discount_total REAL NOT NULL DEFAULT 0",
    "ALTER TABLE receivables ADD COLUMN interest_total REAL NOT NULL DEFAULT 0",
    "ALTER TABLE receivables ADD COLUMN fine_total REAL NOT NULL DEFAULT 0",
    "ALTER TABLE receivables ADD COLUMN addition_total REAL NOT NULL DEFAULT 0",
    "ALTER TABLE receivables ADD COLUMN version INTEGER NOT NULL DEFAULT 0",
    "ALTER TABLE receivable_payments ADD COLUMN principal_amount REAL NOT NULL DEFAULT 0",
    "ALTER TABLE receivable_payments ADD COLUMN settled_amount REAL NOT NULL DEFAULT 0",
    "ALTER TABLE receivable_payments ADD COLUMN interest_amount REAL NOT NULL DEFAULT 0",
    "ALTER TABLE receivable_payments ADD COLUMN fine_amount REAL NOT NULL DEFAULT 0",
    "ALTER TABLE receivable_payments ADD COLUMN addition_amount REAL NOT NULL DEFAULT 0",
    "ALTER TABLE receivable_payments ADD COLUMN discount_amount REAL NOT NULL DEFAULT 0",
    "ALTER TABLE receivable_payments ADD COLUMN user_id TEXT",
    "ALTER TABLE receivable_payments ADD COLUMN user_name TEXT",
    "ALTER TABLE receivable_payments ADD COLUMN idempotency_key TEXT",
    "ALTER TABLE receivable_payments ADD COLUMN request_hash TEXT",
    "ALTER TABLE receivable_payments ADD COLUMN response_json TEXT",
    "ALTER TABLE receivable_payments ADD COLUMN card_modality_id TEXT",
    "ALTER TABLE receivable_payments ADD COLUMN card_modality_version_id TEXT",
    "ALTER TABLE receivable_payments ADD COLUMN modality_name TEXT",
    "ALTER TABLE receivable_payments ADD COLUMN tax_percent REAL NOT NULL DEFAULT 0",
    "ALTER TABLE receivable_payments ADD COLUMN receivable_days INTEGER NOT NULL DEFAULT 0",
    "ALTER TABLE receivable_payments ADD COLUMN gross_amount REAL NOT NULL DEFAULT 0",
    "ALTER TABLE receivable_payments ADD COLUMN fee_amount REAL NOT NULL DEFAULT 0",
    "ALTER TABLE receivable_payments ADD COLUMN net_amount REAL NOT NULL DEFAULT 0",
)

TABLE_STATEMENTS = (
    """
    CREATE TABLE receivable_renegotiations (
        id TEXT PRIMARY KEY,
        store_id TEXT NOT NULL,
        receivable_id TEXT NOT NULL,
        sale_id TEXT,
        customer_id TEXT,
        previous_due_date TEXT NOT NULL,
        new_due_date TEXT NOT NULL,
        previous_open_amount REAL NOT NULL,
        new_open_amount REAL NOT NULL,
        payment_amount REAL NOT NULL DEFAULT 0,
        settled_amount REAL NOT NULL DEFAULT 0,
        interest_amount REAL NOT NULL DEFAULT 0,
        fine_amount REAL NOT NULL DEFAULT 0,
        addition_amount REAL NOT NULL DEFAULT 0,
        discount_amount REAL NOT NULL DEFAULT 0,
        method TEXT,
        payment_id TEXT,
        reason TEXT,
        user_id TEXT,
        user_name TEXT,
        idempotency_key TEXT,
        request_hash TEXT,
        response_json TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (store_id) REFERENCES stores(id),
        FOREIGN KEY (receivable_id) REFERENCES receivables(id)
    )
    """,
)

INDEX_STATEMENTS = (
    "CREATE UNIQUE INDEX idx_receivable_payments_store_idempotency ON receivable_payments(store_id, idempotency_key) WHERE idempotency_key IS NOT NULL",
    "CREATE INDEX idx_receivable_payments_card_modality ON receivable_payments(card_modality_id)",
    "CREATE INDEX idx_receivable_renegotiations_receivable ON receivable_renegotiations(store_id, receivable_id, created_at)",
    "CREATE UNIQUE INDEX idx_receivable_renegotiations_store_idempotency ON receivable_renegotiations(store_id, idempotency_key) WHERE idempotency_key IS NOT NULL",
)


MIGRATION_011 = Migration(
    version=11,
    description="Add store credit payments and renegotiation history",
    sqlite_statements=(*ALTER_STATEMENTS, *TABLE_STATEMENTS, *INDEX_STATEMENTS),
    postgresql_statements=(*ALTER_STATEMENTS, *TABLE_STATEMENTS, *INDEX_STATEMENTS),
    code_id="mova-sports-store-credit-business-rules-v11",
)
