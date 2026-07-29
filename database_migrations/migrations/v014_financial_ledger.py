from __future__ import annotations

from ..models import Migration


ALTER_STATEMENTS = (
    "ALTER TABLE cash_movements ADD COLUMN origin_type TEXT NOT NULL DEFAULT 'legacy'",
    "ALTER TABLE cash_movements ADD COLUMN origin_id TEXT",
    "ALTER TABLE cash_movements ADD COLUMN user_id TEXT",
    "ALTER TABLE cash_movements ADD COLUMN user_name TEXT",
    "ALTER TABLE cash_movements ADD COLUMN resulting_balance REAL",
    "ALTER TABLE cash_movements ADD COLUMN reversal_of_id TEXT",
    "ALTER TABLE cash_movements ADD COLUMN reversed_at TEXT",
    "ALTER TABLE cash_movements ADD COLUMN idempotency_key TEXT",
    "ALTER TABLE cash_movements ADD COLUMN request_hash TEXT",
    "ALTER TABLE cash_movements ADD COLUMN response_json TEXT",
    "ALTER TABLE payables ADD COLUMN open_amount REAL",
    "ALTER TABLE payables ADD COLUMN interest REAL NOT NULL DEFAULT 0",
    "ALTER TABLE payables ADD COLUMN fine REAL NOT NULL DEFAULT 0",
    "ALTER TABLE payables ADD COLUMN recurring INTEGER NOT NULL DEFAULT 0",
    "ALTER TABLE payables ADD COLUMN recurring_day INTEGER",
    "ALTER TABLE payables ADD COLUMN recurring_series_id TEXT",
    "ALTER TABLE payables ADD COLUMN recurrence_month TEXT",
    "ALTER TABLE payables ADD COLUMN generated_from_id TEXT",
    "ALTER TABLE payables ADD COLUMN version INTEGER NOT NULL DEFAULT 0",
    "ALTER TABLE payables ADD COLUMN cancelled_at TEXT",
    "ALTER TABLE payables ADD COLUMN cancellation_reason TEXT",
    "ALTER TABLE payables ADD COLUMN cancelled_by_id TEXT",
    "ALTER TABLE payables ADD COLUMN cancelled_by_name TEXT",
)

