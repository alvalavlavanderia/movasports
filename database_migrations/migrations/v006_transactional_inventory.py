from __future__ import annotations

from ..models import Migration


TABLE_STATEMENTS = (
    """
    CREATE TABLE inventory_movements (
        id TEXT PRIMARY KEY,
        store_id TEXT NOT NULL,
        product_id TEXT NOT NULL,
        product_name TEXT NOT NULL,
        barcode TEXT NOT NULL,
        movement_type TEXT NOT NULL,
        direction TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        real_delta INTEGER NOT NULL DEFAULT 0,
        reserved_delta INTEGER NOT NULL DEFAULT 0,
        real_before INTEGER NOT NULL,
        real_after INTEGER NOT NULL,
        reserved_before INTEGER NOT NULL,
        reserved_after INTEGER NOT NULL,
        available_before INTEGER NOT NULL,
        available_after INTEGER NOT NULL,
        reference_type TEXT NOT NULL,
        reference_id TEXT NOT NULL,
        source_key TEXT NOT NULL,
        user_id TEXT,
        user_name TEXT,
        notes TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (store_id) REFERENCES stores(id),
        CHECK (direction IN ('in', 'out', 'reserve', 'release')),
        CHECK (quantity > 0),
        CHECK (real_before >= 0),
        CHECK (real_after >= 0),
        CHECK (reserved_before >= 0),
        CHECK (reserved_after >= 0),
        CHECK (available_before >= 0),
        CHECK (available_after >= 0),
        CHECK (real_after = real_before + real_delta),
        CHECK (reserved_after = reserved_before + reserved_delta),
        CHECK (available_before = real_before - reserved_before),
        CHECK (available_after = real_after - reserved_after),
        CHECK (real_delta <> 0 OR reserved_delta <> 0)
    )
    """,
)

INDEX_STATEMENTS = (
    "CREATE UNIQUE INDEX idx_inventory_movements_store_source ON inventory_movements(store_id, source_key)",
    "CREATE INDEX idx_inventory_movements_product_created ON inventory_movements(store_id, product_id, created_at)",
    "CREATE INDEX idx_inventory_movements_reference ON inventory_movements(store_id, reference_type, reference_id)",
    "CREATE INDEX idx_inventory_movements_type_created ON inventory_movements(store_id, movement_type, created_at)",
)

SQLITE_BACKFILL = (
    """
    INSERT INTO inventory_movements (
        id, store_id, product_id, product_name, barcode,
        movement_type, direction, quantity,
        real_delta, reserved_delta, real_before, real_after,
        reserved_before, reserved_after, available_before, available_after,
        reference_type, reference_id, source_key, user_id, user_name, notes,
        created_at
    )
    SELECT
        'opening:' || store_id || ':' || id,
        store_id,
        id,
        name,
        COALESCE(barcode, ''),
        'opening_balance',
        'in',
        stock,
        stock,
        0,
        0,
        stock,
        0,
        0,
        0,
        stock,
        'migration_snapshot',
        id,
        'opening:' || id,
        NULL,
        'Migration v006',
        'Saldo real existente na ativacao do ledger transacional.',
        strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
    FROM products
    WHERE stock > 0
      AND NOT EXISTS (
          SELECT 1
          FROM inventory_movements movement
          WHERE movement.store_id = products.store_id
            AND movement.source_key = 'opening:' || products.id
      )
    """,
)

POSTGRESQL_BACKFILL = (
    """
    INSERT INTO inventory_movements (
        id, store_id, product_id, product_name, barcode,
        movement_type, direction, quantity,
        real_delta, reserved_delta, real_before, real_after,
        reserved_before, reserved_after, available_before, available_after,
        reference_type, reference_id, source_key, user_id, user_name, notes,
        created_at
    )
    SELECT
        'opening:' || store_id || ':' || id,
        store_id,
        id,
        name,
        COALESCE(barcode, ''),
        'opening_balance',
        'in',
        stock,
        stock,
        0,
        0,
        stock,
        0,
        0,
        0,
        stock,
        'migration_snapshot',
        id,
        'opening:' || id,
        NULL,
        'Migration v006',
        'Saldo real existente na ativacao do ledger transacional.',
        CURRENT_TIMESTAMP::TEXT
    FROM products
    WHERE stock > 0
      AND NOT EXISTS (
          SELECT 1
          FROM inventory_movements movement
          WHERE movement.store_id = products.store_id
            AND movement.source_key = 'opening:' || products.id
      )
    """,
)


MIGRATION_006 = Migration(
    version=6,
    description="Add transactional inventory ledger",
    sqlite_statements=(
        *TABLE_STATEMENTS,
        *INDEX_STATEMENTS,
        *SQLITE_BACKFILL,
    ),
    postgresql_statements=(
        *TABLE_STATEMENTS,
        *INDEX_STATEMENTS,
        *POSTGRESQL_BACKFILL,
    ),
    code_id="mova-sports-transactional-inventory-ledger-v6",
)
