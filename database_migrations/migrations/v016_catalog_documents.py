from __future__ import annotations

from ..models import Migration


TABLE_STATEMENTS = (
    """
    CREATE TABLE generated_documents (
        id TEXT PRIMARY KEY,
        store_id TEXT NOT NULL,
        document_type TEXT NOT NULL,
        source_type TEXT NOT NULL,
        source_id TEXT,
        operation_number TEXT,
        format TEXT NOT NULL,
        template_version TEXT NOT NULL,
        copy_number INTEGER NOT NULL DEFAULT 1,
        filename TEXT NOT NULL,
        snapshot_json TEXT NOT NULL,
        generated_by_id TEXT,
        generated_by_name TEXT,
        idempotency_key TEXT NOT NULL,
        request_hash TEXT NOT NULL,
        generated_at TEXT NOT NULL,
        FOREIGN KEY (store_id) REFERENCES stores(id),
        CHECK (
            document_type IN (
                'sale_receipt',
                'conditional',
                'exchange',
                'catalog',
                'product_labels'
            )
        ),
        CHECK (
            source_type IN (
                'sale',
                'conditional',
                'exchange',
                'catalog',
                'product'
            )
        ),
        CHECK (format IN ('a4', 'thermal')),
        CHECK (copy_number > 0),
        CHECK (filename <> ''),
        CHECK (template_version <> '')
    )
    """,
)

INDEX_STATEMENTS = (
    "CREATE UNIQUE INDEX idx_generated_documents_store_key ON generated_documents(store_id, idempotency_key)",
    "CREATE INDEX idx_generated_documents_source ON generated_documents(store_id, source_type, source_id, document_type, generated_at)",
    "CREATE INDEX idx_generated_documents_store_created ON generated_documents(store_id, generated_at)",
)


MIGRATION_016 = Migration(
    version=16,
    description="Add authoritative catalog document snapshots",
    sqlite_statements=(*TABLE_STATEMENTS, *INDEX_STATEMENTS),
    postgresql_statements=(*TABLE_STATEMENTS, *INDEX_STATEMENTS),
    code_id="mova-sports-catalog-documents-v16",
)