TABLE_STATEMENTS = (
    """
    CREATE TABLE payable_payments (
        id TEXT PRIMARY KEY,
        store_id TEXT NOT NULL,
        payable_id TEXT NOT NULL,
        cash_movement_id TEXT,
        amount REAL NOT NULL,
        interest_amount REAL NOT NULL DEFAULT 0,
        fine_amount REAL NOT NULL DEFAULT 0,
        discount_amount REAL NOT NULL DEFAULT 0,
        method TEXT NOT NULL,
        note TEXT,
        status TEXT NOT NULL DEFAULT 'active',
        reversal_cash_movement_id TEXT,
        reversed_at TEXT,
        reversal_reason TEXT,
        reversal_idempotency_key TEXT,
        reversal_request_hash TEXT,
        reversal_response_json TEXT,
        user_id TEXT,
        user_name TEXT,
        idempotency_key TEXT NOT NULL,
        request_hash TEXT NOT NULL,
        response_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (store_id) REFERENCES stores(id),
        FOREIGN KEY (payable_id) REFERENCES payables(id),
        FOREIGN KEY (cash_movement_id) REFERENCES cash_movements(id),
        CHECK (amount >= 0),
        CHECK (interest_amount >= 0),
        CHECK (fine_amount >= 0),
        CHECK (discount_amount >= 0),
        CHECK (method IN ('cash', 'pix', 'debit')),
        CHECK (status IN ('active', 'reversed'))
    )
    """,
    """
    CREATE TABLE payable_events (
        id TEXT PRIMARY KEY,
        store_id TEXT NOT NULL,
        payable_id TEXT NOT NULL,
        event_type TEXT NOT NULL,
        payment_id TEXT,
        previous_status TEXT,
        new_status TEXT,
        details_json TEXT NOT NULL,
        user_id TEXT,
        user_name TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (store_id) REFERENCES stores(id),
        FOREIGN KEY (payable_id) REFERENCES payables(id),
        CHECK (event_type IN ('created', 'updated', 'payment', 'payment_reversal', 'cancelled', 'recurrence'))
    )
    """,
    """
    CREATE TABLE bank_receipts (
        id TEXT PRIMARY KEY,
        store_id TEXT NOT NULL,
        description TEXT NOT NULL,
        credit_amount REAL NOT NULL DEFAULT 0,
        debit_amount REAL NOT NULL DEFAULT 0,
        total_amount REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'registered',
        user_id TEXT,
        user_name TEXT,
        idempotency_key TEXT NOT NULL,
        request_hash TEXT NOT NULL,
        response_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (store_id) REFERENCES stores(id),
        CHECK (credit_amount >= 0),
        CHECK (debit_amount >= 0),
        CHECK (total_amount > 0),
        CHECK (status IN ('registered', 'reversed'))
    )
    """,
    """
    CREATE TABLE sale_cancellations (
        id TEXT PRIMARY KEY,
        store_id TEXT NOT NULL,
        sale_id TEXT NOT NULL,
        return_id TEXT NOT NULL,
        reason TEXT NOT NULL,
        reconciliation_required INTEGER NOT NULL DEFAULT 0,
        user_id TEXT,
        user_name TEXT,
        idempotency_key TEXT NOT NULL,
        request_hash TEXT NOT NULL,
        response_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (store_id) REFERENCES stores(id),
        FOREIGN KEY (sale_id) REFERENCES sales(id),
        FOREIGN KEY (return_id) REFERENCES sale_returns(id),
        UNIQUE (sale_id),
        CHECK (reason <> '')
    )
    """,
)

INDEX_STATEMENTS = (
    "CREATE UNIQUE INDEX idx_cash_store_idempotency ON cash_movements(store_id, idempotency_key) WHERE idempotency_key IS NOT NULL",
    "CREATE UNIQUE INDEX idx_cash_reversal_once ON cash_movements(reversal_of_id) WHERE reversal_of_id IS NOT NULL",
    "CREATE INDEX idx_cash_origin ON cash_movements(store_id, origin_type, origin_id)",
    "CREATE UNIQUE INDEX idx_payable_payments_store_key ON payable_payments(store_id, idempotency_key)",
    "CREATE UNIQUE INDEX idx_payable_payment_reversal_key ON payable_payments(store_id, reversal_idempotency_key) WHERE reversal_idempotency_key IS NOT NULL",
    "CREATE INDEX idx_payable_payments_payable ON payable_payments(store_id, payable_id, created_at)",
    "CREATE INDEX idx_payable_events_payable ON payable_events(store_id, payable_id, created_at)",
    "CREATE UNIQUE INDEX idx_payables_recurrence_month ON payables(store_id, recurring_series_id, recurrence_month) WHERE recurring_series_id IS NOT NULL AND recurrence_month IS NOT NULL",
    "CREATE UNIQUE INDEX idx_bank_receipts_store_key ON bank_receipts(store_id, idempotency_key)",
    "CREATE UNIQUE INDEX idx_sale_cancellations_store_key ON sale_cancellations(store_id, idempotency_key)",
    "CREATE UNIQUE INDEX idx_sale_cancellations_sale ON sale_cancellations(sale_id)",
)


MIGRATION_014 = Migration(
    version=14,
    description="Add continuous financial ledger and traceable reversals",
    sqlite_statements=(*ALTER_STATEMENTS, *TABLE_STATEMENTS, *INDEX_STATEMENTS),
    postgresql_statements=(*ALTER_STATEMENTS, *TABLE_STATEMENTS, *INDEX_STATEMENTS),
    code_id="mova-sports-financial-ledger-v14",
)
