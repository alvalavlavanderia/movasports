from __future__ import annotations

import os
import re
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path

from werkzeug.security import generate_password_hash

from database_migrations.runner import DatabaseTarget, resolve_database_target
from environment_config import FALSE_VALUES, TRUE_VALUES, VALID_ENVIRONMENTS

from .adapters import AdapterFactory, open_bootstrap_adapter
from .models import BootstrapError, BootstrapResult, BootstrapStatus
from .validation import (
    ADMIN_ID,
    STORE_ID,
    database_missing_status,
    database_unavailable_status,
    empty_app_state_json,
    inspect_adapter,
    require_writable_status,
)


PASSWORD_ENV_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
COMMON_PASSWORDS = frozenset({"1234", "admin", "senha", "password"})


def _sqlite_exists(target: DatabaseTarget) -> bool:
    return target.driver != "sqlite" or Path(target.sqlite_path).is_file()


def _open(target: DatabaseTarget, *, readonly: bool, adapter_factory: AdapterFactory | None):
    factory = adapter_factory or open_bootstrap_adapter
    return factory(target, readonly=readonly)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _bootstrap_flag(environ: Mapping[str, str]) -> bool:
    raw = str(environ.get("MOVA_ALLOW_BOOTSTRAP", "") or "").strip().lower()
    if raw in TRUE_VALUES:
        return True
    if raw in FALSE_VALUES:
        return False
    return False


def require_bootstrap_authorization(
    environ: Mapping[str, str],
    *,
    confirm_bootstrap: bool,
    confirm_production: bool,
    test_mode: bool = False,
) -> str:
    if not confirm_bootstrap:
        raise BootstrapError(
            "Bootstrap exige confirmacao administrativa explicita.",
            code="bootstrap_confirmation_required",
        )
    if test_mode:
        return "test"
    environment = str(environ.get("APP_ENV", "") or "").strip().lower()
    if environment not in VALID_ENVIRONMENTS:
        raise BootstrapError(
            "APP_ENV deve estar configurada com um ambiente reconhecido.",
            code="environment_not_configured",
        )
    if not _bootstrap_flag(environ):
        raise BootstrapError(
            "Bootstrap nao esta autorizado neste ambiente.",
            code="bootstrap_not_allowed",
        )
    if environment == "production" and not confirm_production:
        raise BootstrapError(
            "Production exige confirmacao administrativa adicional.",
            code="production_confirmation_required",
        )
    return environment


def validate_bootstrap_credentials(
    *,
    store_name: str,
    admin_name: str,
    admin_login: str,
    password_env: str,
    environ: Mapping[str, str],
) -> str:
    if not str(store_name or "").strip():
        raise BootstrapError("Nome da loja e obrigatorio.", code="store_name_required")
    if not str(admin_name or "").strip():
        raise BootstrapError("Nome do administrador e obrigatorio.", code="admin_name_required")
    login = str(admin_login or "").strip()
    if not login:
        raise BootstrapError("Login do administrador e obrigatorio.", code="admin_login_required")
    variable = str(password_env or "").strip()
    if not variable or not PASSWORD_ENV_PATTERN.fullmatch(variable):
        raise BootstrapError(
            "Informe uma variavel de ambiente valida para a senha.",
            code="password_environment_invalid",
        )
    password = str(environ.get(variable, "") or "")
    if not password:
        raise BootstrapError(
            "A variavel de senha do administrador nao esta configurada.",
            code="password_missing",
        )
    if len(password) < 8:
        raise BootstrapError("A senha inicial deve ter pelo menos 8 caracteres.", code="password_too_short")
    if password.lower() in COMMON_PASSWORDS:
        raise BootstrapError("Escolha uma senha inicial mais forte.", code="password_too_common")
    if password.casefold() == login.casefold():
        raise BootstrapError("A senha inicial nao pode ser igual ao login.", code="password_matches_login")
    return password


def get_bootstrap_status(
    *,
    environ: Mapping[str, str] | None = None,
    sqlite_path: str | None = None,
    database_url: str | None = None,
    adapter_factory: AdapterFactory | None = None,
) -> BootstrapStatus:
    source = os.environ if environ is None else environ
    target = resolve_database_target(source, sqlite_path=sqlite_path, database_url=database_url)
    if not _sqlite_exists(target):
        return database_missing_status(source, target.driver)
    adapter = None
    try:
        adapter = _open(target, readonly=True, adapter_factory=adapter_factory)
        return inspect_adapter(adapter, source)
    except Exception:
        return database_unavailable_status(source, target.driver)
    finally:
        if adapter is not None:
            try:
                adapter.rollback()
            finally:
                adapter.close()


