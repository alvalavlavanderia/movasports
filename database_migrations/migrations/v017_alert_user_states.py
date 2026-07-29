from __future__ import annotations

from ..models import Migration


TABLE_STATEMENTS = (
    """
    CREATE TABLE alert_user_states (
        id TEXT PRIMARY KEY,
        store_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        alert_id TEXT NOT NULL,
        read_at TEXT,
        pinned_at TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (store_id) REFERENCES stores(id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """,
)

INDEX_STATEMENTS = (
    "CREATE UNIQUE INDEX idx_alert_user_states_identity ON alert_user_states(store_id, user_id, alert_id)",
    "CREATE INDEX idx_alert_user_states_user_updated ON alert_user_states(store_id, user_id, updated_at)",
)


MIGRATION_017 = Migration(
    version=17,
    description="Add per-user state for active operational alerts",
    sqlite_statements=(*TABLE_STATEMENTS, *INDEX_STATEMENTS),
    postgresql_statements=(*TABLE_STATEMENTS, *INDEX_STATEMENTS),
    code_id="mova-sports-alert-user-states-v17",
)
