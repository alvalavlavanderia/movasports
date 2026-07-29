from __future__ import annotations

from ..models import Migration


TABLE_STATEMENTS = (
    """
    CREATE TABLE store_settings (
        store_id TEXT PRIMARY KEY,
        legal_name TEXT,
        trade_name TEXT,
        document TEXT,
        document_type TEXT,
        phone TEXT,
        whatsapp TEXT,
        email TEXT,
        zip TEXT,
        address TEXT,
        address_number TEXT,
        complement TEXT,
        district TEXT,
        city TEXT,
        state TEXT,
        logo_url TEXT,
        print_show_document INTEGER NOT NULL DEFAULT 1,
        print_show_phone INTEGER NOT NULL DEFAULT 1,
        print_show_whatsapp INTEGER NOT NULL DEFAULT 1,
        print_show_address INTEGER NOT NULL DEFAULT 1,
        print_show_email INTEGER NOT NULL DEFAULT 1,
        receipt_footer TEXT,
        pix_key TEXT,
        pix_key_type TEXT,
        pix_recipient_name TEXT,
        pix_recipient_document TEXT,
        pix_bank TEXT,
        pix_enabled INTEGER NOT NULL DEFAULT 1,
        debit_enabled INTEGER NOT NULL DEFAULT 1,
        credit_enabled INTEGER NOT NULL DEFAULT 1,
        store_credit_enabled INTEGER NOT NULL DEFAULT 1,
        version INTEGER NOT NULL DEFAULT 1,
        updated_by_id TEXT,
        updated_by_name TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (store_id) REFERENCES stores(id)
    )
    """,
    """
    CREATE TABLE user_preferences (
        id TEXT PRIMARY KEY,
        store_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        theme TEXT NOT NULL DEFAULT 'system',
        version INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (store_id) REFERENCES stores(id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        CHECK (theme IN ('light', 'dark', 'system'))
    )
    """,
)

USER_COLUMNS = (
    "ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER NOT NULL DEFAULT 0",
    "ALTER TABLE users ADD COLUMN blocked_at TEXT",
    "ALTER TABLE users ADD COLUMN last_login_at TEXT",
)

INDEX_STATEMENTS = (
    "CREATE UNIQUE INDEX idx_user_preferences_identity ON user_preferences(store_id, user_id)",
    "CREATE INDEX idx_store_settings_updated ON store_settings(updated_at)",
)


MIGRATION_018 = Migration(
    version=18,
    description="Add versioned store settings, user preferences and login blocking state",
    sqlite_statements=(*TABLE_STATEMENTS, *USER_COLUMNS, *INDEX_STATEMENTS),
    postgresql_statements=(*TABLE_STATEMENTS, *USER_COLUMNS, *INDEX_STATEMENTS),
    code_id="mova-sports-store-settings-user-security-v18",
)
