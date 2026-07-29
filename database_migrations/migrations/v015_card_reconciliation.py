from __future__ import annotations

from ..models import Migration


ALTER_STATEMENTS = (
    "ALTER TABLE receivables ADD COLUMN difference_amount REAL NOT NULL DEFAULT 0",
    "ALTER TABLE receivable_payments ADD COLUMN reconciliation_id TEXT",
    "ALTER TABLE receivable_payments ADD COLUMN status TEXT NOT NULL DEFAULT 'active'",
    "ALTER TABLE receivable_payments ADD COLUMN reversed_at TEXT",
    "ALTER TABLE receivable_payments ADD COLUMN reversal_reason TEXT",
)

TABLE_STATEMENTS = (
    """
    CREATE TABLE card_reconciliations (
        id TEXT PRIMARY KEY,
        store_id TEXT NOT NULL,
        receipt_date TEXT NOT NULL,
        total_received REAL NOT NULL,
        item_count INTEGER NOT NULL,
        note TEXT,
        status TEXT NOT NULL DEFAULT 'active',
        cash_movement_id TEXT NOT NULL,
        reversal_cash_movement_id TEXT,
        user_id TEXT,
        user_name TEXT,
        idempotency_key TEXT NOT NULL,
        request_hash TEXT NOT NULL,
        response_json TEXT NOT NULL,
        reversed_at TEXT,
        reversal_reason TEXT,
        reversed_by_id TEXT,
        reversed_by_name TEXT,
        reversal_idempotency_key TEXT,
        reversal_request_hash TEXT,
        reversal_response_json TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (store_id) REFERENCES stores(id),
        FOREIGN KEY (cash_movement_id) REFERENCES cash_movements(id),
        FOREIGN KEY (reversal_cash_movement_id) REFERENCES cash_movements(id),
        CHECK (total_received > 0),
        CHECK (item_count > 0),
        CHECK (status IN ('active', 'reversed'))
    )
    """,
    """
    CREATE TABLE card_reconciliation_items (
        id TEXT PRIMARY KEY,
        store_id TEXT NOT NULL,
        reconciliation_id TEXT NOT NULL,
        receivable_id TEXT NOT NULL,
        payment_id TEXT NOT NULL,
        sale_id TEXT,
        method TEXT NOT NULL,
        modality_name TEXT,
        expected_balance_before REAL NOT NULL,
        allocated_amount REAL NOT NULL,
        close_with_divergence INTEGER NOT NULL DEFAULT 0,
        divergence_note TEXT,
        difference_after REAL NOT NULL DEFAULT 0,
        difference_before REAL NOT NULL DEFAULT 0,
        received_before REAL NOT NULL,
        received_after REAL NOT NULL,
        open_amount_before REAL NOT NULL,
        open_amount_after REAL NOT NULL,
        status_before TEXT NOT NULL,
        status_after TEXT NOT NULL,
        version_before INTEGER NOT NULL,
        version_after INTEGER NOT NULL,
        paid_at_before TEXT,
        last_payment_at_before TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (store_id) REFERENCES stores(id),
        FOREIGN KEY (reconciliation_id) REFERENCES card_reconciliations(id),
        FOREIGN KEY (receivable_id) REFERENCES receivables(id),
        FOREIGN KEY (payment_id) REFERENCES receivable_payments(id),
        CHECK (expected_balance_before >= 0),
        CHECK (allocated_amount >= 0),
        CHECK (received_before >= 0),
        CHECK (received_after >= 0),
        CHECK (open_amount_before >= 0),
        CHECK (open_amount_after >= 0),
        CHECK (version_after = version_before + 1)
    )
    """,
)

INDEX_STATEMENTS = (
    "CREATE UNIQUE INDEX idx_card_reconciliations_store_key ON card_reconciliations(store_id, idempotency_key)",
    "CREATE UNIQUE INDEX idx_card_reconciliation_reversal_key ON card_reconciliations(store_id, reversal_idempotency_key) WHERE reversal_idempotency_key IS NOT NULL",
    "CREATE INDEX idx_card_reconciliations_store_date ON card_reconciliations(store_id, receipt_date, created_at)",
    "CREATE INDEX idx_card_reconciliation_items_group ON card_reconciliation_items(reconciliation_id, created_at)",
    "CREATE INDEX idx_card_reconciliation_items_receivable ON card_reconciliation_items(store_id, receivable_id, created_at)",
    "CREATE INDEX idx_receivable_payments_reconciliation ON receivable_payments(reconciliation_id)",
)


MIGRATION_015 = Migration(
    version=15,
    description="Add traceable card receivable reconciliation",
    sqlite_statements=(*ALTER_STATEMENTS, *TABLE_STATEMENTS, *INDEX_STATEMENTS),
    postgresql_statements=(*ALTER_STATEMENTS, *TABLE_STATEMENTS, *INDEX_STATEMENTS),
    code_id="mova-sports-card-reconciliation-v15",
)
