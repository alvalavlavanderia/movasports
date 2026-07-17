import importlib
import logging
import sys
import unittest
from unittest import mock

from environment_config import load_environment_config


class EnvironmentConfigTests(unittest.TestCase):
    def load(self, values):
        logger = mock.Mock(spec=logging.Logger)
        return load_environment_config(values, logger), logger

    def test_development_is_recognized(self):
        config, logger = self.load({"APP_ENV": "development"})

        self.assertEqual(config.environment, "development")
        self.assertEqual(config.status, "configured")
        self.assertTrue(config.is_development)
        self.assertFalse(config.allow_migrations)
        self.assertFalse(config.allow_data_import_reset)
        logger.warning.assert_not_called()

    def test_staging_is_recognized(self):
        config, _ = self.load({"APP_ENV": "staging"})

        self.assertEqual(config.environment, "staging")
        self.assertTrue(config.is_staging)

    def test_production_is_recognized(self):
        config, _ = self.load({"APP_ENV": "production"})

        self.assertEqual(config.environment, "production")
        self.assertTrue(config.is_production)

    def test_invalid_environment_is_restrictive_without_logging_its_value(self):
        invalid_value = "invalid-with-sensitive-text"
        config, logger = self.load({
            "APP_ENV": invalid_value,
            "DATABASE_URL": "postgresql://user:secret@example.invalid/database",
            "MOVA_SECRET_KEY": "do-not-log-this-secret",
            "MOVA_ALLOW_MIGRATIONS": "true",
            "MOVA_ALLOW_DATA_IMPORT_RESET": "true",
        })

        self.assertIsNone(config.environment)
        self.assertEqual(config.status, "invalid")
        self.assertFalse(config.allow_migrations)
        self.assertFalse(config.allow_data_import_reset)
        logged = " ".join(str(call) for call in logger.warning.call_args_list)
        self.assertNotIn(invalid_value, logged)
        self.assertNotIn("postgresql://", logged)
        self.assertNotIn("do-not-log-this-secret", logged)

    def test_missing_environment_remains_operational_but_restrictive(self):
        config, logger = self.load({
            "MOVA_ALLOW_MIGRATIONS": "true",
            "MOVA_ALLOW_DATA_IMPORT_RESET": "true",
        })

        self.assertIsNone(config.environment)
        self.assertEqual(config.status, "missing")
        self.assertEqual(config.effective_name, "missing")
        self.assertFalse(config.allow_migrations)
        self.assertFalse(config.allow_data_import_reset)
        logger.warning.assert_called_once()

    def test_sensitive_flags_are_disabled_by_default(self):
        for environment in ("development", "staging", "production"):
            with self.subTest(environment=environment):
                config, _ = self.load({"APP_ENV": environment})
                self.assertFalse(config.allow_migrations)
                self.assertFalse(config.allow_data_import_reset)

    def test_development_and_staging_require_explicit_flags(self):
        for environment in ("development", "staging"):
            with self.subTest(environment=environment):
                config, _ = self.load({
                    "APP_ENV": environment,
                    "MOVA_ALLOW_MIGRATIONS": "true",
                    "MOVA_ALLOW_DATA_IMPORT_RESET": "1",
                })
                self.assertTrue(config.allow_migrations)
                self.assertTrue(config.allow_data_import_reset)

    def test_production_never_gets_sensitive_capabilities_from_flags(self):
        config, _ = self.load({
            "APP_ENV": "production",
            "MOVA_ALLOW_MIGRATIONS": "true",
            "MOVA_ALLOW_DATA_IMPORT_RESET": "true",
        })

        self.assertFalse(config.allow_migrations)
        self.assertFalse(config.allow_data_import_reset)

    def test_invalid_flag_is_disabled_without_logging_its_value(self):
        invalid_flag = "secret-looking-invalid-value"
        config, logger = self.load({
            "APP_ENV": "development",
            "MOVA_ALLOW_MIGRATIONS": invalid_flag,
        })

        self.assertFalse(config.allow_migrations)
        logged = " ".join(str(call) for call in logger.warning.call_args_list)
        self.assertNotIn(invalid_flag, logged)

    def test_importing_wsgi_has_no_database_or_backup_side_effect(self):
        import server

        sys.modules.pop("wsgi", None)
        with (
            mock.patch.object(server, "init_db") as init_db,
            mock.patch.object(server, "ensure_startup_backup") as startup_backup,
            mock.patch.object(server, "connect_db") as connect_db,
        ):
            module = importlib.import_module("wsgi")

        self.assertIs(module.app, server.app)
        init_db.assert_not_called()
        startup_backup.assert_not_called()
        connect_db.assert_not_called()


if __name__ == "__main__":
    unittest.main()
