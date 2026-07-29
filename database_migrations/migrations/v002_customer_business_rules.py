from __future__ import annotations

from ..models import Migration


CUSTOMER_COLUMNS = (
    "ALTER TABLE customers ADD COLUMN address_number TEXT",
    "ALTER TABLE customers ADD COLUMN state TEXT",
    "ALTER TABLE customers ADD COLUMN notes TEXT",
    "ALTER TABLE customers ADD COLUMN is_default INTEGER NOT NULL DEFAULT 0",
    "ALTER TABLE customers ADD COLUMN created_at TEXT",
)

CUSTOMER_HISTORY_TABLES = (
    """
    CREATE TABLE customer_status_history (
        id TEXT PRIMARY KEY,
        store_id TEXT NOT NULL,
        customer_id TEXT NOT NULL,
        previous_status TEXT NOT NULL,
        new_status TEXT NOT NULL,
        reason TEXT,
        user_id TEXT,
        user_name TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (store_id) REFERENCES stores(id),
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )
    """,
    """
    CREATE TABLE customer_credit_limit_history (
        id TEXT PRIMARY KEY,
        store_id TEXT NOT NULL,
        customer_id TEXT NOT NULL,
        previous_limit REAL NOT NULL,
        new_limit REAL NOT NULL,
        user_id TEXT,
        user_name TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (store_id) REFERENCES stores(id),
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )
    """,
    "CREATE INDEX idx_customer_status_history_customer ON customer_status_history(store_id, customer_id, created_at)",
    "CREATE INDEX idx_customer_limit_history_customer ON customer_credit_limit_history(store_id, customer_id, created_at)",
    "CREATE UNIQUE INDEX idx_customers_store_default ON customers(store_id) WHERE is_default = 1",
)

SQLITE_DEFAULT_CUSTOMER = """
    INSERT INTO customers (
        id, store_id, code, name, cpf, rg, birth, whatsapp, email, address,
        city, district, zip, credit_limit, status, updated_at, address_number,
        state, notes, is_default, created_at
    )
    SELECT
        stores.id || ':customer:default', stores.id, 'PADRAO', 'Cliente padrao',
        '', '', '', '', '', '', '', '', '', 0, 'active',
        strftime('%Y-%m-%dT%H:%M:%fZ', 'now'), '', '', '', 1,
        strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
    FROM stores
    WHERE NOT EXISTS (
        SELECT 1 FROM customers
        WHERE customers.store_id = stores.id AND customers.is_default = 1
    )
      AND NOT EXISTS (
        SELECT 1 FROM customers
        WHERE customers.id = stores.id || ':customer:default'
    )
"""

POSTGRESQL_DEFAULT_CUSTOMER = """
    INSERT INTO customers (
        id, store_id, code, name, cpf, rg, birth, whatsapp, email, address,
        city, district, zip, credit_limit, status, updated_at, address_number,
        state, notes, is_default, created_at
    )
    SELECT
        stores.id || ':customer:default', stores.id, 'PADRAO', 'Cliente padrao',
        '', '', '', '', '', '', '', '', '', 0, 'active',
        CURRENT_TIMESTAMP::text, '', '', '', 1, CURRENT_TIMESTAMP::text
    FROM stores
    WHERE NOT EXISTS (
        SELECT 1 FROM customers
        WHERE customers.store_id = stores.id AND customers.is_default = 1
    )
      AND NOT EXISTS (
        SELECT 1 FROM customers
        WHERE customers.id = stores.id || ':customer:default'
    )
"""

SQLITE_ADOPT_DEFAULT_CUSTOMER = """
    UPDATE customers
    SET is_default = 1,
        created_at = COALESCE(NULLIF(created_at, ''), updated_at)
    WHERE id = store_id || ':customer:default'
"""

POSTGRESQL_ADOPT_DEFAULT_CUSTOMER = """
    UPDATE customers
    SET is_default = 1,
        created_at = COALESCE(NULLIF(created_at, ''), updated_at)
    WHERE id = store_id || ':customer:default'
"""


MIGRATION_002 = Migration(
    version=2,
    description="Add customer business rules",
    sqlite_statements=(
        *CUSTOMER_COLUMNS,
        *CUSTOMER_HISTORY_TABLES,
        SQLITE_ADOPT_DEFAULT_CUSTOMER,
        SQLITE_DEFAULT_CUSTOMER,
    ),
    postgresql_statements=(
        *CUSTOMER_COLUMNS,
        *CUSTOMER_HISTORY_TABLES,
        POSTGRESQL_ADOPT_DEFAULT_CUSTOMER,
        POSTGRESQL_DEFAULT_CUSTOMER,
    ),
    code_id="mova-sports-customer-business-rules-v2",
)
