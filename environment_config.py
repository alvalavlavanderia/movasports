from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Mapping


VALID_ENVIRONMENTS = frozenset({"development", "staging", "production"})
TRUE_VALUES = frozenset({"1", "true", "yes", "on"})
FALSE_VALUES = frozenset({"", "0", "false", "no", "off"})


@dataclass(frozen=True)
class EnvironmentConfig:
    environment: str | None
    status: str
    allow_migrations: bool
    allow_data_import_reset: bool

    @property
    def is_configured(self) -> bool:
        return self.status == "configured"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_staging(self) -> bool:
        return self.environment == "staging"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def effective_name(self) -> str:
        return self.environment or self.status


def _read_flag(environ: Mapping[str, str], name: str, logger: logging.Logger) -> bool:
    value = str(environ.get(name, "") or "").strip().lower()
    if value in TRUE_VALUES:
        return True
    if value not in FALSE_VALUES:
        logger.warning("A variável %s possui valor inválido e foi desabilitada por segurança.", name)
    return False


def load_environment_config(
    environ: Mapping[str, str] | None = None,
    logger: logging.Logger | None = None,
) -> EnvironmentConfig:
    source = os.environ if environ is None else environ
    target_logger = logger or logging.getLogger("mova.environment")
    raw_environment = str(source.get("APP_ENV", "") or "").strip().lower()

    if not raw_environment:
        target_logger.warning(
            "APP_ENV não está configurada. A aplicação seguirá temporariamente em modo compatível e restritivo; "
            "capacidades sensíveis permanecerão desabilitadas."
        )
        environment = None
        status = "missing"
    elif raw_environment not in VALID_ENVIRONMENTS:
        target_logger.warning(
            "APP_ENV possui valor não reconhecido. A aplicação seguirá em modo restritivo; "
            "capacidades sensíveis permanecerão desabilitadas."
        )
        environment = None
        status = "invalid"
    else:
        environment = raw_environment
        status = "configured"

    requested_migrations = _read_flag(source, "MOVA_ALLOW_MIGRATIONS", target_logger)
    requested_data_operations = _read_flag(source, "MOVA_ALLOW_DATA_IMPORT_RESET", target_logger)
    sensitive_environment = environment in {"development", "staging"}

    return EnvironmentConfig(
        environment=environment,
        status=status,
        allow_migrations=bool(sensitive_environment and requested_migrations),
        allow_data_import_reset=bool(sensitive_environment and requested_data_operations),
    )
