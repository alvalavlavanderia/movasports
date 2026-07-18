"""Administrative entry point for versioned database migrations."""

from database_migrations.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
