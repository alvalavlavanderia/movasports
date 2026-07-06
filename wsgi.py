from server import app, ensure_startup_backup, init_db


init_db()
ensure_startup_backup()
