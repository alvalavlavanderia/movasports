from __future__ import annotations

import argparse
import json
import sys

from .models import BootstrapError
from .runner import get_bootstrap_status, run_database_bootstrap


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m database_bootstrap")
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("status", help="Consultar o bootstrap sem alterar o banco.")

    run = subcommands.add_parser("run", help="Executar o bootstrap administrativo explicito.")
    run.add_argument("--store-name", required=True)
    run.add_argument("--admin-name", required=True)
    run.add_argument("--admin-login", required=True)
    run.add_argument("--admin-password-env", required=True)
    run.add_argument("--confirm-bootstrap", action="store_true")
    run.add_argument("--confirm-production", action="store_true")
    return parser


def _print(payload: dict, *, stream=None) -> None:
    safe = {
        key: value
        for key, value in payload.items()
        if key not in {"password", "password_hash", "database_url", "sqlite_path"}
    }
    print(json.dumps(safe, ensure_ascii=False, sort_keys=True), file=stream)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "status":
            status = get_bootstrap_status()
            _print(status.to_dict())
            return 0 if status.ok else 1
        result = run_database_bootstrap(
            store_name=args.store_name,
            admin_name=args.admin_name,
            admin_login=args.admin_login,
            admin_password_env=args.admin_password_env,
            confirm_bootstrap=args.confirm_bootstrap,
            confirm_production=args.confirm_production,
        )
        _print(result.to_dict())
        return 0
    except BootstrapError as error:
        _print({"ok": False, "error": str(error), "code": error.code}, stream=sys.stderr)
        return 2
    except Exception:
        _print({"ok": False, "error": "Falha operacional no comando de bootstrap."}, stream=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
