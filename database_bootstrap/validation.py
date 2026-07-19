from __future__ import annotations

import json
from collections.abc import Mapping

from database_migrations.registry import get_registry
from database_migrations.runner import MigrationError, validate_history

from .models import BootstrapError, BootstrapStatus


STORE_ID = "matriz"
ADMIN_ID = "admin"

EMPTY_APP_STATE = {
    "users": [],
    "products": [],
    "customers": [],
    "suppliers": [],
    "brands": [],
    "categories": [],
    "sales": [],
    "receivables": [],
    "payables": [],
    "cash": [],
    "cashClosings": [],
    "returns": [],
    "conditionals": [],
}


def empty_app_state_json() -> str:
    return json.dumps(EMPTY_APP_STATE, ensure_ascii=False, separators=(",", ":"))


def _safe_environment(environ: Mapping[str, str]) -> str:
    value = str(environ.get("APP_ENV", "") or "").strip().lower()
    return value if value in {"development", "staging", "production"} else "unconfigured"


def _base_status(
    *,
    ok: bool,
    state: str,
    environment: str,
    driver: str,
    schema_version: int | None = None,
    action: str,
    errors: tuple[str, ...] = (),
) -> BootstrapStatus:
    return BootstrapStatus(
        ok=ok,
        state=state,
        environment=environment,
        driver=driver,
        schema_version=schema_version,
        store="UNKNOWN",
        app_state="UNKNOWN",
        admin="UNKNOWN",
        action=action,
        errors=errors,
    )


def database_missing_status(environ: Mapping[str, str], driver: str) -> BootstrapStatus:
    return _base_status(
        ok=False,
        state="DATABASE_MISSING",
        environment=_safe_environment(environ),
        driver=driver,
        action="Crie o banco e aplique as migrations antes do bootstrap.",
    )


def database_unavailable_status(environ: Mapping[str, str], driver: str) -> BootstrapStatus:
    return _base_status(
        ok=False,
        state="DATABASE_UNAVAILABLE",
        environment=_safe_environment(environ),
        driver=driver,
        action="Verifique a disponibilidade do banco sem alterar seus dados.",
        errors=("Nao foi possivel consultar o banco de dados.",),
    )


def _migration_error_state(error: MigrationError) -> str:
    if error.code == "future_version":
        return "SCHEMA_FUTURE"
    return "MIGRATION_HISTORY_INVALID"


def _component_status(adapter) -> tuple[str, str, str, str, tuple[str, ...]]:
    stores = adapter.fetch_stores()
    matrix_store = next((row for row in stores if str(row.get("id")) == STORE_ID), None)
    if matrix_store is not None:
        store_status = "STORE_PRESENT"
    elif stores:
        store_status = "STORE_MISMATCH"
    else:
        store_status = "STORE_MISSING"

    app_rows = adapter.fetch_app_states()
    app_row = next((row for row in app_rows if int(row.get("id") or 0) == 1), None)
    if app_row is None:
        app_status = "APP_STATE_CONFLICT" if app_rows else "APP_STATE_MISSING"
    else:
        try:
            parsed = json.loads(str(app_row.get("data") or ""))
            app_status = "APP_STATE_PRESENT" if isinstance(parsed, dict) else "APP_STATE_INVALID"
        except (TypeError, ValueError, json.JSONDecodeError):
            app_status = "APP_STATE_INVALID"

    users = adapter.fetch_users()
    initial = next((row for row in users if str(row.get("id")) == ADMIN_ID), None)
    active_matrix_admins = [
        row for row in users
        if str(row.get("role")) == "admin"
        and bool(row.get("active"))
        and str(row.get("store_id")) == STORE_ID
    ]
    inactive_matrix_admins = [
        row for row in users
        if str(row.get("role")) == "admin"
        and not bool(row.get("active"))
        and str(row.get("store_id")) == STORE_ID
    ]
    foreign_admins = [
        row for row in users
        if str(row.get("role")) == "admin" and str(row.get("store_id")) != STORE_ID
    ]

    if initial is not None:
        if str(initial.get("role")) != "admin":
            admin_status = "ADMIN_ID_CONFLICT"
        elif str(initial.get("store_id")) != STORE_ID:
            admin_status = "ADMIN_STORE_MISMATCH"
        elif not bool(initial.get("active")):
            admin_status = "ADMIN_INACTIVE"
        else:
            admin_status = "ADMIN_PRESENT"
    elif len(active_matrix_admins) == 1:
        admin_status = "ADMIN_PRESENT"
    elif len(active_matrix_admins) > 1:
        admin_status = "MULTIPLE_INITIAL_ADMIN_CANDIDATES"
    elif inactive_matrix_admins:
        admin_status = "ADMIN_INACTIVE"
    elif foreign_admins:
        admin_status = "ADMIN_STORE_MISMATCH"
    else:
        admin_status = "ADMIN_MISSING"

    errors: list[str] = []
    conflict_states = {
        "STORE_MISMATCH",
        "APP_STATE_CONFLICT",
        "APP_STATE_INVALID",
        "ADMIN_ID_CONFLICT",
        "ADMIN_STORE_MISMATCH",
        "ADMIN_INACTIVE",
        "MULTIPLE_INITIAL_ADMIN_CANDIDATES",
    }
    for value in (store_status, app_status, admin_status):
        if value in conflict_states:
            errors.append(value)

    present = (
        store_status == "STORE_PRESENT",
        app_status == "APP_STATE_PRESENT",
        admin_status == "ADMIN_PRESENT",
    )
    if errors:
        overall = errors[0]
        action = "Revise a inconsistencia manualmente antes de executar o bootstrap."
    elif all(present):
        overall = "BOOTSTRAP_COMPLETE"
        action = "Nenhuma acao necessaria."
    elif not any(present):
        overall = "BOOTSTRAP_NOT_STARTED"
        action = "Execute o comando administrativo de bootstrap."
    else:
        overall = "BOOTSTRAP_PARTIAL"
        action = "Execute o bootstrap para criar somente os componentes ausentes."
    return overall, store_status, app_status, admin_status, tuple(errors)


