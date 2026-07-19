from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

from database_bootstrap import cli
from database_bootstrap.models import BootstrapError, BootstrapResult, BootstrapStatus


def complete_status(**changes):
    values = {
        "ok": True,
        "state": "BOOTSTRAP_COMPLETE",
        "environment": "development",
        "driver": "sqlite",
        "schema_version": 1,
        "store": "STORE_PRESENT",
        "app_state": "APP_STATE_PRESENT",
        "admin": "ADMIN_PRESENT",
        "action": "Nenhuma acao necessaria.",
    }
    values.update(changes)
    return BootstrapStatus(**values)


def successful_result(**changes):
    values = {
        "ok": True,
        "status": "BOOTSTRAP_COMPLETE",
        "environment": "development",
        "driver": "sqlite",
        "schema_version": 1,
        "store_created": True,
        "app_state_created": True,
        "admin_created": True,
        "already_complete": False,
    }
    values.update(changes)
    return BootstrapResult(**values)


RUN_ARGUMENTS = [
    "run",
    "--store-name", "Loja Matriz",
    "--admin-name", "Administrador",
    "--admin-login", "admin",
    "--admin-password-env", "BOOTSTRAP_PASSWORD",
    "--confirm-bootstrap",
]


class BootstrapCliTests(unittest.TestCase):
    def invoke(self, args, *, status=None, result=None, error=None):
        stdout = io.StringIO()
        stderr = io.StringIO()
        status = status or complete_status()
        result = result or successful_result()
        run_side_effect = error if error is not None else None
        with (
            mock.patch.object(cli, "get_bootstrap_status", return_value=status),
            mock.patch.object(cli, "run_database_bootstrap", return_value=result, side_effect=run_side_effect) as run,
            redirect_stdout(stdout),
            redirect_stderr(stderr),
        ):
            code = cli.main(args)
        return code, stdout.getvalue(), stderr.getvalue(), run

    def test_status_success_exit_zero(self):
        code, output, error, _ = self.invoke(["status"])
        self.assertEqual(code, 0)
        self.assertFalse(error)
        self.assertEqual(json.loads(output)["state"], "BOOTSTRAP_COMPLETE")

    def test_status_failure_exit_nonzero(self):
        status = complete_status(ok=False, state="DATABASE_MISSING")
        code, output, _, _ = self.invoke(["status"], status=status)
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(output)["state"], "DATABASE_MISSING")

    def test_run_success_exit_zero(self):
        code, output, error, _ = self.invoke(RUN_ARGUMENTS)
        self.assertEqual(code, 0)
        self.assertFalse(error)
        self.assertTrue(json.loads(output)["admin_created"])

    def test_run_forwards_required_parameters(self):
        _, _, _, run = self.invoke(RUN_ARGUMENTS)
        run.assert_called_once_with(
            store_name="Loja Matriz",
            admin_name="Administrador",
            admin_login="admin",
            admin_password_env="BOOTSTRAP_PASSWORD",
            confirm_bootstrap=True,
            confirm_production=False,
        )

    def test_run_forwards_production_confirmation(self):
        _, _, _, run = self.invoke([*RUN_ARGUMENTS, "--confirm-production"])
        self.assertTrue(run.call_args.kwargs["confirm_production"])

    def test_run_without_confirmation_reaches_authoritative_runner(self):
        args = [item for item in RUN_ARGUMENTS if item != "--confirm-bootstrap"]
        _, _, _, run = self.invoke(args)
        self.assertFalse(run.call_args.kwargs["confirm_bootstrap"])

    def test_administrative_error_exit_two(self):
        failure = BootstrapError("Operacao bloqueada.", code="blocked")
        code, output, error, _ = self.invoke(RUN_ARGUMENTS, error=failure)
        self.assertEqual(code, 2)
        self.assertFalse(output)
        self.assertEqual(json.loads(error)["code"], "blocked")

    def test_unknown_error_has_safe_message(self):
        code, output, error, _ = self.invoke(RUN_ARGUMENTS, error=RuntimeError("private detail"))
        self.assertEqual(code, 1)
        self.assertFalse(output)
        self.assertNotIn("private detail", error)
        self.assertNotIn("Traceback", error)

    def test_output_does_not_expose_password(self):
        result = successful_result()
        code, output, _, _ = self.invoke(RUN_ARGUMENTS, result=result)
        self.assertEqual(code, 0)
        self.assertNotIn("Strong-123", output)
        self.assertNotIn("password_hash", output)

    def test_output_filters_sensitive_internal_keys(self):
        stream = io.StringIO()
        with redirect_stdout(stream):
            cli._print({
                "ok": True,
                "password": "secret",
                "password_hash": "hash",
                "database_url": "postgresql://private",
                "sqlite_path": "C:/private.db",
            })
        payload = json.loads(stream.getvalue())
        self.assertEqual(payload, {"ok": True})

    def test_status_never_calls_run(self):
        _, _, _, run = self.invoke(["status"])
        run.assert_not_called()

    def test_missing_store_name_is_rejected_by_parser(self):
        args = [item for item in RUN_ARGUMENTS if item not in {"--store-name", "Loja Matriz"}]
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as context:
            cli.main(args)
        self.assertEqual(context.exception.code, 2)

    def test_missing_admin_name_is_rejected_by_parser(self):
        args = RUN_ARGUMENTS.copy()
        position = args.index("--admin-name")
        del args[position:position + 2]
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            cli.main(args)

    def test_missing_admin_login_is_rejected_by_parser(self):
        args = RUN_ARGUMENTS.copy()
        position = args.index("--admin-login")
        del args[position:position + 2]
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            cli.main(args)

    def test_missing_password_environment_is_rejected_by_parser(self):
        args = RUN_ARGUMENTS.copy()
        position = args.index("--admin-password-env")
        del args[position:position + 2]
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            cli.main(args)

    def test_invalid_command_is_rejected(self):
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            cli.main(["unknown"])


if __name__ == "__main__":
    unittest.main()
