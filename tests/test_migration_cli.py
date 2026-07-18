from __future__ import annotations

import contextlib
import io
import json
import unittest
from unittest import mock

from database_migrations import cli
from database_migrations.runner import MigrationError


class MigrationCliTests(unittest.TestCase):
    def invoke(self, argv):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = cli.main(argv)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_status_returns_zero_for_valid_result(self):
        with mock.patch.object(cli, "get_migration_status", return_value={"ok": True, "state": "up_to_date"}):
            code, output, error = self.invoke(["status"])
        self.assertEqual(code, 0)
        self.assertEqual(error, "")
        self.assertEqual(json.loads(output)["state"], "up_to_date")

    def test_migrate_returns_zero_for_success(self):
        with mock.patch.object(cli, "run_database_migrations", return_value={"ok": True, "applied": [1]}):
            code, output, error = self.invoke(["migrate", "--create"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output)["applied"], [1])
        self.assertEqual(error, "")

    def test_migrate_returns_nonzero_for_operational_error(self):
        with mock.patch.object(
            cli,
            "run_database_migrations",
            side_effect=MigrationError("Operacao bloqueada.", code="blocked"),
        ):
            code, output, error = self.invoke(["migrate"])
        self.assertEqual(code, 2)
        self.assertEqual(output, "")
        self.assertEqual(json.loads(error)["code"], "blocked")

    def test_baseline_without_confirmation_returns_nonzero(self):
        with mock.patch.object(
            cli,
            "baseline_database",
            side_effect=MigrationError("Confirmacao obrigatoria.", code="confirmation"),
        ):
            code, _output, error = self.invoke(["baseline"])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(error)["code"], "confirmation")

    def test_cli_forwards_confirmations(self):
        with mock.patch.object(cli, "baseline_database", return_value={"ok": True}) as baseline:
            code, _output, _error = self.invoke(
                ["baseline", "--version", "1", "--confirm-baseline", "--confirm-production"]
            )
        self.assertEqual(code, 0)
        baseline.assert_called_once_with(
            version=1,
            confirm_baseline=True,
            confirm_production=True,
        )

    def test_baseline_prints_non_structural_notice_before_execution(self):
        events = []

        def baseline(**_kwargs):
            events.append("called")
            return {"ok": True}

        with mock.patch.object(cli, "baseline_database", side_effect=baseline):
            code, output, _error = self.invoke(["baseline", "--confirm-baseline"])
        self.assertEqual(code, 0)
        lines = output.strip().splitlines()
        self.assertIn("nenhuma migration estrutural", json.loads(lines[0])["notice"].lower())
        self.assertEqual(events, ["called"])
        self.assertTrue(json.loads(lines[1])["ok"])

    def test_safe_output_removes_database_location(self):
        result = {
            "ok": True,
            "database_url": "postgresql://user:secret@private/db",
            "sqlite_path": "C:/private/loja.db",
        }
        with mock.patch.object(cli, "get_migration_status", return_value=result):
            code, output, _error = self.invoke(["status"])
        self.assertEqual(code, 0)
        self.assertNotIn("secret", output)
        self.assertNotIn("private", output)
        self.assertNotIn("database_url", output)
        self.assertNotIn("sqlite_path", output)

    def test_error_does_not_print_traceback_or_secrets(self):
        with mock.patch.object(cli, "get_migration_status", side_effect=RuntimeError("secret-value")):
            code, output, error = self.invoke(["status"])
        self.assertEqual(code, 1)
        self.assertEqual(output, "")
        self.assertNotIn("Traceback", error)
        self.assertNotIn("secret-value", error)

    def test_output_contains_no_personal_or_password_data(self):
        result = {"ok": True, "state": "up_to_date", "current_version": 1}
        with mock.patch.object(cli, "get_migration_status", return_value=result):
            _code, output, _error = self.invoke(["status"])
        self.assertNotIn("password", output.lower())
        self.assertNotIn("cliente", output.lower())


if __name__ == "__main__":
    unittest.main()