def inspect_adapter(adapter, environ: Mapping[str, str]) -> BootstrapStatus:
    environment = _safe_environment(environ)
    try:
        tables = adapter.table_names()
    except Exception:
        return database_unavailable_status(environ, adapter.driver)
    if not tables or not adapter.history_exists():
        return _base_status(
            ok=False,
            state="SCHEMA_MIGRATIONS_MISSING",
            environment=environment,
            driver=adapter.driver,
            action="Aplique migrations ou registre uma baseline valida antes do bootstrap.",
        )

    registry = get_registry()
    try:
        history = validate_history(adapter.load_history(), registry)
    except MigrationError as error:
        state = _migration_error_state(error)
        return _base_status(
            ok=False,
            state=state,
            environment=environment,
            driver=adapter.driver,
            action="Corrija o historico de migrations por processo administrativo.",
            errors=(str(error),),
        )
    except Exception:
        return _base_status(
            ok=False,
            state="MIGRATION_HISTORY_INVALID",
            environment=environment,
            driver=adapter.driver,
            action="Corrija o historico de migrations por processo administrativo.",
        )

    versions = {int(item.version) for item in history}
    pending = [item.version for item in registry if item.version not in versions]
    current_version = max(versions, default=0)
    if pending:
        return _base_status(
            ok=False,
            state="SCHEMA_OUTDATED",
            environment=environment,
            driver=adapter.driver,
            schema_version=current_version,
            action="Aplique as migrations pendentes antes do bootstrap.",
        )

    validation = adapter.validate_current_schema()
    if not validation.compatible:
        return _base_status(
            ok=False,
            state="SCHEMA_INVALID",
            environment=environment,
            driver=adapter.driver,
            schema_version=current_version,
            action="Corrija o schema por migration ou procedimento administrativo aprovado.",
            errors=tuple(validation.errors),
        )

    overall, store, app_state, admin, errors = _component_status(adapter)
    return BootstrapStatus(
        ok=not errors,
        state=overall,
        environment=environment,
        driver=adapter.driver,
        schema_version=current_version,
        store=store,
        app_state=app_state,
        admin=admin,
        action=(
            "Revise a inconsistencia manualmente antes de executar o bootstrap."
            if errors
            else (
                "Nenhuma acao necessaria."
                if overall == "BOOTSTRAP_COMPLETE"
                else "Execute o comando administrativo de bootstrap."
            )
        ),
        errors=errors,
    )


def require_writable_status(status: BootstrapStatus) -> None:
    if not status.ok:
        raise BootstrapError(
            "O banco nao atende as pre-condicoes seguras do bootstrap.",
            code=status.state.lower(),
        )
    if status.state not in {"BOOTSTRAP_NOT_STARTED", "BOOTSTRAP_PARTIAL", "BOOTSTRAP_COMPLETE"}:
        raise BootstrapError(
            "O estado atual exige intervencao administrativa manual.",
            code="bootstrap_conflict",
        )
