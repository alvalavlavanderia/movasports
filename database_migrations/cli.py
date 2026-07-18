from __future__ import annotations

import argparse
import json
import sys

from .runner import MigrationError, baseline_database, get_migration_status, run_database_migrations


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m database_migrations")
    subcommands = parser.add_subparsers(dest="command", required=True)

    subcommands.add_parser("status", help="Consultar migrations sem alterar o banco.")

    migrate = subcommands.add_parser("migrate", help="Aplicar migrations pendentes.")
    migrate.add_argument("--create", action="store_true", help="Permitir criar banco SQLite ausente.")
    migrate.add_argument("--confirm-production", action="store_true")

    baseline = subcommands.add_parser("baseline", help="Registrar baseline de banco legado compativel.")
    baseline.add_argument("--version", type=int, default=1)
    baseline.add_argument("--confirm-baseline", action="store_true")
    baseline.add_argument("--confirm-production", action="store_true")
    return parser


def _print_result(result: dict) -> None:
    safe = {
        key: value
        for key, value in result.items()
        if key not in {"database_url", "sqlite_path"}
    }
    print(json.dumps(safe, ensure_ascii=False, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "status":
            result = get_migration_status()
            _print_result(result)
            return 0 if result.get("ok") else 1
        if args.command == "migrate":
            result = run_database_migrations(
                create_database=args.create,
                confirm_production=args.confirm_production,
            )
            _print_result(result)
            return 0
        print(json.dumps({
            "notice": "Baseline registrara somente o historico; nenhuma migration estrutural sera aplicada."
        }, ensure_ascii=False, sort_keys=True))
        result = baseline_database(
            version=args.version,
            confirm_baseline=args.confirm_baseline,
            confirm_production=args.confirm_production,
        )
        _print_result(result)
        return 0
    except MigrationError as error:
        print(json.dumps({"ok": False, "error": str(error), "code": error.code}, ensure_ascii=False), file=sys.stderr)
        return 2
    except Exception:
        print(json.dumps({"ok": False, "error": "Falha operacional no comando de migrations."}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
