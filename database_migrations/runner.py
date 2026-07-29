from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic
from typing import Callable, Mapping

from environment_config import FALSE_VALUES, TRUE_VALUES, VALID_ENVIRONMENTS

from .adapters import (
    AdapterFactory,
    PostgreSQLAdapter,
    SQLiteAdapter,
    open_postgresql_adapter,
    open_sqlite_adapter,
)
from .models import AppliedMigration, Migration
from .registry import get_registry


class MigrationError(RuntimeError):
    def __init__(self, message: str, *, code: str = "migration_error"):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class DatabaseTarget:
    driver: str
    sqlite_path: str = ""
    database_url: str = ""


def resolve_database_target(
    environ: Mapping[str, str] | None = None,
    *,
    sqlite_path: str | None = None,
    database_url: str | None = None,
) -> DatabaseTarget:
    source = os.environ if environ is None else environ
    resolved_url = str(source.get("DATABASE_URL", "") if database_url is None else database_url).strip()
    if resolved_url:
        return DatabaseTarget("postgresql", database_url=resolved_url)
    default_path = str(Path(__file__).resolve().parents[1] / "loja.db")
    resolved_path = str(source.get("MOVA_DB", default_path) if sqlite_path is None else sqlite_path).strip()
    return DatabaseTarget("sqlite", sqlite_path=resolved_path or default_path)


def _raw_migration_flag(environ: Mapping[str, str]) -> bool:
    raw = str(environ.get("MOVA_ALLOW_MIGRATIONS", "") or "").strip().lower()
    if raw in TRUE_VALUES:
        return True
    if raw in FALSE_VALUES:
        return False
    return False


def require_migration_authorization(
    environ: Mapping[str, str] | None = None,
    *,
    confirm_production: bool = False,
    test_mode: bool = False,
) -> str:
    if test_mode:
        return "test"
    source = os.environ if environ is None else environ
    environment = str(source.get("APP_ENV", "") or "").strip().lower()
    if environment not in VALID_ENVIRONMENTS:
        raise MigrationError(
            "APP_ENV deve estar configurada com um ambiente reconhecido.",
            code="environment_not_configured",
        )
    if not _raw_migration_flag(source):
        raise MigrationError(
            "Migrations nao estao autorizadas neste ambiente.",
            code="migrations_not_allowed",
        )
    if environment == "production" and not confirm_production:
        raise MigrationError(
            "Production exige confirmacao administrativa adicional.",
            code="production_confirmation_required",
        )
    return environment


def _default_adapter_factory(
    target: DatabaseTarget,
    *,
    readonly: bool,
    create: bool = False,
) -> SQLiteAdapter | PostgreSQLAdapter:
    if target.driver == "postgresql":
        return open_postgresql_adapter(target.database_url, readonly=readonly)
    return open_sqlite_adapter(target.sqlite_path, readonly=readonly, create=create)


def _open_adapter(
    target: DatabaseTarget,
    *,
    readonly: bool,
    create: bool,
    adapter_factory: AdapterFactory | None,
):
    factory = adapter_factory or _default_adapter_factory
    return factory(target, readonly=readonly, create=create)


def _parse_applied_at(value: object) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    else:
        raise ValueError("Timestamp de migration invalido.")
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("Timestamp de migration sem timezone.")
    return parsed


