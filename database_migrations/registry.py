from __future__ import annotations

from collections.abc import Iterable

from .migrations.v001_create_current_schema import MIGRATION_001
from .migrations.v002_customer_business_rules import MIGRATION_002
from .migrations.v003_supplier_auxiliary_catalogs import MIGRATION_003
from .migrations.v004_product_stock_entries import MIGRATION_004
from .migrations.v005_purchase_financial_flows import MIGRATION_005
from .migrations.v006_transactional_inventory import MIGRATION_006
from .migrations.v007_inventory_counts import MIGRATION_007
from .migrations.v008_card_modalities import MIGRATION_008
from .migrations.v009_card_modality_history import MIGRATION_009
from .migrations.v010_transactional_sales import MIGRATION_010
from .migrations.v011_store_credit_business_rules import MIGRATION_011
from .migrations.v012_transactional_conditionals import MIGRATION_012
from .migrations.v013_returns_exchanges_warranties import MIGRATION_013
from .migrations.v014_financial_ledger import MIGRATION_014
from .migrations.v015_card_reconciliation import MIGRATION_015
from .migrations.v016_catalog_documents import MIGRATION_016
from .migrations.v017_alert_user_states import MIGRATION_017
from .migrations.v018_store_settings_and_user_security import MIGRATION_018
from .models import Migration, validate_registry


MIGRATIONS = validate_registry(
    (
        MIGRATION_001,
        MIGRATION_002,
        MIGRATION_003,
        MIGRATION_004,
        MIGRATION_005,
        MIGRATION_006,
        MIGRATION_007,
        MIGRATION_008,
        MIGRATION_009,
        MIGRATION_010,
        MIGRATION_011,
        MIGRATION_012,
        MIGRATION_013,
        MIGRATION_014,
        MIGRATION_015,
        MIGRATION_016,
        MIGRATION_017,
        MIGRATION_018,
    )
)


def get_registry(migrations: Iterable[Migration] | None = None) -> tuple[Migration, ...]:
    return validate_registry(MIGRATIONS if migrations is None else migrations)