def _ensure_login_available(adapter, login: str) -> None:
    for user in adapter.fetch_users():
        if str(user.get("id")) == ADMIN_ID:
            raise BootstrapError(
                "O identificador reservado do administrador ja esta em uso.",
                code="admin_id_conflict",
            )
        if (
            str(user.get("store_id")) == STORE_ID
            and str(user.get("login", "")).casefold() == login.casefold()
        ):
            raise BootstrapError(
                "O login informado ja pertence a outro usuario.",
                code="admin_login_conflict",
            )


def run_database_bootstrap(
    *,
    store_name: str,
    admin_name: str,
    admin_login: str,
    admin_password_env: str,
    confirm_bootstrap: bool,
    confirm_production: bool = False,
    environ: Mapping[str, str] | None = None,
    sqlite_path: str | None = None,
    database_url: str | None = None,
    adapter_factory: AdapterFactory | None = None,
    test_mode: bool = False,
) -> BootstrapResult:
    source = os.environ if environ is None else environ
    environment = require_bootstrap_authorization(
        source,
        confirm_bootstrap=confirm_bootstrap,
        confirm_production=confirm_production,
        test_mode=test_mode,
    )
    password = validate_bootstrap_credentials(
        store_name=store_name,
        admin_name=admin_name,
        admin_login=admin_login,
        password_env=admin_password_env,
        environ=source,
    )
    target = resolve_database_target(source, sqlite_path=sqlite_path, database_url=database_url)
    if not _sqlite_exists(target):
        raise BootstrapError("Banco inexistente nao pode receber bootstrap.", code="database_missing")

    adapter = None
    transaction_started = False
    try:
        adapter = _open(target, readonly=False, adapter_factory=adapter_factory)
        adapter.begin_write()
        transaction_started = True
        adapter.acquire_bootstrap_lock()

        status = inspect_adapter(adapter, source)
        require_writable_status(status)
        if status.state == "BOOTSTRAP_COMPLETE":
            adapter.commit()
            transaction_started = False
            return BootstrapResult(
                ok=True,
                status="BOOTSTRAP_COMPLETE",
                environment=environment,
                driver=target.driver,
                schema_version=int(status.schema_version or 0),
                store_created=False,
                app_state_created=False,
                admin_created=False,
                already_complete=True,
            )

        now = _utc_now()
        store_created = status.store == "STORE_MISSING"
        app_state_created = status.app_state == "APP_STATE_MISSING"
        admin_created = status.admin == "ADMIN_MISSING"

        if store_created:
            adapter.insert_store(STORE_ID, store_name.strip(), now)
        if app_state_created:
            adapter.insert_app_state(empty_app_state_json(), now)
        if admin_created:
            _ensure_login_available(adapter, admin_login.strip())
            adapter.insert_admin(
                ADMIN_ID,
                STORE_ID,
                admin_name.strip(),
                admin_login.strip(),
                generate_password_hash(password),
                now,
            )

        final_status = inspect_adapter(adapter, source)
        if not final_status.ok or final_status.state != "BOOTSTRAP_COMPLETE":
            raise BootstrapError(
                "O estado final do bootstrap nao ficou consistente.",
                code="bootstrap_final_validation_failed",
            )
        adapter.commit()
        transaction_started = False
        return BootstrapResult(
            ok=True,
            status=final_status.state,
            environment=environment,
            driver=target.driver,
            schema_version=int(final_status.schema_version or 0),
            store_created=store_created,
            app_state_created=app_state_created,
            admin_created=admin_created,
            already_complete=False,
        )
    except BootstrapError:
        if adapter is not None and transaction_started:
            adapter.rollback()
        raise
    except Exception as error:
        if adapter is not None and transaction_started:
            adapter.rollback()
        message = "Falha operacional; o bootstrap foi integralmente revertido."
        if "locked" in str(error).lower() or "lock" in type(error).__name__.lower():
            raise BootstrapError(message, code="bootstrap_lock_error") from error
        raise BootstrapError(message, code="bootstrap_failed") from error
    finally:
        password = ""
        if adapter is not None:
            adapter.close()