def validate_history(
    history: list[AppliedMigration],
    registry: tuple[Migration, ...],
) -> tuple[AppliedMigration, ...]:
    known = {migration.version: migration for migration in registry}
    seen: set[int] = set()
    ordered: list[AppliedMigration] = []
    for row in history:
        version = row.version
        if isinstance(version, bool) or not isinstance(version, int) or version <= 0:
            raise MigrationError("Historico possui versao invalida.", code="invalid_history")
        if version in seen:
            raise MigrationError("Historico possui versao duplicada.", code="duplicate_version")
        migration = known.get(version)
        if migration is None:
            raise MigrationError("Banco possui migration futura ou desconhecida.", code="future_version")
        if not isinstance(row.description, str) or row.description != migration.description:
            raise MigrationError("Descricao de migration aplicada diverge do registry.", code="description_mismatch")
        if not isinstance(row.checksum, str) or row.checksum != migration.checksum:
            raise MigrationError("Checksum de migration aplicada diverge do registry.", code="checksum_mismatch")
        if (
            isinstance(row.execution_time_ms, bool)
            or not isinstance(row.execution_time_ms, int)
            or row.execution_time_ms < 0
        ):
            raise MigrationError("Historico possui duracao invalida.", code="invalid_history")
        try:
            _parse_applied_at(row.applied_at)
        except (TypeError, ValueError) as error:
            raise MigrationError("Historico possui applied_at invalido.", code="invalid_history") from error
        seen.add(version)
        ordered.append(row)

    ordered.sort(key=lambda item: int(item.version))
    actual = tuple(int(item.version) for item in ordered)
    expected = tuple(range(1, len(ordered) + 1))
    if actual != expected:
        raise MigrationError("Historico possui lacuna de versoes.", code="version_gap")
    return tuple(ordered)


def _utc_now_text() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _sqlite_file_exists(target: DatabaseTarget) -> bool:
    return target.driver != "sqlite" or Path(target.sqlite_path).is_file()


def _status_from_adapter(adapter, registry: tuple[Migration, ...]) -> dict:
    tables = adapter.table_names()
    if not tables:
        return {
            "ok": True,
            "state": "empty",
            "driver": adapter.driver,
            "current_version": 0,
            "applied": [],
            "pending": [item.version for item in registry],
            "baseline_possible": False,
        }

    if not adapter.history_exists():
        validation = adapter.validate_v1_schema()
        return {
            "ok": validation.compatible,
            "state": "legacy_compatible" if validation.compatible else "legacy_incompatible",
            "driver": adapter.driver,
            "current_version": 0,
            "applied": [],
            "pending": [item.version for item in registry],
            "baseline_possible": validation.compatible,
            "errors": list(validation.errors),
        }

    try:
        history = validate_history(adapter.load_history(), registry)
    except MigrationError as error:
        return {
            "ok": False,
            "state": error.code,
            "driver": adapter.driver,
            "current_version": None,
            "applied": [],
            "pending": [],
            "baseline_possible": False,
            "errors": [str(error)],
        }

    applied_versions = [int(item.version) for item in history]
    pending = [item.version for item in registry if item.version not in applied_versions]
    if history:
        current_version = max(applied_versions)
        if pending and current_version == 1:
            validation = adapter.validate_v1_schema()
        elif pending and current_version == 2:
            validation = adapter.validate_v2_schema()
        elif pending and current_version == 5:
            validation = adapter.validate_v5_schema()
        elif pending and current_version == 6:
            validation = adapter.validate_v6_schema()
        else:
            validation = adapter.validate_current_schema()
        if not validation.compatible:
            return {
                "ok": False,
                "state": "schema_incompatible",
                "driver": adapter.driver,
                "current_version": max(applied_versions),
                "applied": applied_versions,
                "pending": pending,
                "baseline_possible": False,
                "errors": list(validation.errors),
            }
    return {
        "ok": True,
        "state": "up_to_date" if not pending else "pending",
        "driver": adapter.driver,
        "current_version": max(applied_versions, default=0),
        "applied": applied_versions,
        "pending": pending,
        "baseline_possible": False,
    }


