from __future__ import annotations

from ..models import Migration


TABLE_STATEMENTS = (
    """
    CREATE TABLE stock_entry_payables (
        id TEXT PRIMARY KEY,
        store_id TEXT NOT NULL,
        entry_id TEXT NOT NULL,
        payable_id TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (store_id) REFERENCES stores(id),
        FOREIGN KEY (entry_id) REFERENCES stock_entries(id),
        FOREIGN KEY (payable_id) REFERENCES payables(id),
        UNIQUE (entry_id, payable_id)
    )
    """,
    """
    CREATE TABLE stock_entry_cancellations (
        id TEXT PRIMARY KEY,
        store_id TEXT NOT NULL,
        entry_id TEXT NOT NULL,
        reason TEXT NOT NULL,
        notes TEXT,
        idempotency_key TEXT NOT NULL,
        request_hash TEXT NOT NULL,
        response_json TEXT NOT NULL,
        user_id TEXT,
        user_name TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (store_id) REFERENCES stores(id),
        FOREIGN KEY (entry_id) REFERENCES stock_entries(id),
        UNIQUE (entry_id),
        UNIQUE (store_id, idempotency_key)
    )
    """,
    """
    CREATE TABLE purchase_stock_movements (
        id TEXT PRIMARY KEY,
        store_id TEXT NOT NULL,
        product_id TEXT NOT NULL,
        movement_type TEXT NOT NULL,
        direction TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        balance_before INTEGER NOT NULL,
        balance_after INTEGER NOT NULL,
        reference_type TEXT NOT NULL,
        reference_id TEXT NOT NULL,
        user_id TEXT,
        user_name TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (store_id) REFERENCES stores(id),
        FOREIGN KEY (product_id) REFERENCES products(id),
        CHECK (movement_type IN ('entry_cancellation', 'supplier_return', 'supplier_return_cancellation')),
        CHECK (direction IN ('in', 'out')),
        CHECK (quantity > 0),
        CHECK (balance_before >= 0),
        CHECK (balance_after >= 0)
    )
    """,
    """
    CREATE TABLE supplier_return_sequences (
        store_id TEXT PRIMARY KEY,
        next_number INTEGER NOT NULL DEFAULT 1,
        FOREIGN KEY (store_id) REFERENCES stores(id),
        CHECK (next_number > 0)
    )
    """,
    """
    CREATE TABLE supplier_returns (
        id TEXT PRIMARY KEY,
        store_id TEXT NOT NULL,
        return_number INTEGER NOT NULL,
        entry_id TEXT NOT NULL,
        supplier_id TEXT NOT NULL,
        supplier_name TEXT NOT NULL,
        reason TEXT NOT NULL,
        notes TEXT,
        total_quantity INTEGER NOT NULL,
        total_value REAL NOT NULL,
        pending_value REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'confirmed',
        financial_status TEXT NOT NULL DEFAULT 'pending',
        idempotency_key TEXT NOT NULL,
        request_hash TEXT NOT NULL,
        response_json TEXT NOT NULL,
        user_id TEXT,
        user_name TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (store_id) REFERENCES stores(id),
        FOREIGN KEY (entry_id) REFERENCES stock_entries(id),
        FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
        CHECK (return_number > 0),
        CHECK (total_quantity > 0),
        CHECK (total_value > 0),
        CHECK (pending_value >= 0),
        CHECK (status IN ('confirmed', 'cancelled')),
        CHECK (financial_status IN ('pending', 'partial', 'settled'))
    )
    """,
    """
    CREATE TABLE supplier_return_items (
        id TEXT PRIMARY KEY,
        return_id TEXT NOT NULL,
        entry_item_id TEXT NOT NULL,
        product_id TEXT NOT NULL,
        product_name TEXT NOT NULL,
        barcode TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        unit_cost REAL NOT NULL,
        total_cost REAL NOT NULL,
        stock_before INTEGER NOT NULL,
        stock_after INTEGER NOT NULL,
        FOREIGN KEY (return_id) REFERENCES supplier_returns(id),
        FOREIGN KEY (entry_item_id) REFERENCES stock_entry_items(id),
        FOREIGN KEY (product_id) REFERENCES products(id),
        CHECK (quantity > 0),
        CHECK (unit_cost > 0),
        CHECK (total_cost > 0),
        CHECK (stock_before >= 0),
        CHECK (stock_after >= 0)
    )
    """,
    """
    CREATE TABLE supplier_credits (
        id TEXT PRIMARY KEY,
        store_id TEXT NOT NULL,
        supplier_id TEXT NOT NULL,
        supplier_name TEXT NOT NULL,
        return_id TEXT NOT NULL,
        original_amount REAL NOT NULL,
        used_amount REAL NOT NULL DEFAULT 0,
        status TEXT NOT NULL DEFAULT 'available',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (store_id) REFERENCES stores(id),
        FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
        FOREIGN KEY (return_id) REFERENCES supplier_returns(id),
        CHECK (original_amount > 0),
        CHECK (used_amount >= 0),
        CHECK (used_amount <= original_amount),
        CHECK (status IN ('available', 'partially_used', 'used', 'reversed'))
    )
    """,
    """
    CREATE TABLE supplier_return_allocations (
        id TEXT PRIMARY KEY,
        store_id TEXT NOT NULL,
        return_id TEXT NOT NULL,
        allocation_type TEXT NOT NULL,
        payable_id TEXT,
        credit_id TEXT,
        cash_movement_id TEXT,
        amount REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'active',
        created_at TEXT NOT NULL,
        FOREIGN KEY (store_id) REFERENCES stores(id),
        FOREIGN KEY (return_id) REFERENCES supplier_returns(id),
        FOREIGN KEY (payable_id) REFERENCES payables(id),
        FOREIGN KEY (credit_id) REFERENCES supplier_credits(id),
        FOREIGN KEY (cash_movement_id) REFERENCES cash_movements(id),
        CHECK (allocation_type IN ('payable_abatement', 'supplier_credit', 'cash_refund', 'pix_refund')),
        CHECK (amount > 0),
        CHECK (status IN ('active', 'reversed'))
    )
    """,
    """
    CREATE TABLE supplier_credit_usages (
        id TEXT PRIMARY KEY,
        store_id TEXT NOT NULL,
        supplier_id TEXT NOT NULL,
        payable_id TEXT NOT NULL,
        amount REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'active',
        idempotency_key TEXT NOT NULL,
        request_hash TEXT NOT NULL,
        response_json TEXT NOT NULL,
        user_id TEXT,
        user_name TEXT,
        created_at TEXT NOT NULL,
        reversed_at TEXT,
        FOREIGN KEY (store_id) REFERENCES stores(id),
        FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
        FOREIGN KEY (payable_id) REFERENCES payables(id),
        CHECK (amount > 0),
        CHECK (status IN ('active', 'reversed')),
        UNIQUE (store_id, idempotency_key)
    )
    """,
    """
    CREATE TABLE supplier_credit_allocations (
        id TEXT PRIMARY KEY,
        usage_id TEXT NOT NULL,
        credit_id TEXT NOT NULL,
        amount REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'active',
        created_at TEXT NOT NULL,
        FOREIGN KEY (usage_id) REFERENCES supplier_credit_usages(id),
        FOREIGN KEY (credit_id) REFERENCES supplier_credits(id),
        CHECK (amount > 0),
        CHECK (status IN ('active', 'reversed'))
    )
    """,
)

