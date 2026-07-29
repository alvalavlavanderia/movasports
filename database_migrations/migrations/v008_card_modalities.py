from __future__ import annotations

from ..models import Migration


TABLE_STATEMENTS = (
    """
    CREATE TABLE card_modalities (
        id TEXT PRIMARY KEY,
        store_id TEXT NOT NULL,
        name TEXT NOT NULL,
        method TEXT NOT NULL,
        installments INTEGER NOT NULL DEFAULT 1,
        status TEXT NOT NULL DEFAULT 'active',
        tax_percent REAL NOT NULL DEFAULT 0,
        receivable_days INTEGER NOT NULL DEFAULT 1,
        valid_from TEXT NOT NULL,
        valid_until TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (store_id) REFERENCES stores(id),
        CHECK (method IN ('debit', 'credit')),
        CHECK (status IN ('active', 'inactive')),
        CHECK (installments >= 1 AND installments <= 10),
        CHECK (tax_percent >= 0),
        CHECK (receivable_days >= 0),
        UNIQUE (store_id, method, installments)
    )
    """,
)

INDEX_STATEMENTS = (
    "CREATE INDEX idx_card_modalities_store_status ON card_modalities(store_id, status)",
    "CREATE INDEX idx_card_modalities_store_method_installments ON card_modalities(store_id, method, installments)",
)


MIGRATION_008 = Migration(
    version=8,
    description="Add card payment modalities",
    sqlite_statements=(*TABLE_STATEMENTS, *INDEX_STATEMENTS),
    postgresql_statements=(*TABLE_STATEMENTS, *INDEX_STATEMENTS),
    code_id="mova-sports-card-modalities-v8",
)