def get_migration_status(
    *,
    environ: Mapping[str, str] | None = None,
    sqlite_path: str | None = None,
    database_url: str | None = None,
    migrations=None,
    adapter_factory: AdapterFactory | None = None,
) -> dict:
    registry = get_registry(migrations)
    target = resolve_database_target(
        environ,
        sqlite_path=sqlite_path,
        database_url=database_url,
    )
    if not _sqlite_file_exists(target):
        return {
            "ok": True,
            "state": "database_missing",
            "driver": target.driver,
            "current_version": None,
            "applied": [],
            "pending": [item.version for item in registry],
            "baseline_possible": False,
        }
    adapter = None
    try:
        adapter = _open_adapter(
            target,
            readonly=True,
            create=False,
            adapter_factory=adapter_factory,
        )
        return _status_from_adapter(adapter, registry)
    except Exception as error:
        if isinstance(error, MigrationError):
            raise
        return {
            "ok": False,
            "state": "database_unavailable",
            "driver": target.driver,
            "current_version": None,
            "applied": [],
            "pending": [],
            "baseline_possible": False,
            "errors": ["Nao foi possivel consultar o banco de dados."],
        }
    finally:
        if adapter is not None:
            try:
                adapter.rollback()
            finally:
                adapter.close()


def _ensure_migration_candidate(adapter, registry: tuple[Migration, ...]) -> tuple[AppliedMigration, ...]:
    tables = adapter.table_names()
    has_history = adapter.history_exists()
    if not has_history:
        business_tables = tables - {"schema_migrations"}
        if business_tables:
            raise MigrationError(
                "Banco existente requer baseline explicita ou reparo antes de migrate.",
                code="legacy_database_requires_baseline",
            )
        adapter.create_history_table()
        return ()
    return validate_history(adapter.load_history(), registry)


def run_database_migrations(
    *,
    create_database: bool = False,
    confirm_production: bool = False,
    environ: Mapping[str, str] | None = None,
    sqlite_path: str | None = None,
    database_url: str | None = None,
    migrations=None,
    adapter_factory: AdapterFactory | None = None,
    test_mode: bool = False,
) -> dict:
    environment = require_migration_authorization(
        environ,
        confirm_production=confirm_production,
        test_mode=test_mode,
    )
    registry = get_registry(migrations)
    target = resolve_database_target(
        environ,
        sqlite_path=sqlite_path,
        database_url=database_url,
    )
    existed = _sqlite_file_exists(target)
    if target.driver == "sqlite" and not existed and not create_database:
        raise MigrationError(
            "Banco SQLite ausente. Use --create para cria-lo explicitamente.",
            code="database_missing",
        )

    if existed:
        status = get_migration_status(
            environ=environ,
            sqlite_path=sqlite_path,
            database_url=database_url,
            migrations=registry,
            adapter_factory=adapter_factory,
        )
        if status["state"] in {"legacy_compatible", "legacy_incompatible"}:
            raise MigrationError(
                "Banco legado nao pode ser migrado sem baseline explicita e valida.",
                code="legacy_database_requires_baseline",
            )
        if not status["ok"]:
            raise MigrationError(status.get("errors", ["Historico invalido."])[0], code=status["state"])
        if not status["pending"]:
            return {
                "ok": True,
                "environment": environment,
                "driver": target.driver,
                "applied": [],
                "current_version": status["current_version"],
                "message": "Nenhuma migration pendente.",
            }

    adapter = None
    applied_now: list[int] = []
    try:
        adapter = _open_adapter(
            target,
            readonly=False,
            create=bool(target.driver == "sqlite" and not existed and create_database),
            adapter_factory=adapter_factory,
        )
        for migration in registry:
            adapter.begin_write()
            try:
                adapter.acquire_migration_lock()
                history = _ensure_migration_candidate(adapter, registry)
                applied_versions = {int(item.version) for item in history}
                if migration.version in applied_versions:
                    adapter.rollback()
                    continue
                expected_next = len(history) + 1
                if migration.version != expected_next:
                    raise MigrationError("Migration pendente fora de ordem.", code="version_gap")
                started = monotonic()
                adapter.apply_migration(migration)
                execution_time_ms = max(0, int((monotonic() - started) * 1000))
                if migration.version == registry[-1].version:
                    validation = adapter.validate_current_schema()
                    if not validation.compatible:
                        raise MigrationError(
                            "Schema criado pelas migrations nao corresponde ao estado atual.",
                            code="schema_incompatible",
                        )
                adapter.insert_history(migration, _utc_now_text(), execution_time_ms)
                adapter.commit()
                applied_now.append(migration.version)
            except Exception:
                adapter.rollback()
                raise
        final_history = validate_history(adapter.load_history(), registry)
        validation = adapter.validate_current_schema()
        if not validation.compatible:
            raise MigrationError(
                "Schema posterior a migration nao corresponde a baseline.",
                code="schema_incompatible",
            )
        return {
            "ok": True,
            "environment": environment,
            "driver": target.driver,
            "applied": applied_now,
            "current_version": max((int(item.version) for item in final_history), default=0),
            "message": "Migrations aplicadas com sucesso." if applied_now else "Nenhuma migration pendente.",
        }
    except MigrationError:
        raise
    except Exception as error:
        raise MigrationError("Falha ao aplicar migrations; a transacao foi revertida.", code="migration_failed") from error
    finally:
        if adapter is not None:
            adapter.close()


