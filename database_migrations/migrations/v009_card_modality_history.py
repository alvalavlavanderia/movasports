from __future__ import annotations

from ..models import Migration


ALTER_STATEMENTS = (
    "ALTER TABLE card_modalities ADD COLUMN card_modality_id TEXT NOT NULL DEFAULT ''",
    "UPDATE card_modalities SET card_modality_id = id WHERE card_modality_id = ''",
)

TABLE_STATEMENTS = (
    """
    CREATE TABLE card_modality_history (
        id TEXT PRIMARY KEY,
        card_modality_id TEXT NOT NULL,
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
        CHECK (receivable_days >= 0)
    )
    """,
)

INDEX_STATEMENTS = (
    "CREATE UNIQUE INDEX idx_card_modalities_store_stable_id ON card_modalities(store_id, card_modality_id)",
    "CREATE INDEX idx_card_modality_history_store_modality ON card_modality_history(store_id, card_modality_id)",
    "CREATE INDEX idx_card_modality_history_store_created ON card_modality_history(store_id, created_at)",
)


MIGRATION_009 = Migration(
    version=9,
    description="Add card modality history and stable identifiers",
    sqlite_statements=(*ALTER_STATEMENTS, *TABLE_STATEMENTS, *INDEX_STATEMENTS),
    postgresql_statements=(*ALTER_STATEMENTS, *TABLE_STATEMENTS, *INDEX_STATEMENTS),
    code_id="mova-sports-card-modality-history-v9",
)