INDEX_STATEMENTS = (
    "CREATE INDEX idx_stock_entry_payables_entry ON stock_entry_payables(store_id, entry_id)",
    "CREATE UNIQUE INDEX idx_stock_entry_payables_payable ON stock_entry_payables(payable_id)",
    "CREATE INDEX idx_purchase_stock_movements_reference ON purchase_stock_movements(reference_type, reference_id)",
    "CREATE INDEX idx_purchase_stock_movements_product ON purchase_stock_movements(store_id, product_id, created_at)",
    "CREATE UNIQUE INDEX idx_supplier_returns_store_number ON supplier_returns(store_id, return_number)",
    "CREATE UNIQUE INDEX idx_supplier_returns_store_idempotency ON supplier_returns(store_id, idempotency_key)",
    "CREATE INDEX idx_supplier_returns_entry ON supplier_returns(store_id, entry_id, created_at)",
    "CREATE INDEX idx_supplier_returns_supplier ON supplier_returns(store_id, supplier_id, created_at)",
    "CREATE INDEX idx_supplier_return_items_return ON supplier_return_items(return_id)",
    "CREATE INDEX idx_supplier_return_items_entry_item ON supplier_return_items(entry_item_id)",
    "CREATE INDEX idx_supplier_credits_supplier ON supplier_credits(store_id, supplier_id, created_at)",
    "CREATE INDEX idx_supplier_credits_return ON supplier_credits(return_id)",
    "CREATE INDEX idx_supplier_return_allocations_return ON supplier_return_allocations(return_id)",
    "CREATE INDEX idx_supplier_return_allocations_payable ON supplier_return_allocations(payable_id)",
    "CREATE INDEX idx_supplier_credit_usages_payable ON supplier_credit_usages(store_id, payable_id, created_at)",
    "CREATE INDEX idx_supplier_credit_allocations_usage ON supplier_credit_allocations(usage_id)",
    "CREATE INDEX idx_supplier_credit_allocations_credit ON supplier_credit_allocations(credit_id)",
)


MIGRATION_005 = Migration(
    version=5,
    description="Add purchase financial and supplier return flows",
    sqlite_statements=(*TABLE_STATEMENTS, *INDEX_STATEMENTS),
    postgresql_statements=(*TABLE_STATEMENTS, *INDEX_STATEMENTS),
    code_id="mova-sports-purchase-financial-flows-v5",
)