def baseline_database(
    *,
    version: int = 1,
    confirm_baseline: bool = False,
    confirm_production: bool = False,
    environ: Mapping[str, str] | None = None,
    sqlite_path: str | None = None,
    database_url: str | None = None,
    migrations=None,
    adapter_factory: AdapterFactory | None = None,
    test_mode: bool = False,
) -> dict:
    environment = require_migration_authorization(
        environ,
        confirm_production=confirm_production,
        test_mode=test_mode,
    )
    if not confirm_baseline:
        raise MigrationError(
            "Baseline exige --confirm-baseline.",
            code="baseline_confirmation_required",
        )
    registry = get_registry(migrations)
    if version != 1 or version != registry[0].version:
        raise MigrationError("Somente a baseline formal versao 1 e aceita.", code="invalid_baseline_version")
    target = resolve_database_target(
        environ,
        sqlite_path=sqlite_path,
        database_url=database_url,
    )
    if not _sqlite_file_exists(target):
        raise MigrationError("Banco inexistente nao pode receber baseline.", code="database_missing")

    adapter = None
    try:
        adapter = _open_adapter(
            target,
            readonly=False,
            create=False,
            adapter_factory=adapter_factory,
        )
        adapter.begin_write()
        adapter.acquire_migration_lock()
        validation = adapter.validate_v1_schema()
        if not validation.compatible:
            raise MigrationError(
                validation.errors[0] if validation.errors else "Schema legado incompativel.",
                code="legacy_schema_incompatible",
            )
        if not adapter.table_names():
            raise MigrationError("Banco vazio nao pode receber baseline.", code="empty_database")
        if adapter.history_exists():
            history = validate_history(adapter.load_history(), registry)
            if len(history) == 1 and int(history[0].version) == 1:
                adapter.rollback()
                return {
                    "ok": True,
                    "environment": environment,
                    "driver": target.driver,
                    "baseline_version": 1,
                    "already_baselined": True,
                    "message": "Baseline ja registrada e valida.",
                }
            raise MigrationError("Historico existente e incompativel com baseline.", code="invalid_history")
        adapter.create_history_table()
        adapter.insert_history(registry[0], _utc_now_text(), 0)
        adapter.commit()
        return {
            "ok": True,
            "environment": environment,
            "driver": target.driver,
            "baseline_version": 1,
            "already_baselined": False,
            "message": "Baseline registrada sem aplicar DDL de negocio.",
        }
    except MigrationError:
        if adapter is not None:
            adapter.rollback()
        raise
    except Exception as error:
        if adapter is not None:
            adapter.rollback()
        raise MigrationError("Falha ao registrar baseline; a transacao foi revertida.", code="baseline_failed") from error
    finally:
        if adapter is not None:
            adapter.close()
