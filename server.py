from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone

from flask import Flask, jsonify, request, send_from_directory, session
from environment_config import load_environment_config
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash


APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
USE_POSTGRES = bool(DATABASE_URL)
DB_PATH = os.environ.get("MOVA_DB", os.path.join(APP_DIR, "loja.db"))
BACKUP_DIR = os.environ.get("MOVA_BACKUP_DIR", os.path.join(APP_DIR, "backups"))
UPLOAD_DIR = os.environ.get("MOVA_UPLOAD_DIR", os.path.join(APP_DIR, "uploads"))
PRODUCT_UPLOAD_DIR = os.path.join(UPLOAD_DIR, "products")
ALLOWED_PRODUCT_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_PRODUCT_IMAGE_BYTES = 5 * 1024 * 1024
CLOUDINARY_URL = os.environ.get("CLOUDINARY_URL", "").strip()
CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME", "").strip()
CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY", "").strip()
CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET", "").strip()
CLOUDINARY_FOLDER = os.environ.get("CLOUDINARY_FOLDER", "mova-sports/products").strip() or "mova-sports/products"
VALID_CLOUDINARY_URL = CLOUDINARY_URL.startswith("cloudinary://")
USE_CLOUDINARY = bool(VALID_CLOUDINARY_URL or (CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET))
DB_BUSY_TIMEOUT_MS = max(1000, int(float(os.environ.get("MOVA_DB_BUSY_TIMEOUT_MS", "5000") or 5000)))
ENVIRONMENT = load_environment_config()
APP_ENV = ENVIRONMENT.environment or ""
IS_PRODUCTION = ENVIRONMENT.is_production
ALLOW_MIGRATIONS = ENVIRONMENT.allow_migrations
ALLOW_DATA_IMPORT_RESET = ENVIRONMENT.allow_data_import_reset
SECRET_KEY = os.environ.get("MOVA_SECRET_KEY", "").strip()
SESSION_HOURS = max(1, int(float(os.environ.get("MOVA_SESSION_HOURS", "12") or 12)))
LOGIN_ATTEMPT_LIMIT = max(3, int(float(os.environ.get("MOVA_LOGIN_ATTEMPTS", "5") or 5)))
LOGIN_ATTEMPT_WINDOW_SECONDS = max(60, int(float(os.environ.get("MOVA_LOGIN_WINDOW_SECONDS", "900") or 900)))
LOGIN_ATTEMPTS: dict[str, list[datetime]] = {}
POSTGRES_CAMEL_ALIASES = (
    "cashIn",
    "cashOut",
    "costTotal",
    "createdAt",
    "customerId",
    "customerName",
    "dueDate",
    "expectedCash",
    "informedCash",
    "issueDate",
    "lastPaymentAt",
    "minStock",
    "paidAmount",
    "paidAt",
    "productId",
    "productName",
    "receivableId",
    "refId",
    "returnId",
    "saleId",
    "totalBalance",
    "unitCost",
    "unitPrice",
    "updatedAt",
    "userId",
    "userName",
    "userRole",
)

if IS_PRODUCTION:
    if not SECRET_KEY or len(SECRET_KEY) < 32:
        raise RuntimeError("Defina MOVA_SECRET_KEY com pelo menos 32 caracteres em produção.")
    admin_password = os.environ.get("MOVA_ADMIN_PASSWORD", "").strip()
    if admin_password and (
        len(admin_password) < 8
        or admin_password.lower() in {"1234", "admin", "senha", "password"}
    ):
        raise RuntimeError("MOVA_ADMIN_PASSWORD deve ter pelo menos 8 caracteres e não pode ser uma senha comum.")

app = Flask(__name__, static_folder=APP_DIR, static_url_path="")
app.secret_key = SECRET_KEY or "mova-sports-dev-secret"
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=IS_PRODUCTION,
    PERMANENT_SESSION_LIFETIME=timedelta(hours=SESSION_HOURS),
)

DATA_IMPORT_RESET_OPERATIONS = {
    ("POST", "/api/import"): "import",
    ("POST", "/api/reset"): "reset",
    ("PUT", "/api/state"): "state_replace",
}


def current_data_import_reset_operation() -> str | None:
    return DATA_IMPORT_RESET_OPERATIONS.get((request.method, request.path))


def data_import_reset_denial_reason(user: dict | None) -> str | None:
    if not user:
        return "unauthenticated"
    if user.get("role") != "admin":
        return "not_admin"
    if ENVIRONMENT.environment not in {"development", "staging"}:
        return "capability_disabled"
    if not ENVIRONMENT.allow_data_import_reset:
        return "capability_disabled"
    return None


def data_import_reset_capabilities(user: dict | None) -> dict:
    return {"dataImportReset": data_import_reset_denial_reason(user) is None}


def log_blocked_data_operation(operation: str, reason: str) -> None:
    app.logger.warning(
        "Operacao destrutiva bloqueada. operation=%s reason=%s",
        operation,
        reason,
    )


@app.after_request
def no_cache(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if IS_PRODUCTION:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


@app.before_request
def require_login_for_api():
    if not request.path.startswith("/api/"):
        return None
    if request.path in {"/api/health", "/api/session", "/api/login", "/api/logout"}:
        return None
    if not session.get("user"):
        operation = current_data_import_reset_operation()
        if operation:
            log_blocked_data_operation(operation, "unauthenticated")
        return jsonify({"ok": False, "error": "Login obrigatório."}), 401
    return None


@app.before_request
def protect_data_import_reset_before_database_access():
    operation = current_data_import_reset_operation()
    if not operation:
        return None
    reason = data_import_reset_denial_reason(session.get("user"))
    if reason == "not_admin":
        log_blocked_data_operation(operation, reason)
        return jsonify({"ok": False, "error": "Apenas administrador pode realizar esta ação."}), 403
    if reason == "capability_disabled":
        log_blocked_data_operation(operation, reason)
        return jsonify({"ok": False, "error": "Operação indisponível neste ambiente."}), 403
    return None


@app.before_request
def validate_active_session_for_api():
    if not request.path.startswith("/api/"):
        return None
    if request.path in {"/api/health", "/api/session", "/api/login", "/api/logout"}:
        return None
    if not session.get("user"):
        return None
    if not refresh_session_user():
        operation = current_data_import_reset_operation()
        if operation:
            log_blocked_data_operation(operation, "invalid_session")
        session.clear()
        return jsonify({"ok": False, "error": "Sessao expirada. Faca login novamente."}), 401
    return None


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def refresh_session_user() -> dict | None:
    user = session.get("user")
    if not user:
        return None
    init_db()
    with connect_db() as conn:
        row = conn.execute(
            """
            SELECT id, name, login, role, active
            FROM users
            WHERE store_id = ? AND id = ?
            """,
            ("matriz", user.get("id")),
        ).fetchone()
    if not row or not row["active"]:
        return None
    public = public_user(row)
    if public != user:
        session["user"] = public
    return public


def client_rate_key(login: str) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    ip = forwarded_for.split(",", 1)[0].strip() or request.remote_addr or "unknown"
    return f"{ip}:{login.casefold()}"


def login_blocked(login: str) -> bool:
    key = client_rate_key(login)
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=LOGIN_ATTEMPT_WINDOW_SECONDS)
    LOGIN_ATTEMPTS[key] = [item for item in LOGIN_ATTEMPTS.get(key, []) if item > cutoff]
    return len(LOGIN_ATTEMPTS[key]) >= LOGIN_ATTEMPT_LIMIT


def register_login_failure(login: str) -> None:
    key = client_rate_key(login)
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=LOGIN_ATTEMPT_WINDOW_SECONDS)
    attempts = [item for item in LOGIN_ATTEMPTS.get(key, []) if item > cutoff]
    attempts.append(datetime.now(timezone.utc))
    LOGIN_ATTEMPTS[key] = attempts


def clear_login_failures(login: str) -> None:
    LOGIN_ATTEMPTS.pop(client_rate_key(login), None)


def validate_password_strength(password: str) -> str | None:
    if not IS_PRODUCTION or not password:
        return None
    if len(password) < 8:
        return "Em produção, a senha deve ter pelo menos 8 caracteres."
    if password.lower() in {"1234", "admin", "senha", "password"}:
        return "Escolha uma senha mais forte."
    if password.isdigit() or password.isalpha():
        return "Use uma senha com letras, números ou símbolos."
    return None


class DbRow(dict):
    def __init__(self, keys, values):
        super().__init__(zip(keys, values))
        self._values = list(values)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._values[key]
        return super().__getitem__(key)


class EmptyCursor:
    def fetchone(self):
        return None

    def fetchall(self):
        return []


class PgCursor:
    def __init__(self, cursor):
        self.cursor = cursor
        self.keys = [getattr(item, "name", item[0]) for item in cursor.description] if cursor.description else []

    def _row(self, values):
        if values is None:
            return None
        return DbRow(self.keys, values)

    def fetchone(self):
        return self._row(self.cursor.fetchone())

    def fetchall(self):
        return [self._row(row) for row in self.cursor.fetchall()]


class PgConnection:
    def __init__(self, url: str):
        import psycopg2

        self.conn = psycopg2.connect(url)

    def execute(self, sql: str, params=()):
        translated = translate_postgres_sql(sql)
        if translated is None:
            return EmptyCursor()
        cursor = self.conn.cursor()
        cursor.execute(translated, params or ())
        return PgCursor(cursor)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        if exc_type:
            self.conn.rollback()
        else:
            self.conn.commit()
        self.conn.close()


def translate_postgres_sql(sql: str) -> str | None:
    stripped = sql.strip()
    upper = stripped.upper()
    if upper.startswith("PRAGMA"):
        return None
    if upper.startswith("INSERT OR IGNORE INTO STORES"):
        sql = "INSERT INTO stores (id, name, created_at) VALUES (?, ?, ?) ON CONFLICT (id) DO NOTHING"
    sql = sql.replace("ORDER BY name COLLATE NOCASE", "ORDER BY LOWER(name)")
    for alias in POSTGRES_CAMEL_ALIASES:
        sql = sql.replace(f" AS {alias}", f' AS "{alias}"')
    return sql.replace("?", "%s")


def connect_db():
    if USE_POSTGRES:
        return PgConnection(DATABASE_URL)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute(f"PRAGMA busy_timeout = {DB_BUSY_TIMEOUT_MS}")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    return conn


def ensure_backup_dir() -> None:
    os.makedirs(BACKUP_DIR, exist_ok=True)


def create_database_backup(reason: str = "manual") -> dict:
    if USE_POSTGRES:
        raise RuntimeError("Backup manual por arquivo nao se aplica ao PostgreSQL. Use backup/snapshot da hospedagem.")
    ensure_backup_dir()
    init_db()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_reason = "".join(char for char in reason.lower().strip().replace(" ", "-") if char.isalnum() or char in {"-", "_"}) or "manual"
    filename = f"loja-{stamp}-{safe_reason}.db"
    path = os.path.join(BACKUP_DIR, filename)
    with connect_db() as source, sqlite3.connect(path) as target:
        source.execute("PRAGMA wal_checkpoint(FULL)")
        source.backup(target)
    return {
        "filename": filename,
        "path": path,
        "size": os.path.getsize(path),
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "reason": reason,
    }


def list_database_backups() -> list[dict]:
    if USE_POSTGRES:
        return []
    ensure_backup_dir()
    backups = []
    for entry in os.scandir(BACKUP_DIR):
        if not entry.is_file() or not entry.name.endswith(".db"):
            continue
        stat = entry.stat()
        backups.append({
            "filename": entry.name,
            "size": stat.st_size,
            "createdAt": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
        })
    return sorted(backups, key=lambda item: item["createdAt"], reverse=True)


def prune_database_backups(keep: int = 30) -> None:
    backups = list_database_backups()
    for backup in backups[keep:]:
        try:
            os.remove(os.path.join(BACKUP_DIR, backup["filename"]))
        except FileNotFoundError:
            pass


def database_file_size(path: str) -> int:
    return os.path.getsize(path) if os.path.exists(path) else 0


def database_status() -> dict:
    init_db()
    backup_items = list_database_backups()
    table_names = [
        "products",
        "customers",
        "sales",
        "cash_movements",
        "receivables",
        "payables",
        "cash_closings",
        "users",
        "audit_logs",
    ]
    counts = {}
    if USE_POSTGRES:
        with connect_db() as conn:
            version = conn.execute("SELECT version() AS version").fetchone()["version"]
            database_name = conn.execute("SELECT current_database() AS name").fetchone()["name"]
            size = int(conn.execute("SELECT pg_database_size(current_database()) AS size").fetchone()["size"])
            for table in table_names:
                try:
                    counts[table] = int(conn.execute(f"SELECT COUNT(*) AS total FROM {table}").fetchone()["total"])
                except Exception:
                    counts[table] = 0
        return {
            "engine": "PostgreSQL",
            "path": database_name,
            "filename": database_name,
            "size": size,
            "walSize": 0,
            "shmSize": 0,
            "journalMode": "server-managed",
            "synchronous": "server-managed",
            "foreignKeys": True,
            "busyTimeoutMs": None,
            "pageCount": None,
            "pageSize": None,
            "estimatedDataSize": size,
            "integrity": "ok",
            "foreignKeyErrors": 0,
            "counts": counts,
            "backupCount": len(backup_items),
            "lastBackup": backup_items[0] if backup_items else None,
            "version": version,
        }
    with connect_db() as conn:
        journal_mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        synchronous = conn.execute("PRAGMA synchronous").fetchone()[0]
        foreign_keys = bool(conn.execute("PRAGMA foreign_keys").fetchone()[0])
        page_count = int(conn.execute("PRAGMA page_count").fetchone()[0])
        page_size = int(conn.execute("PRAGMA page_size").fetchone()[0])
        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        foreign_key_errors = len(conn.execute("PRAGMA foreign_key_check").fetchall())
        for table in table_names:
            try:
                counts[table] = int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
            except sqlite3.OperationalError:
                counts[table] = 0
    return {
        "engine": "SQLite",
        "path": DB_PATH,
        "filename": os.path.basename(DB_PATH),
        "size": database_file_size(DB_PATH),
        "walSize": database_file_size(f"{DB_PATH}-wal"),
        "shmSize": database_file_size(f"{DB_PATH}-shm"),
        "journalMode": journal_mode,
        "synchronous": synchronous,
        "foreignKeys": foreign_keys,
        "busyTimeoutMs": DB_BUSY_TIMEOUT_MS,
        "pageCount": page_count,
        "pageSize": page_size,
        "estimatedDataSize": page_count * page_size,
        "integrity": integrity,
        "foreignKeyErrors": foreign_key_errors,
        "counts": counts,
        "backupCount": len(backup_items),
        "lastBackup": backup_items[0] if backup_items else None,
    }


def ensure_startup_backup() -> None:
    if USE_POSTGRES:
        return
    if not os.path.exists(DB_PATH):
        return
    ensure_backup_dir()
    marker = datetime.now().strftime("%Y%m%d")
    existing = [item for item in list_database_backups() if marker in item["filename"] and "startup" in item["filename"]]
    if existing:
        return
    create_database_backup("startup")
    prune_database_backups()


def ensure_upload_dirs() -> None:
    os.makedirs(PRODUCT_UPLOAD_DIR, exist_ok=True)


def allowed_product_image(filename: str) -> bool:
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return extension in ALLOWED_PRODUCT_IMAGE_EXTENSIONS


def save_product_image(file_storage) -> dict:
    if not file_storage or not file_storage.filename:
        raise ValueError("Envie uma imagem.")
    if not allowed_product_image(file_storage.filename):
        raise ValueError("Formato inválido. Use JPG, PNG ou WEBP.")
    file_storage.stream.seek(0, os.SEEK_END)
    size = file_storage.stream.tell()
    file_storage.stream.seek(0)
    if size > MAX_PRODUCT_IMAGE_BYTES:
        raise ValueError("Imagem maior que 5MB.")
    extension = file_storage.filename.rsplit(".", 1)[-1].lower()
    base_name = secure_filename(file_storage.filename.rsplit(".", 1)[0]) or "produto"
    file_storage.stream.seek(0)
    if USE_CLOUDINARY:
        try:
            import cloudinary
            import cloudinary.uploader
        except ImportError as exc:
            raise ValueError("Cloudinary nao instalado. Verifique requirements.txt e refaca o deploy.") from exc
        config = {"secure": True}
        if VALID_CLOUDINARY_URL:
            os.environ["CLOUDINARY_URL"] = CLOUDINARY_URL
        elif CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET:
            config.update({
                "cloud_name": CLOUDINARY_CLOUD_NAME,
                "api_key": CLOUDINARY_API_KEY,
                "api_secret": CLOUDINARY_API_SECRET,
            })
        cloudinary.config(**config)
        result = cloudinary.uploader.upload(
            file_storage.stream,
            folder=CLOUDINARY_FOLDER,
            public_id=f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{os.urandom(4).hex()}-{base_name}",
            resource_type="image",
            overwrite=False,
        )
        return {
            "url": result.get("secure_url") or result.get("url", ""),
            "filename": result.get("public_id", base_name),
            "size": size,
            "storage": "cloudinary",
        }
    ensure_upload_dirs()
    filename = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{os.urandom(4).hex()}-{base_name}.{extension}"
    path = os.path.join(PRODUCT_UPLOAD_DIR, filename)
    file_storage.save(path)
    return {"url": f"/uploads/products/{filename}", "filename": filename, "size": os.path.getsize(path), "storage": "local"}


def initial_admin_password() -> str:
    return os.environ.get("MOVA_ADMIN_PASSWORD", "").strip()


def initial_admin_user() -> dict:
    return {
        "id": "admin",
        "name": os.environ.get("MOVA_ADMIN_NAME", "Administrador").strip() or "Administrador",
        "login": os.environ.get("MOVA_ADMIN_LOGIN", "admin").strip() or "admin",
        "role": "admin",
        "active": True,
    }


def default_state() -> dict:
    return {
        "users": [initial_admin_user()],
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


SENSITIVE_CREDENTIAL_KEYS = {"password", "password_hash"}


class LegacyUsersWithoutHashesError(RuntimeError):
    pass


def sanitize_credentials(value):
    if isinstance(value, dict):
        return {
            key: sanitize_credentials(item)
            for key, item in value.items()
            if str(key).lower() not in SENSITIVE_CREDENTIAL_KEYS
        }
    if isinstance(value, list):
        return [sanitize_credentials(item) for item in value]
    return value


def password_hash_is_structurally_valid(value: str | None) -> bool:
    parts = str(value or "").split("$")
    return len(parts) == 3 and all(parts)


def password_matches(stored_hash: str | None, candidate: str) -> bool:
    if not password_hash_is_structurally_valid(stored_hash):
        app.logger.warning("Autenticacao bloqueada: usuario sem password_hash valido.")
        return False
    try:
        return check_password_hash(str(stored_hash), candidate)
    except (TypeError, ValueError):
        app.logger.warning("Autenticacao bloqueada: usuario sem password_hash valido.")
        return False


@app.errorhandler(LegacyUsersWithoutHashesError)
def handle_legacy_users_without_hashes(_error):
    app.logger.warning("Operacao bloqueada: tabela users vazia com estado legado de usuarios.")
    return jsonify({
        "ok": False,
        "error": "O cadastro de usuarios requer verificacao administrativa antes desta operacao.",
    }), 409


def init_db() -> None:
    with connect_db() as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS stores (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "INSERT OR IGNORE INTO stores (id, name, created_at) VALUES (?, ?, ?)",
            ("matriz", "Loja Matriz", utc_now()),
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS app_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                data TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        exists = conn.execute("SELECT id FROM app_state WHERE id = 1").fetchone()
        app_state_created = not bool(exists)
        if app_state_created:
            conn.execute(
                "INSERT INTO app_state (id, data, updated_at) VALUES (1, ?, ?)",
                (json.dumps(default_state(), ensure_ascii=False), utc_now()),
            )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                store_id TEXT NOT NULL,
                name TEXT NOT NULL,
                login TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'operator',
                active INTEGER NOT NULL DEFAULT 1,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (store_id) REFERENCES stores(id)
            )
            """
        )
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_store_login ON users(store_id, login)")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_logs (
                id TEXT PRIMARY KEY,
                store_id TEXT NOT NULL,
                user_id TEXT,
                user_name TEXT,
                user_role TEXT,
                action TEXT NOT NULL,
                module TEXT NOT NULL,
                ref_id TEXT,
                details TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (store_id) REFERENCES stores(id)
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_store_created ON audit_logs(store_id, created_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_module ON audit_logs(module)")
        state_row = conn.execute("SELECT data FROM app_state WHERE id = 1").fetchone()
        try:
            state = json.loads(state_row["data"]) if state_row else default_state()
        except json.JSONDecodeError:
            state = default_state()
        users_count = conn.execute("SELECT COUNT(*) AS total FROM users").fetchone()["total"]
        if users_count == 0:
            if app_state_created:
                create_initial_admin_user(conn)
            elif state.get("users"):
                app.logger.warning(
                    "Bootstrap de usuarios bloqueado: tabela users vazia com estado legado."
                )
            else:
                app.logger.warning(
                    "Bootstrap de usuarios bloqueado: banco existente sem usuarios autoritativos."
                )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS brands (
                id TEXT PRIMARY KEY,
                store_id TEXT NOT NULL,
                name TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (store_id) REFERENCES stores(id)
            )
            """
        )
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_brands_store_name ON brands(store_id, name)")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id TEXT PRIMARY KEY,
                store_id TEXT NOT NULL,
                name TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (store_id) REFERENCES stores(id)
            )
            """
        )
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_categories_store_name ON categories(store_id, name)")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS suppliers (
                id TEXT PRIMARY KEY,
                store_id TEXT NOT NULL,
                name TEXT NOT NULL,
                cnpj TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (store_id) REFERENCES stores(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS customers (
                id TEXT PRIMARY KEY,
                store_id TEXT NOT NULL,
                code TEXT,
                name TEXT NOT NULL,
                cpf TEXT,
                rg TEXT,
                birth TEXT,
                whatsapp TEXT,
                email TEXT,
                address TEXT,
                city TEXT,
                district TEXT,
                zip TEXT,
                credit_limit REAL NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'active',
                updated_at TEXT NOT NULL,
                FOREIGN KEY (store_id) REFERENCES stores(id)
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_customers_store_name ON customers(store_id, name)")
        conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_customers_store_cpf
            ON customers(store_id, cpf)
            WHERE cpf IS NOT NULL AND cpf <> ''
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                store_id TEXT NOT NULL,
                barcode TEXT,
                name TEXT NOT NULL,
                size TEXT,
                color TEXT,
                gender TEXT,
                category_name TEXT,
                brand_name TEXT,
                stock INTEGER NOT NULL DEFAULT 0,
                min_stock INTEGER NOT NULL DEFAULT 0,
                description TEXT,
                active INTEGER NOT NULL DEFAULT 1,
                cost REAL NOT NULL DEFAULT 0,
                price REAL NOT NULL DEFAULT 0,
                photo TEXT,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (store_id) REFERENCES stores(id)
            )
            """
        )
        conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_products_store_barcode
            ON products(store_id, barcode)
            WHERE barcode IS NOT NULL AND barcode <> ''
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sales (
                id TEXT PRIMARY KEY,
                store_id TEXT NOT NULL,
                customer_id TEXT,
                customer_name TEXT NOT NULL,
                subtotal REAL NOT NULL DEFAULT 0,
                discount REAL NOT NULL DEFAULT 0,
                total REAL NOT NULL DEFAULT 0,
                cost_total REAL NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'completed',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (store_id) REFERENCES stores(id)
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sales_store_created ON sales(store_id, created_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sales_customer ON sales(customer_id)")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sale_items (
                id TEXT PRIMARY KEY,
                sale_id TEXT NOT NULL,
                product_id TEXT,
                barcode TEXT,
                name TEXT NOT NULL,
                brand TEXT,
                quantity INTEGER NOT NULL DEFAULT 1,
                unit_cost REAL NOT NULL DEFAULT 0,
                unit_price REAL NOT NULL DEFAULT 0,
                total REAL NOT NULL DEFAULT 0,
                FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sale_items_sale ON sale_items(sale_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sale_items_product ON sale_items(product_id)")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sale_payments (
                id TEXT PRIMARY KEY,
                sale_id TEXT NOT NULL,
                method TEXT NOT NULL,
                amount REAL NOT NULL DEFAULT 0,
                installments INTEGER NOT NULL DEFAULT 1,
                status TEXT NOT NULL DEFAULT 'registered',
                created_at TEXT NOT NULL,
                FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sale_payments_sale ON sale_payments(sale_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sale_payments_method ON sale_payments(method)")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cash_movements (
                id TEXT PRIMARY KEY,
                store_id TEXT NOT NULL,
                direction TEXT NOT NULL,
                type TEXT,
                description TEXT,
                method TEXT,
                amount REAL NOT NULL DEFAULT 0,
                ref_id TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (store_id) REFERENCES stores(id)
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_cash_store_created ON cash_movements(store_id, created_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_cash_method ON cash_movements(method)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_cash_ref ON cash_movements(ref_id)")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cash_closings (
                id TEXT PRIMARY KEY,
                store_id TEXT NOT NULL,
                date TEXT NOT NULL,
                expected_cash REAL NOT NULL DEFAULT 0,
                informed_cash REAL NOT NULL DEFAULT 0,
                difference REAL NOT NULL DEFAULT 0,
                total_balance REAL NOT NULL DEFAULT 0,
                cash_in REAL NOT NULL DEFAULT 0,
                cash_out REAL NOT NULL DEFAULT 0,
                notes TEXT,
                user_id TEXT,
                user_name TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (store_id) REFERENCES stores(id)
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_cash_closings_store_date ON cash_closings(store_id, date)")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS receivables (
                id TEXT PRIMARY KEY,
                store_id TEXT NOT NULL,
                sale_id TEXT,
                customer_id TEXT,
                customer_name TEXT,
                method TEXT NOT NULL,
                amount REAL NOT NULL DEFAULT 0,
                received REAL NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'open',
                due_date TEXT,
                paid_at TEXT,
                last_payment_at TEXT,
                installment TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (store_id) REFERENCES stores(id)
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_receivables_store_due ON receivables(store_id, due_date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_receivables_status ON receivables(status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_receivables_sale ON receivables(sale_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_receivables_customer ON receivables(customer_id)")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS receivable_payments (
                id TEXT PRIMARY KEY,
                store_id TEXT NOT NULL,
                receivable_id TEXT NOT NULL,
                sale_id TEXT,
                customer_id TEXT,
                method TEXT NOT NULL,
                amount REAL NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                note TEXT,
                FOREIGN KEY (store_id) REFERENCES stores(id),
                FOREIGN KEY (receivable_id) REFERENCES receivables(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_receivable_payments_receivable ON receivable_payments(receivable_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_receivable_payments_customer ON receivable_payments(store_id, customer_id, created_at)")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sale_returns (
                id TEXT PRIMARY KEY,
                store_id TEXT NOT NULL,
                sale_id TEXT NOT NULL,
                customer_name TEXT,
                total REAL NOT NULL DEFAULT 0,
                reason TEXT,
                notes TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (store_id) REFERENCES stores(id)
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_returns_store_created ON sale_returns(store_id, created_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_returns_sale ON sale_returns(sale_id)")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sale_return_items (
                id TEXT PRIMARY KEY,
                return_id TEXT NOT NULL,
                product_id TEXT,
                product_name TEXT,
                action TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                unit_price REAL NOT NULL DEFAULT 0,
                total REAL NOT NULL DEFAULT 0,
                FOREIGN KEY (return_id) REFERENCES sale_returns(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_return_items_return ON sale_return_items(return_id)")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS payables (
                id TEXT PRIMARY KEY,
                store_id TEXT NOT NULL,
                supplier TEXT,
                category TEXT NOT NULL,
                amount REAL NOT NULL DEFAULT 0,
                issue_date TEXT,
                due_date TEXT NOT NULL,
                notes TEXT,
                paid_amount REAL NOT NULL DEFAULT 0,
                fee REAL NOT NULL DEFAULT 0,
                discount REAL NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'pending',
                paid_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (store_id) REFERENCES stores(id)
            )
            """
        )
        if USE_POSTGRES:
            conn.execute("ALTER TABLE payables ADD COLUMN IF NOT EXISTS discount REAL NOT NULL DEFAULT 0")
        else:
            payable_columns = {row["name"] for row in conn.execute("PRAGMA table_info(payables)").fetchall()}
            if "discount" not in payable_columns:
                conn.execute("ALTER TABLE payables ADD COLUMN discount REAL NOT NULL DEFAULT 0")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_payables_store_due ON payables(store_id, due_date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_payables_status ON payables(status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_payables_supplier ON payables(supplier)")
        row = conn.execute("SELECT data FROM app_state WHERE id = 1").fetchone()
        products_count = conn.execute("SELECT COUNT(*) AS total FROM products").fetchone()["total"]
        customers_count = conn.execute("SELECT COUNT(*) AS total FROM customers").fetchone()["total"]
        sales_count = conn.execute("SELECT COUNT(*) AS total FROM sales").fetchone()["total"]
        cash_count = conn.execute("SELECT COUNT(*) AS total FROM cash_movements").fetchone()["total"]
        receivables_count = conn.execute("SELECT COUNT(*) AS total FROM receivables").fetchone()["total"]
        payables_count = conn.execute("SELECT COUNT(*) AS total FROM payables").fetchone()["total"]
        if row and products_count == 0 and customers_count == 0 and sales_count == 0 and cash_count == 0 and receivables_count == 0 and payables_count == 0:
            try:
                sync_business_tables(conn, json.loads(row["data"]))
            except json.JSONDecodeError:
                sync_business_tables(conn, default_state())


def create_initial_admin_user(conn: sqlite3.Connection, store_id: str = "matriz") -> bool:
    now = utc_now()
    user = initial_admin_user()
    password = initial_admin_password()
    if not password:
        app.logger.error(
            "Administrador inicial nao criado: configure MOVA_ADMIN_PASSWORD antes do primeiro acesso."
        )
        return False
    conn.execute(
        """
        INSERT INTO users (id, store_id, name, login, password_hash, role, active, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user["id"],
            store_id,
            user["name"],
            user["login"],
            generate_password_hash(password),
            user["role"],
            1,
            now,
        ),
    )
    return True


def public_user(row: sqlite3.Row | dict) -> dict:
    return {
        "id": row["id"],
        "name": row["name"],
        "login": row["login"],
        "role": row["role"],
        "active": bool(row["active"]),
    }


def sanitize_audit_value(value):
    if isinstance(value, dict):
        sanitized = {}
        for key, item in value.items():
            lowered = str(key).lower()
            if lowered in {"password", "password_hash"}:
                sanitized[key] = "[removido]"
            elif lowered == "photo" and isinstance(item, str) and len(item) > 180:
                sanitized[key] = "[imagem]"
            else:
                sanitized[key] = sanitize_audit_value(item)
        return sanitized
    if isinstance(value, list):
        return [sanitize_audit_value(item) for item in value[:50]]
    if isinstance(value, str) and len(value) > 600:
        return value[:600] + "...[cortado]"
    return value


def record_audit(action: str, module: str, ref_id: str = "", details: dict | None = None, conn: sqlite3.Connection | None = None) -> None:
    user = session.get("user") or {}
    payload = (
        os.urandom(16).hex(),
        "matriz",
        user.get("id", ""),
        user.get("name", ""),
        user.get("role", ""),
        action,
        module,
        ref_id,
        json.dumps(sanitize_audit_value(details or {}), ensure_ascii=False),
        utc_now(),
    )
    sql = """
        INSERT INTO audit_logs (
            id, store_id, user_id, user_name, user_role, action, module, ref_id, details, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    if conn is not None:
        conn.execute(sql, payload)
        return
    with connect_db() as audit_conn:
        audit_conn.execute(sql, payload)


def require_admin() -> tuple[dict | None, tuple | None]:
    user = session.get("user")
    if not user:
        return None, (jsonify({"ok": False, "error": "Login obrigatório."}), 401)
    if user.get("role") != "admin":
        return None, (jsonify({"ok": False, "error": "Apenas administrador pode realizar esta ação."}), 403)
    return user, None


def require_data_import_reset_permission(operation: str) -> tuple[dict | None, tuple | None]:
    current_user = session.get("user")
    user, error_response = require_admin()
    if error_response:
        reason = "unauthenticated" if not current_user else "not_admin"
        log_blocked_data_operation(operation, reason)
        return None, error_response
    reason = data_import_reset_denial_reason(user)
    if reason:
        log_blocked_data_operation(operation, reason)
        return None, (jsonify({"ok": False, "error": "Operação indisponível neste ambiente."}), 403)
    return user, None


def normalize_user_payload(payload: dict, existing: dict | None = None) -> dict:
    now = utc_now()
    existing = existing or {}
    return {
        "id": payload.get("id") or existing.get("id") or os.urandom(16).hex(),
        "name": str(payload.get("name", existing.get("name", ""))).strip(),
        "login": str(payload.get("login", existing.get("login", ""))).strip(),
        "password": str(payload.get("password", "") or ""),
        "role": str(payload.get("role", existing.get("role", "operator")) or "operator").strip(),
        "active": bool(payload.get("active", existing.get("active", True))),
        "updatedAt": now,
    }


def validate_user_payload(user: dict, creating: bool = False) -> str | None:
    if not user["name"]:
        return "Nome do usuário é obrigatório."
    if not user["login"]:
        return "Login do usuário é obrigatório."
    if user["role"] not in {"admin", "operator"}:
        return "Perfil de usuário inválido."
    if creating and not user["password"]:
        return "Senha é obrigatória."
    password_error = validate_password_strength(user["password"])
    if password_error:
        return password_error
    return None


def write_app_state_only(state: dict) -> str:
    updated_at = utc_now()
    with connect_db() as conn:
        state_to_store = prepare_state_for_storage(conn, state)
        conn.execute(
            """
            INSERT INTO app_state (id, data, updated_at)
            VALUES (1, ?, ?)
            ON CONFLICT(id) DO UPDATE SET data = excluded.data, updated_at = excluded.updated_at
            """,
            (json.dumps(state_to_store, ensure_ascii=False), updated_at),
        )
    return updated_at


def sync_user_to_state(user: dict | None = None, deleted_id: str | None = None) -> None:
    state, _ = read_state()
    # A tabela users ja foi atualizada pelo endpoint especifico. O app_state
    # recebe apenas o snapshot publico preparado pela fronteira de persistencia.
    write_app_state_only(state)


def sync_business_tables(conn: sqlite3.Connection, state: dict, store_id: str = "matriz") -> None:
    now = utc_now()
    conn.execute("DELETE FROM sale_return_items WHERE return_id IN (SELECT id FROM sale_returns WHERE store_id = ?)", (store_id,))
    conn.execute("DELETE FROM sale_returns WHERE store_id = ?", (store_id,))
    conn.execute("DELETE FROM cash_closings WHERE store_id = ?", (store_id,))
    conn.execute("DELETE FROM cash_movements WHERE store_id = ?", (store_id,))
    conn.execute("DELETE FROM receivable_payments WHERE store_id = ?", (store_id,))
    conn.execute("DELETE FROM receivables WHERE store_id = ?", (store_id,))
    conn.execute("DELETE FROM payables WHERE store_id = ?", (store_id,))
    conn.execute("DELETE FROM sale_payments WHERE sale_id IN (SELECT id FROM sales WHERE store_id = ?)", (store_id,))
    conn.execute("DELETE FROM sale_items WHERE sale_id IN (SELECT id FROM sales WHERE store_id = ?)", (store_id,))
    conn.execute("DELETE FROM sales WHERE store_id = ?", (store_id,))
    conn.execute("DELETE FROM products WHERE store_id = ?", (store_id,))
    conn.execute("DELETE FROM customers WHERE store_id = ?", (store_id,))
    conn.execute("DELETE FROM suppliers WHERE store_id = ?", (store_id,))
    conn.execute("DELETE FROM brands WHERE store_id = ?", (store_id,))
    conn.execute("DELETE FROM categories WHERE store_id = ?", (store_id,))

    for name in sorted({item for item in state.get("brands", []) if item}):
        conn.execute(
            "INSERT INTO brands (id, store_id, name, updated_at) VALUES (?, ?, ?, ?)",
            (f"{store_id}:brand:{name.casefold()}", store_id, name, now),
        )

    for name in sorted({item for item in state.get("categories", []) if item}):
        conn.execute(
            "INSERT INTO categories (id, store_id, name, updated_at) VALUES (?, ?, ?, ?)",
            (f"{store_id}:category:{name.casefold()}", store_id, name, now),
        )

    for supplier in state.get("suppliers", []):
        conn.execute(
            """
            INSERT INTO suppliers (id, store_id, name, cnpj, phone, email, address, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                supplier.get("id"),
                store_id,
                supplier.get("name", ""),
                supplier.get("cnpj", ""),
                supplier.get("phone", ""),
                supplier.get("email", ""),
                supplier.get("address", ""),
                supplier.get("updatedAt", now),
            ),
        )

    for sale in state.get("sales", []):
        conn.execute(
            """
            INSERT INTO sales (
                id, store_id, customer_id, customer_name, subtotal, discount,
                total, cost_total, status, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                sale.get("id"),
                store_id,
                sale.get("customerId", ""),
                sale.get("customerName", "Venda simples"),
                float(sale.get("subtotal") or 0),
                float(sale.get("discount") or 0),
                float(sale.get("total") or 0),
                float(sale.get("costTotal") or 0),
                sale.get("status", "completed"),
                sale.get("createdAt", now),
                sale.get("updatedAt", sale.get("createdAt", now)),
            ),
        )
        for index, item in enumerate(sale.get("items", []), start=1):
            conn.execute(
                """
                INSERT INTO sale_items (
                    id, sale_id, product_id, barcode, name, brand, quantity,
                    unit_cost, unit_price, total
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    f"{sale.get('id')}:item:{index}",
                    sale.get("id"),
                    item.get("productId", ""),
                    item.get("barcode", ""),
                    item.get("name", ""),
                    item.get("brand", ""),
                    int(item.get("quantity") or 0),
                    float(item.get("unitCost") or 0),
                    float(item.get("unitPrice") or 0),
                    float(item.get("total") or 0),
                ),
            )
        for index, payment in enumerate(sale.get("payments", []), start=1):
            conn.execute(
                """
                INSERT INTO sale_payments (id, sale_id, method, amount, installments, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    f"{sale.get('id')}:payment:{index}",
                    sale.get("id"),
                    payment.get("method", ""),
                    float(payment.get("amount") or 0),
                    int(payment.get("installments") or 1),
                    payment.get("status", "registered"),
                    sale.get("createdAt", now),
                ),
            )

    for return_doc in state.get("returns", []):
        conn.execute(
            """
            INSERT INTO sale_returns (id, store_id, sale_id, customer_name, total, reason, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                return_doc.get("id"),
                store_id,
                return_doc.get("saleId", ""),
                return_doc.get("customerName", ""),
                float(return_doc.get("total") or 0),
                return_doc.get("reason", ""),
                return_doc.get("notes", ""),
                return_doc.get("createdAt", now),
            ),
        )
        for index, item in enumerate(return_doc.get("items", []), start=1):
            conn.execute(
                """
                INSERT INTO sale_return_items (
                    id, return_id, product_id, product_name, action, quantity, unit_price, total
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    f"{return_doc.get('id')}:item:{index}",
                    return_doc.get("id"),
                    item.get("productId", ""),
                    item.get("productName", ""),
                    item.get("action", ""),
                    int(item.get("quantity") or 0),
                    float(item.get("unitPrice") or 0),
                    float(item.get("total") or 0),
                ),
            )

    for movement in state.get("cash", []):
        conn.execute(
            """
            INSERT INTO cash_movements (
                id, store_id, direction, type, description, method, amount, ref_id, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                movement.get("id"),
                store_id,
                movement.get("direction", ""),
                movement.get("type", ""),
                movement.get("description", ""),
                movement.get("method", ""),
                float(movement.get("amount") or 0),
                movement.get("refId", ""),
                movement.get("createdAt", now),
            ),
        )

    for closing in state.get("cashClosings", []):
        conn.execute(
            """
            INSERT INTO cash_closings (
                id, store_id, date, expected_cash, informed_cash, difference, total_balance,
                cash_in, cash_out, notes, user_id, user_name, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                closing.get("id"),
                store_id,
                closing.get("date", ""),
                float(closing.get("expectedCash") or 0),
                float(closing.get("informedCash") or 0),
                float(closing.get("difference") or 0),
                float(closing.get("totalBalance") or 0),
                float(closing.get("cashIn") or 0),
                float(closing.get("cashOut") or 0),
                closing.get("notes", ""),
                closing.get("userId", ""),
                closing.get("userName", ""),
                closing.get("createdAt", now),
            ),
        )

    for receivable in state.get("receivables", []):
        conn.execute(
            """
            INSERT INTO receivables (
                id, store_id, sale_id, customer_id, customer_name, method, amount,
                received, status, due_date, paid_at, last_payment_at, installment,
                created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                receivable.get("id"),
                store_id,
                receivable.get("saleId", ""),
                receivable.get("customerId", ""),
                receivable.get("customerName", ""),
                receivable.get("method", ""),
                float(receivable.get("amount") or 0),
                float(receivable.get("received") or 0),
                receivable.get("status", "open"),
                receivable.get("dueDate", ""),
                receivable.get("paidAt", ""),
                receivable.get("lastPaymentAt", ""),
                str(receivable.get("installment", "")),
                receivable.get("createdAt", now),
                receivable.get("updatedAt", receivable.get("lastPaymentAt", receivable.get("paidAt", receivable.get("createdAt", now)))),
            ),
        )
        for index, payment in enumerate(receivable.get("payments", []) or [], start=1):
            payment_id = payment.get("id") or f"{receivable.get('id')}:payment:{index}"
            conn.execute(
                """
                INSERT INTO receivable_payments (
                    id, store_id, receivable_id, sale_id, customer_id, method, amount, created_at, note
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payment_id,
                    store_id,
                    receivable.get("id"),
                    receivable.get("saleId", ""),
                    receivable.get("customerId", ""),
                    payment.get("method", receivable.get("method", "")),
                    float(payment.get("amount") or 0),
                    payment.get("createdAt", receivable.get("lastPaymentAt", receivable.get("paidAt", now))),
                    payment.get("note", ""),
                ),
            )

    for payable in state.get("payables", []):
        conn.execute(
            """
            INSERT INTO payables (
                id, store_id, supplier, category, amount, issue_date, due_date,
                notes, paid_amount, fee, discount, status, paid_at, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payable.get("id"),
                store_id,
                payable.get("supplier", ""),
                payable.get("category", ""),
                float(payable.get("amount") or 0),
                payable.get("issueDate", ""),
                payable.get("dueDate", ""),
                payable.get("notes", ""),
                float(payable.get("paidAmount") or 0),
                float(payable.get("fee") or 0),
                float(payable.get("discount") or 0),
                payable.get("status", "pending"),
                payable.get("paidAt", ""),
                payable.get("createdAt", now),
                payable.get("updatedAt", payable.get("paidAt", payable.get("createdAt", now))),
            ),
        )

    for customer in state.get("customers", []):
        conn.execute(
            """
            INSERT INTO customers (
                id, store_id, code, name, cpf, rg, birth, whatsapp, email, address,
                city, district, zip, credit_limit, status, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                customer.get("id"),
                store_id,
                customer.get("code", ""),
                customer.get("name", ""),
                customer.get("cpf", ""),
                customer.get("rg", ""),
                customer.get("birth", ""),
                customer.get("whatsapp", ""),
                customer.get("email", ""),
                customer.get("address", ""),
                customer.get("city", ""),
                customer.get("district", ""),
                customer.get("zip", ""),
                float(customer.get("limit") or 0),
                customer.get("status", "active"),
                customer.get("updatedAt", now),
            ),
        )

    for product in state.get("products", []):
        conn.execute(
            """
            INSERT INTO products (
                id, store_id, barcode, name, size, color, gender, category_name, brand_name,
                stock, min_stock, description, active, cost, price, photo, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                product.get("id"),
                store_id,
                product.get("barcode", ""),
                product.get("name", ""),
                product.get("size", ""),
                product.get("color", ""),
                product.get("gender", ""),
                product.get("category", ""),
                product.get("brand", ""),
                int(product.get("stock") or 0),
                int(product.get("minStock") or 0),
                product.get("description", ""),
                1 if product.get("active", True) else 0,
                float(product.get("cost") or 0),
                float(product.get("price") or 0),
                product.get("photo", ""),
                product.get("updatedAt", now),
            ),
        )


def read_state() -> tuple[dict, str]:
    init_db()
    with connect_db() as conn:
        row = conn.execute("SELECT data, updated_at FROM app_state WHERE id = 1").fetchone()
        if not row:
            state = default_state()
            state["users"] = users_state_from_db(conn)
            return state, utc_now()
        try:
            state = json.loads(row["data"])
        except json.JSONDecodeError:
            state = default_state()
        merged = {**default_state(), **state}
        merged["users"] = users_state_from_db(conn)
        return merged, row["updated_at"]


def write_state(state: dict) -> str:
    init_db()
    updated_at = utc_now()
    with connect_db() as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        state_to_store = prepare_state_for_storage(conn, state)
        conn.execute(
            """
            INSERT INTO app_state (id, data, updated_at)
            VALUES (1, ?, ?)
            ON CONFLICT(id) DO UPDATE SET data = excluded.data, updated_at = excluded.updated_at
            """,
            (json.dumps(state_to_store, ensure_ascii=False), updated_at),
        )
        sync_business_tables(conn, state_to_store)
    return updated_at


def users_state_from_db(conn: sqlite3.Connection, store_id: str = "matriz") -> list[dict]:
    rows = conn.execute(
        """
        SELECT id, name, login, role, active
        FROM users
        WHERE store_id = ?
        ORDER BY name COLLATE NOCASE
        """,
        (store_id,),
    ).fetchall()
    return [
        {
            "id": row["id"],
            "name": row["name"],
            "login": row["login"],
            "role": row["role"],
            "active": bool(row["active"]),
        }
        for row in rows
    ]


def stored_app_state_from_connection(conn) -> dict:
    row = conn.execute("SELECT data FROM app_state WHERE id = 1").fetchone()
    if not row:
        return default_state()
    try:
        value = json.loads(row["data"])
    except json.JSONDecodeError:
        return default_state()
    return value if isinstance(value, dict) else default_state()


def prepare_state_for_storage(conn, state: dict, store_id: str = "matriz") -> dict:
    existing_state = stored_app_state_from_connection(conn)
    legacy_users = existing_state.get("users") if isinstance(existing_state.get("users"), list) else []
    public_users = users_state_from_db(conn, store_id)
    if not public_users and legacy_users:
        raise LegacyUsersWithoutHashesError()

    protected_users = []
    for public_user_data in public_users:
        legacy_user = next((
            item for item in legacy_users
            if isinstance(item, dict) and (
                item.get("id") == public_user_data["id"]
                or item.get("login") == public_user_data["login"]
            )
        ), {})
        protected = dict(public_user_data)
        for key, value in legacy_user.items():
            if str(key).lower() in SENSITIVE_CREDENTIAL_KEYS:
                protected[key] = value
        protected_users.append(protected)

    incoming_state = sanitize_credentials(state if isinstance(state, dict) else {})
    prepared = {**default_state(), **incoming_state}
    prepared["users"] = protected_users
    return prepared


def reset_business_data(store_id: str = "matriz") -> tuple[str, dict]:
    updated_at = utc_now()
    with connect_db() as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        users = users_state_from_db(conn, store_id)
        empty_state = prepare_state_for_storage(conn, {**default_state(), "users": users}, store_id)
        conn.execute("DELETE FROM sale_return_items WHERE return_id IN (SELECT id FROM sale_returns WHERE store_id = ?)", (store_id,))
        conn.execute("DELETE FROM sale_returns WHERE store_id = ?", (store_id,))
        conn.execute("DELETE FROM cash_closings WHERE store_id = ?", (store_id,))
        conn.execute("DELETE FROM cash_movements WHERE store_id = ?", (store_id,))
        conn.execute("DELETE FROM receivable_payments WHERE store_id = ?", (store_id,))
        conn.execute("DELETE FROM receivables WHERE store_id = ?", (store_id,))
        conn.execute("DELETE FROM payables WHERE store_id = ?", (store_id,))
        conn.execute("DELETE FROM sale_payments WHERE sale_id IN (SELECT id FROM sales WHERE store_id = ?)", (store_id,))
        conn.execute("DELETE FROM sale_items WHERE sale_id IN (SELECT id FROM sales WHERE store_id = ?)", (store_id,))
        conn.execute("DELETE FROM sales WHERE store_id = ?", (store_id,))
        conn.execute("DELETE FROM products WHERE store_id = ?", (store_id,))
        conn.execute("DELETE FROM customers WHERE store_id = ?", (store_id,))
        conn.execute("DELETE FROM suppliers WHERE store_id = ?", (store_id,))
        conn.execute("DELETE FROM brands WHERE store_id = ?", (store_id,))
        conn.execute("DELETE FROM categories WHERE store_id = ?", (store_id,))
        conn.execute(
            """
            INSERT INTO app_state (id, data, updated_at)
            VALUES (1, ?, ?)
            ON CONFLICT(id) DO UPDATE SET data = excluded.data, updated_at = excluded.updated_at
            """,
            (json.dumps(empty_state, ensure_ascii=False), updated_at),
        )
        record_audit(
            "reset",
            "state",
            "app_state",
            {"updatedAt": updated_at, "preservedUsers": len(empty_state["users"])},
            conn,
        )
    return updated_at, {
        "products": 0,
        "customers": 0,
        "suppliers": 0,
        "brands": 0,
        "categories": 0,
        "sales": 0,
        "receivables": 0,
        "payables": 0,
        "cash": 0,
        "cashClosings": 0,
        "returns": 0,
        "users": len(empty_state["users"]),
    }


def normalize_product_payload(payload: dict, existing: dict | None = None) -> dict:
    now = utc_now()
    existing = existing or {}
    return {
        "id": payload.get("id") or existing.get("id") or os.urandom(16).hex(),
        "barcode": str(payload.get("barcode", existing.get("barcode", ""))).strip(),
        "name": str(payload.get("name", existing.get("name", ""))).strip(),
        "size": str(payload.get("size", existing.get("size", ""))).strip(),
        "color": str(payload.get("color", existing.get("color", ""))).strip(),
        "gender": str(payload.get("gender", existing.get("gender", ""))).strip(),
        "category": str(payload.get("category", existing.get("category", ""))).strip(),
        "brand": str(payload.get("brand", existing.get("brand", ""))).strip(),
        "stock": max(0, int(float(payload.get("stock", existing.get("stock", 0)) or 0))),
        "minStock": max(0, int(float(payload.get("minStock", existing.get("minStock", 0)) or 0))),
        "description": str(payload.get("description", existing.get("description", ""))).strip(),
        "active": bool(payload.get("active", existing.get("active", True))),
        "cost": float(payload.get("cost", existing.get("cost", 0)) or 0),
        "price": float(payload.get("price", existing.get("price", 0)) or 0),
        "photo": payload.get("photo", existing.get("photo", "")) or "",
        "updatedAt": now,
    }


def validate_product(product: dict) -> str | None:
    if not product["barcode"]:
        return "Código de barras é obrigatório."
    if not product["name"]:
        return "Nome do produto é obrigatório."
    return None


def product_from_row(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "barcode": row["barcode"] or "",
        "name": row["name"] or "",
        "size": row["size"] or "",
        "color": row["color"] or "",
        "gender": row["gender"] or "",
        "category": row["category"] or "",
        "brand": row["brand"] or "",
        "stock": int(row["stock"] or 0),
        "minStock": int(row["minStock"] or 0),
        "description": row["description"] or "",
        "active": bool(row["active"]),
        "cost": float(row["cost"] or 0),
        "price": float(row["price"] or 0),
        "photo": row["photo"] or "",
        "updatedAt": row["updatedAt"],
    }


def upsert_product(conn: sqlite3.Connection, product: dict, store_id: str = "matriz") -> None:
    conn.execute(
        """
        INSERT INTO products (
            id, store_id, barcode, name, size, color, gender, category_name, brand_name,
            stock, min_stock, description, active, cost, price, photo, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            barcode = excluded.barcode,
            name = excluded.name,
            size = excluded.size,
            color = excluded.color,
            gender = excluded.gender,
            category_name = excluded.category_name,
            brand_name = excluded.brand_name,
            stock = excluded.stock,
            min_stock = excluded.min_stock,
            description = excluded.description,
            active = excluded.active,
            cost = excluded.cost,
            price = excluded.price,
            photo = excluded.photo,
            updated_at = excluded.updated_at
        """,
        (
            product["id"],
            store_id,
            product["barcode"],
            product["name"],
            product["size"],
            product["color"],
            product["gender"],
            product["category"],
            product["brand"],
            product["stock"],
            product["minStock"],
            product["description"],
            1 if product["active"] else 0,
            product["cost"],
            product["price"],
            product["photo"],
            product["updatedAt"],
        ),
    )


def sync_product_to_state(product: dict | None = None, deleted_id: str | None = None) -> None:
    state, _ = read_state()
    if deleted_id:
        state["products"] = [item for item in state.get("products", []) if item.get("id") != deleted_id]
    elif product:
        products = [item for item in state.get("products", []) if item.get("id") != product["id"]]
        state["products"] = [product, *products]
        if product["brand"] and product["brand"] not in state["brands"]:
            state["brands"].append(product["brand"])
        if product["category"] and product["category"] not in state["categories"]:
            state["categories"].append(product["category"])
    write_app_state_only(state)


def normalize_customer_payload(payload: dict, existing: dict | None = None) -> dict:
    now = utc_now()
    existing = existing or {}
    return {
        "id": payload.get("id") or existing.get("id") or os.urandom(16).hex(),
        "code": str(payload.get("code", existing.get("code", ""))).strip(),
        "name": str(payload.get("name", existing.get("name", ""))).strip(),
        "cpf": str(payload.get("cpf", existing.get("cpf", ""))).strip(),
        "rg": str(payload.get("rg", existing.get("rg", ""))).strip(),
        "birth": str(payload.get("birth", existing.get("birth", ""))).strip(),
        "whatsapp": str(payload.get("whatsapp", existing.get("whatsapp", ""))).strip(),
        "email": str(payload.get("email", existing.get("email", ""))).strip(),
        "address": str(payload.get("address", existing.get("address", ""))).strip(),
        "city": str(payload.get("city", existing.get("city", ""))).strip(),
        "district": str(payload.get("district", existing.get("district", ""))).strip(),
        "zip": str(payload.get("zip", existing.get("zip", ""))).strip(),
        "limit": float(payload.get("limit", existing.get("limit", 0)) or 0),
        "status": str(payload.get("status", existing.get("status", "active")) or "active").strip(),
        "updatedAt": now,
    }


def validate_customer(customer: dict) -> str | None:
    if not customer["name"]:
        return "Nome do cliente é obrigatório."
    if customer["limit"] < 0:
        return "Limite de crédito não pode ser negativo."
    return None


def customer_from_row(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "code": row["code"] or "",
        "name": row["name"] or "",
        "cpf": row["cpf"] or "",
        "rg": row["rg"] or "",
        "birth": row["birth"] or "",
        "whatsapp": row["whatsapp"] or "",
        "email": row["email"] or "",
        "address": row["address"] or "",
        "city": row["city"] or "",
        "district": row["district"] or "",
        "zip": row["zip"] or "",
        "limit": float(row["limit"] or 0),
        "status": row["status"] or "active",
        "updatedAt": row["updatedAt"],
    }


def upsert_customer(conn: sqlite3.Connection, customer: dict, store_id: str = "matriz") -> None:
    conn.execute(
        """
        INSERT INTO customers (
            id, store_id, code, name, cpf, rg, birth, whatsapp, email, address,
            city, district, zip, credit_limit, status, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            code = excluded.code,
            name = excluded.name,
            cpf = excluded.cpf,
            rg = excluded.rg,
            birth = excluded.birth,
            whatsapp = excluded.whatsapp,
            email = excluded.email,
            address = excluded.address,
            city = excluded.city,
            district = excluded.district,
            zip = excluded.zip,
            credit_limit = excluded.credit_limit,
            status = excluded.status,
            updated_at = excluded.updated_at
        """,
        (
            customer["id"],
            store_id,
            customer["code"],
            customer["name"],
            customer["cpf"],
            customer["rg"],
            customer["birth"],
            customer["whatsapp"],
            customer["email"],
            customer["address"],
            customer["city"],
            customer["district"],
            customer["zip"],
            customer["limit"],
            customer["status"],
            customer["updatedAt"],
        ),
    )


def sync_customer_to_state(customer: dict | None = None, deleted_id: str | None = None) -> None:
    state, _ = read_state()
    if deleted_id:
        state["customers"] = [item for item in state.get("customers", []) if item.get("id") != deleted_id]
    elif customer:
        customers = [item for item in state.get("customers", []) if item.get("id") != customer["id"]]
        state["customers"] = [customer, *customers]
    write_app_state_only(state)


def normalize_supplier_payload(payload: dict, existing: dict | None = None) -> dict:
    now = utc_now()
    existing = existing or {}
    return {
        "id": payload.get("id") or existing.get("id") or os.urandom(16).hex(),
        "name": str(payload.get("name", existing.get("name", ""))).strip(),
        "cnpj": str(payload.get("cnpj", existing.get("cnpj", ""))).strip(),
        "phone": str(payload.get("phone", existing.get("phone", ""))).strip(),
        "email": str(payload.get("email", existing.get("email", ""))).strip(),
        "address": str(payload.get("address", existing.get("address", ""))).strip(),
        "updatedAt": now,
    }


def validate_supplier(supplier: dict) -> str | None:
    if not supplier["name"]:
        return "Nome do fornecedor é obrigatório."
    return None


def supplier_from_row(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "name": row["name"] or "",
        "cnpj": row["cnpj"] or "",
        "phone": row["phone"] or "",
        "email": row["email"] or "",
        "address": row["address"] or "",
        "updatedAt": row["updatedAt"],
    }


def upsert_supplier(conn: sqlite3.Connection, supplier: dict, store_id: str = "matriz") -> None:
    conn.execute(
        """
        INSERT INTO suppliers (id, store_id, name, cnpj, phone, email, address, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            name = excluded.name,
            cnpj = excluded.cnpj,
            phone = excluded.phone,
            email = excluded.email,
            address = excluded.address,
            updated_at = excluded.updated_at
        """,
        (
            supplier["id"],
            store_id,
            supplier["name"],
            supplier["cnpj"],
            supplier["phone"],
            supplier["email"],
            supplier["address"],
            supplier["updatedAt"],
        ),
    )


def sync_supplier_to_state(supplier: dict | None = None, deleted_id: str | None = None) -> None:
    state, _ = read_state()
    if deleted_id:
        state["suppliers"] = [item for item in state.get("suppliers", []) if item.get("id") != deleted_id]
    elif supplier:
        suppliers = [item for item in state.get("suppliers", []) if item.get("id") != supplier["id"]]
        state["suppliers"] = [supplier, *suppliers]
    write_app_state_only(state)


def money_round(value: float) -> float:
    return round(float(value or 0) + 0.0000001, 2)


def next_sale_code_db(conn: sqlite3.Connection, store_id: str = "matriz") -> str:
    rows = conn.execute("SELECT id FROM sales WHERE store_id = ?", (store_id,)).fetchall()
    highest = 0
    for row in rows:
        sale_id = str(row["id"] or "")
        if sale_id.upper().startswith("VENDA") and sale_id[5:].isdigit():
            highest = max(highest, int(sale_id[5:]))
    return f"VENDA{highest + 1:03d}"


def next_conditional_code(state: dict) -> str:
    highest = 0
    for item in state.get("conditionals", []) or []:
        conditional_id = str(item.get("id", "") or "")
        if conditional_id.upper().startswith("COND") and conditional_id[4:].isdigit():
            highest = max(highest, int(conditional_id[4:]))
    return f"COND{highest + 1:03d}"


def conditional_reserved_quantities(state: dict, exclude_conditional_id: str = "") -> dict[str, int]:
    reserved: dict[str, int] = {}
    for conditional in state.get("conditionals", []) or []:
        if str(conditional.get("id", "")) == exclude_conditional_id:
            continue
        if conditional.get("status") in {"finalized", "cancelled"}:
            continue
        for item in conditional.get("items", []) or []:
            product_id = str(item.get("productId", "") or "")
            if not product_id:
                continue
            reserved[product_id] = reserved.get(product_id, 0) + max(0, int(float(item.get("quantity", 0) or 0)))
    return reserved


def build_conditional_from_payload(payload: dict, state: dict, conditional_id: str) -> tuple[dict | None, str | None]:
    customer_id = str(payload.get("customerId", "") or "").strip()
    customers = state.get("customers", []) or []
    customer = next((item for item in customers if str(item.get("id", "")) == customer_id), None)
    if not customer:
        return None, "Cliente cadastrado é obrigatório para condicional."

    products_by_id = {str(product.get("id", "")): product for product in (state.get("products", []) or [])}
    reserved_by_product = conditional_reserved_quantities(state, conditional_id)
    requested_by_product: dict[str, int] = {}
    items = []
    for item in payload.get("items") or []:
        product_id = str(item.get("productId", "") or "").strip()
        quantity = max(0, int(float(item.get("quantity", 0) or 0)))
        product = products_by_id.get(product_id)
        if not product or quantity <= 0:
            return None, "Item de condicional inválido."
        requested_by_product[product_id] = requested_by_product.get(product_id, 0) + quantity
        available = int(product.get("stock") or 0) - int(reserved_by_product.get(product_id, 0) or 0)
        if available < requested_by_product[product_id]:
            return None, f"Estoque disponivel insuficiente para {product.get('name', 'produto')}. Existem pecas em condicional."
        unit_price = float(item.get("unitPrice", product.get("price", 0)) or 0)
        unit_cost = float(item.get("unitCost", product.get("cost", 0)) or 0)
        items.append({
            "productId": product_id,
            "barcode": product.get("barcode", ""),
            "name": product.get("name", ""),
            "brand": product.get("brand", ""),
            "quantity": quantity,
            "unitCost": unit_cost,
            "unitPrice": unit_price,
            "total": money_round(quantity * unit_price),
        })
    if not items:
        return None, "Adicione produtos ao condicional."

    now = utc_now()
    return {
        "id": conditional_id,
        "customerId": customer["id"],
        "customerName": customer.get("name", ""),
        "items": items,
        "status": "open",
        "createdAt": str(payload.get("createdAt") or now),
        "updatedAt": now,
    }, None


def parse_iso_datetime(value: str) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        normalized = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except ValueError:
        return datetime.now(timezone.utc)


def date_input_from_datetime(value: datetime) -> str:
    return value.date().isoformat()


def build_sale_from_payload(payload: dict, product_rows: dict[str, sqlite3.Row], sale_id: str, reserved_by_product: dict[str, int] | None = None) -> tuple[dict | None, str | None]:
    created_at = str(payload.get("createdAt") or utc_now())
    reserved_by_product = reserved_by_product or {}
    requested_by_product: dict[str, int] = {}
    items = []
    for index, item in enumerate(payload.get("items") or [], start=1):
        product_id = str(item.get("productId", "")).strip()
        quantity = max(0, int(float(item.get("quantity", 0) or 0)))
        if not product_id or quantity <= 0:
            return None, "Item de venda inválido."
        row = product_rows.get(product_id)
        if not row:
            return None, "Produto não encontrado."
        requested_by_product[product_id] = requested_by_product.get(product_id, 0) + quantity
        available = int(row["stock"] or 0) - int(reserved_by_product.get(product_id, 0) or 0)
        if available < requested_by_product[product_id]:
            return None, f"Estoque disponivel insuficiente para {row['name']}. Existem pecas em condicional."
        unit_price = float(item.get("unitPrice", row["price"]) or 0)
        unit_cost = float(item.get("unitCost", row["cost"]) or 0)
        items.append({
            "productId": product_id,
            "barcode": row["barcode"] or "",
            "name": row["name"] or "",
            "brand": row["brand"] or "",
            "quantity": quantity,
            "unitCost": unit_cost,
            "unitPrice": unit_price,
            "total": money_round(quantity * unit_price),
        })
    if not items:
        return None, "Adicione produtos."

    subtotal = money_round(sum(item["total"] for item in items))
    discount = money_round(payload.get("discount", 0))
    total = money_round(max(0, subtotal - discount))
    payments = [
        {"method": str(payment.get("method", "")).strip(), "amount": money_round(payment.get("amount", 0))}
        for payment in (payload.get("payments") or [])
        if money_round(payment.get("amount", 0)) > 0
    ]
    if money_round(sum(payment["amount"] for payment in payments)) != total:
        return None, "Pagamentos precisam fechar com o total."

    sale = {
        "id": sale_id,
        "customerId": str(payload.get("customerId", "") or ""),
        "customerName": str(payload.get("customerName", "") or "Venda simples"),
        "items": items,
        "subtotal": subtotal,
        "discount": discount,
        "total": total,
        "costTotal": money_round(sum(item["quantity"] * item["unitCost"] for item in items)),
        "payments": payments,
        "status": "completed",
        "createdAt": created_at,
        "updatedAt": created_at,
    }
    return sale, None


def build_financial_from_sale(sale: dict, installments: int = 1) -> tuple[list[dict], list[dict]]:
    cash = []
    receivables = []
    created_at = sale["createdAt"]
    sale_date = parse_iso_datetime(created_at)
    for index, payment in enumerate(sale["payments"], start=1):
        method = payment["method"]
        amount = money_round(payment["amount"])
        if method in {"cash", "pix"}:
            cash.append({
                "id": os.urandom(16).hex(),
                "direction": "in",
                "type": "sale",
                "description": f"Venda {sale['id']}",
                "method": method,
                "amount": amount,
                "refId": sale["id"],
                "createdAt": created_at,
            })
        elif method in {"debit", "credit"}:
            receivables.append({
                "id": os.urandom(16).hex(),
                "saleId": sale["id"],
                "customerId": sale["customerId"],
                "customerName": sale["customerName"],
                "method": method,
                "amount": amount,
                "received": 0,
                "status": "cardPending",
                "dueDate": date_input_from_datetime(sale_date),
                "paidAt": "",
                "lastPaymentAt": "",
                "installment": "",
                "createdAt": created_at,
                "updatedAt": created_at,
            })
        elif method == "storeCredit":
            total_installments = max(1, int(installments or 1))
            part = money_round(amount / total_installments)
            for parcel in range(1, total_installments + 1):
                due = sale_date + timedelta(days=30 * parcel)
                parcel_amount = money_round(amount - part * (total_installments - 1)) if parcel == total_installments else part
                receivables.append({
                    "id": os.urandom(16).hex(),
                    "saleId": sale["id"],
                    "customerId": sale["customerId"],
                    "customerName": sale["customerName"],
                    "method": "storeCredit",
                    "amount": parcel_amount,
                    "received": 0,
                    "status": "open",
                    "dueDate": date_input_from_datetime(due),
                    "paidAt": "",
                    "lastPaymentAt": "",
                    "installment": str(parcel),
                    "createdAt": created_at,
                    "updatedAt": created_at,
                })
    return cash, receivables


def sync_sale_to_state(sale: dict, updated_products: list[dict], cash: list[dict], receivables: list[dict]) -> None:
    state, _ = read_state()
    updated_by_id = {product["id"]: product for product in updated_products}
    state["products"] = [updated_by_id.get(product.get("id"), product) for product in state.get("products", [])]
    known_product_ids = {product.get("id") for product in state["products"]}
    state["products"].extend(product for product in updated_products if product["id"] not in known_product_ids)
    state["sales"] = [sale, *[item for item in state.get("sales", []) if item.get("id") != sale["id"]]]
    state["cash"] = [*cash, *state.get("cash", [])]
    state["receivables"] = [*receivables, *state.get("receivables", [])]
    write_state(state)


def sync_cancel_sale_to_state(sale_id: str, updated_products: list[dict], cash: list[dict]) -> tuple[dict | None, list[dict]]:
    state, _ = read_state()
    sale = None
    for item in state.get("sales", []):
        if item.get("id") == sale_id:
            item["status"] = "cancelled"
            item["updatedAt"] = utc_now()
            sale = item
            break
    updated_by_id = {product["id"]: product for product in updated_products}
    state["products"] = [updated_by_id.get(product.get("id"), product) for product in state.get("products", [])]
    changed_receivables = []
    for receivable in state.get("receivables", []):
        if receivable.get("saleId") == sale_id:
            receivable["status"] = "cancelled"
            receivable["updatedAt"] = utc_now()
            changed_receivables.append(receivable)
    state["cash"] = [*cash, *state.get("cash", [])]
    write_state(state)
    return sale, changed_receivables


def sync_return_to_state(return_doc: dict, updated_products: list[dict]) -> None:
    state, _ = read_state()
    updated_by_id = {product["id"]: product for product in updated_products}
    state["products"] = [updated_by_id.get(product.get("id"), product) for product in state.get("products", [])]
    known_product_ids = {product.get("id") for product in state["products"]}
    state["products"].extend(product for product in updated_products if product["id"] not in known_product_ids)
    state["returns"] = [return_doc, *[item for item in state.get("returns", []) if item.get("id") != return_doc["id"]]]
    write_state(state)


def normalize_cash_movement_payload(payload: dict) -> dict:
    return {
        "id": payload.get("id") or os.urandom(16).hex(),
        "direction": str(payload.get("direction", "in") or "in").strip(),
        "type": str(payload.get("type", "manual") or "manual").strip(),
        "description": str(payload.get("description", "") or "").strip(),
        "method": str(payload.get("method", "") or "").strip(),
        "amount": money_round(payload.get("amount", 0)),
        "refId": str(payload.get("refId", "") or "").strip(),
        "createdAt": str(payload.get("createdAt") or utc_now()),
    }


def payable_from_row(row: sqlite3.Row | dict) -> dict:
    return {
        "id": row["id"],
        "supplier": row["supplier"] or "",
        "category": row["category"] or "",
        "amount": money_round(row["amount"]),
        "issueDate": row["issueDate"] or "",
        "dueDate": row["dueDate"] or "",
        "notes": row["notes"] or "",
        "paidAmount": money_round(row["paidAmount"]),
        "fee": money_round(row["fee"]),
        "discount": money_round(row["discount"] if "discount" in row.keys() else 0),
        "status": row["status"] or "pending",
        "paidAt": row["paidAt"] or "",
        "createdAt": row["createdAt"] or utc_now(),
        "updatedAt": row["updatedAt"] or utc_now(),
    }


def normalize_payable_payload(payload: dict, existing: dict | None = None) -> dict:
    now = utc_now()
    existing = existing or {}
    return {
        "id": str(payload.get("id") or existing.get("id") or os.urandom(16).hex()).strip(),
        "supplier": str(payload.get("supplier", existing.get("supplier", "")) or "").strip(),
        "category": str(payload.get("category", existing.get("category", "")) or "").strip(),
        "amount": money_round(payload.get("amount", existing.get("amount", 0))),
        "issueDate": str(payload.get("issueDate", existing.get("issueDate", "")) or "").strip(),
        "dueDate": str(payload.get("dueDate", existing.get("dueDate", "")) or "").strip(),
        "notes": str(payload.get("notes", existing.get("notes", "")) or "").strip(),
        "paidAmount": money_round(payload.get("paidAmount", existing.get("paidAmount", 0))),
        "fee": money_round(payload.get("fee", existing.get("fee", 0))),
        "discount": money_round(payload.get("discount", existing.get("discount", 0))),
        "status": str(payload.get("status", existing.get("status", "pending")) or "pending").strip(),
        "paidAt": str(payload.get("paidAt", existing.get("paidAt", "")) or "").strip(),
        "createdAt": str(payload.get("createdAt", existing.get("createdAt", now)) or now),
        "updatedAt": now,
    }


def validate_payable(payable: dict) -> str | None:
    if not payable["category"]:
        return "Categoria é obrigatória."
    if payable["amount"] <= 0:
        return "Valor deve ser maior que zero."
    if not payable["dueDate"]:
        return "Data de vencimento é obrigatória."
    if payable["status"] not in {"pending", "paid", "cancelled"}:
        return "Status inválido."
    return None


def payable_total_due(payable: dict) -> float:
    return money_round(float(payable.get("amount") or 0) + float(payable.get("fee") or 0) - float(payable.get("discount") or 0))


def payable_open_amount(payable: dict) -> float:
    if payable.get("status") == "cancelled":
        return 0
    return max(0, money_round(payable_total_due(payable) - float(payable.get("paidAmount") or 0)))


def parse_date_input(value: str, fallback: str | None = None) -> str:
    if value:
        try:
            return datetime.fromisoformat(str(value)[:10]).date().isoformat()
        except ValueError:
            pass
    return fallback or datetime.now().date().isoformat()


def date_span(end_date: str, days: int) -> list[str]:
    end = datetime.fromisoformat(end_date).date()
    start = end - timedelta(days=max(1, days) - 1)
    return [(start + timedelta(days=index)).isoformat() for index in range(max(1, days))]


def receivable_open_amount(receivable: dict) -> float:
    if receivable.get("status") == "cancelled":
        return 0
    return max(0, money_round(float(receivable.get("amount") or 0) - float(receivable.get("received") or 0)))


def payable_dashboard_status(payable: dict, today: str) -> str:
    if payable.get("status") == "paid" or payable_open_amount(payable) <= 0.01:
        return "paid"
    due_date = str(payable.get("dueDate") or "")
    if due_date == today:
        return "today"
    if due_date and due_date < today:
        return "overdue"
    return "pending"


def build_dashboard_summary(state: dict, days: int, today: str) -> dict:
    month = today[:7]
    valid_sales = [sale for sale in state.get("sales", []) if sale.get("status") != "cancelled"]
    today_sales = [sale for sale in valid_sales if str(sale.get("createdAt", ""))[:10] == today]
    month_sales = [sale for sale in valid_sales if str(sale.get("createdAt", ""))[:7] == month]
    today_cash = [item for item in state.get("cash", []) if str(item.get("createdAt", ""))[:10] == today]
    open_payables = [item for item in state.get("payables", []) if payable_dashboard_status(item, today) != "paid"]
    open_receivables = [
        item for item in state.get("receivables", [])
        if item.get("method") == "storeCredit" and item.get("status") != "cancelled" and receivable_open_amount(item) > 0
    ]
    stock_value = sum(float(product.get("stock") or 0) * float(product.get("cost") or 0) for product in state.get("products", []))
    cash_balance = sum(float(item.get("amount") or 0) if item.get("direction") == "in" else -float(item.get("amount") or 0) for item in state.get("cash", []))
    payments = [payment for sale in valid_sales for payment in sale.get("payments", [])]
    payment_total = sum(float(payment.get("amount") or 0) for payment in payments)
    payment_methods = ["cash", "pix", "debit", "credit", "storeCredit"]
    payment_rows = []
    for method in payment_methods:
        amount = sum(float(payment.get("amount") or 0) for payment in payments if payment.get("method") == method)
        sales_count = len([
            sale for sale in valid_sales
            if any(payment.get("method") == method and float(payment.get("amount") or 0) > 0 for payment in sale.get("payments", []))
        ])
        payment_rows.append({
            "method": method,
            "amount": money_round(amount),
            "percent": round((amount / payment_total) * 100) if payment_total else 0,
            "salesCount": sales_count,
        })
    products_by_id = {product.get("id"): product for product in state.get("products", [])}
    brands = {}
    last_sale_by_product = {}
    for sale in valid_sales:
        sale_date = str(sale.get("createdAt", ""))
        for item in sale.get("items", []):
            product = products_by_id.get(item.get("productId"), {})
            brand = item.get("brand") or product.get("brand") or "Sem marca"
            brands[brand] = brands.get(brand, 0) + int(float(item.get("quantity") or 0))
            if not last_sale_by_product.get(item.get("productId")) or sale_date > last_sale_by_product[item.get("productId")]:
                last_sale_by_product[item.get("productId")] = sale_date
    stopped = []
    for product in state.get("products", []):
        base_date = parse_date_input(last_sale_by_product.get(product.get("id")) or product.get("updatedAt"), today)
        stopped_days = (datetime.fromisoformat(today).date() - datetime.fromisoformat(base_date).date()).days
        if stopped_days > 90 and int(float(product.get("stock") or 0)) > 0:
            stopped.append({"name": product.get("name") or "-", "days": stopped_days, "stock": int(float(product.get("stock") or 0))})
    sales_chart = []
    for date_item in date_span(today, days):
        day_sales = [sale for sale in valid_sales if str(sale.get("createdAt", ""))[:10] == date_item]
        sales_chart.append({
            "date": date_item,
            "total": money_round(sum(float(sale.get("total") or 0) for sale in day_sales)),
            "salesCount": len(day_sales),
            "pieces": sum(int(float(item.get("quantity") or 0)) for sale in day_sales for item in sale.get("items", [])),
        })
    return {
        "today": today,
        "range": days,
        "metrics": {
            "todaySales": money_round(sum(float(sale.get("total") or 0) for sale in today_sales)),
            "monthSales": money_round(sum(float(sale.get("total") or 0) for sale in month_sales)),
            "monthProfit": money_round(sum(float(sale.get("total") or 0) - float(sale.get("costTotal") or 0) for sale in month_sales)),
            "stockValue": money_round(stock_value),
            "creditOpen": money_round(sum(receivable_open_amount(item) for item in open_receivables)),
            "cashBalance": money_round(cash_balance),
            "cashInToday": money_round(sum(float(item.get("amount") or 0) for item in today_cash if item.get("direction") == "in")),
            "cashOutToday": money_round(sum(float(item.get("amount") or 0) for item in today_cash if item.get("direction") == "out")),
            "payablesOpen": money_round(sum(payable_open_amount(item) for item in open_payables)),
            "payablesCount": len(open_payables),
            "receivableOpen": money_round(sum(receivable_open_amount(item) for item in open_receivables)),
            "receivableCount": len(open_receivables),
        },
        "salesChart": sales_chart,
        "payments": {"total": money_round(payment_total), "totalSales": len(valid_sales), "rows": payment_rows},
        "topBrands": [{"name": name, "qty": qty} for name, qty in sorted(brands.items(), key=lambda item: item[1], reverse=True)[:5]],
        "stoppedProducts": sorted(stopped, key=lambda item: item["days"], reverse=True)[:6],
    }


def format_brl(value: float) -> str:
    amount = f"{money_round(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {amount}"


def build_reports_summary(state: dict, start: str, end: str, today: str) -> dict:
    if start > end:
        start, end = end, start
    sales = [sale for sale in state.get("sales", []) if start <= str(sale.get("createdAt", ""))[:10] <= end]
    valid_sales = [sale for sale in sales if sale.get("status") != "cancelled"]
    pieces = [item for sale in valid_sales for item in sale.get("items", [])]
    sales_total = sum(float(sale.get("total") or 0) for sale in valid_sales)
    top_customers = []
    for customer in state.get("customers", []):
        total = sum(float(sale.get("total") or 0) for sale in valid_sales if sale.get("customerId") == customer.get("id"))
        if total > 0:
            top_customers.append({"name": customer.get("name") or "-", "total": total})
    top_customers.sort(key=lambda item: item["total"], reverse=True)
    customer_top_line = ", ".join(f"{item['name']} {format_brl(item['total'])}" for item in top_customers[:3]) or "-"
    delinquent_customers = {
        item.get("customerId")
        for item in state.get("receivables", [])
        if item.get("method") == "storeCredit" and str(item.get("dueDate") or "") < today and receivable_open_amount(item) > 0
    }
    open_payables = sum(
        payable_open_amount(item)
        for item in state.get("payables", [])
        if payable_dashboard_status(item, today) != "paid"
    )
    open_store_credit = sum(
        receivable_open_amount(item)
        for item in state.get("receivables", [])
        if item.get("method") == "storeCredit"
    )
    payments = [payment for sale in valid_sales for payment in sale.get("payments", [])]
    payment_methods = [
        ("cash", "Dinheiro"),
        ("pix", "PIX"),
        ("debit", "Débito"),
        ("credit", "Crédito"),
        ("storeCredit", "Crediário"),
    ]
    sold_product_ids = {item.get("productId") for item in pieces}
    stopped = [product.get("name") or "-" for product in state.get("products", []) if product.get("id") not in sold_product_ids]
    reports = [
        {
            "title": "Venda",
            "lines": [
                f"Total: {format_brl(sales_total)}",
                f"Ticket médio: {format_brl(sales_total / len(valid_sales) if valid_sales else 0)}",
                f"Produtos vendidos: {sum(int(float(item.get('quantity') or 0)) for item in pieces)}",
                f"Canceladas: {len([sale for sale in sales if sale.get('status') == 'cancelled'])}",
            ],
        },
        {
            "title": "Clientes",
            "lines": [
                f"Cadastrados: {len(state.get('customers', []))}",
                f"Mais compram: {customer_top_line}",
                f"Inadimplentes: {len(delinquent_customers)}",
            ],
        },
        {"title": "Contas a pagar", "lines": [f"Pendentes: {format_brl(open_payables)}"]},
        {"title": "Contas a receber", "lines": [f"Crediário: {format_brl(open_store_credit)}"]},
        {
            "title": "Recebimentos",
            "lines": [
                f"{label}: {format_brl(sum(float(payment.get('amount') or 0) for payment in payments if payment.get('method') == method))}"
                for method, label in payment_methods
            ],
        },
        {"title": "Produtos parados", "lines": stopped[:8]},
    ]
    return {"start": start, "end": end, "reports": reports}


def sync_payable_to_state(payable: dict | None = None, cash: list[dict] | None = None) -> None:
    state, _ = read_state()
    if payable:
        state["payables"] = [item for item in state.get("payables", []) if item.get("id") != payable["id"]]
        state["payables"].append(payable)
    if cash:
        state["cash"] = [*cash, *state.get("cash", [])]
    write_state(state)


def sync_cash_movements_to_state(movements: list[dict], settle_card_amount: float = 0) -> list[dict]:
    state, _ = read_state()
    state["cash"] = [*movements, *state.get("cash", [])]
    changed_receivables = []
    remaining = money_round(settle_card_amount)
    for receivable in sorted(state.get("receivables", []), key=lambda item: item.get("createdAt", "")):
        if remaining <= 0:
            break
        if receivable.get("status") != "cardPending":
            continue
        open_amount = money_round(float(receivable.get("amount") or 0) - float(receivable.get("received") or 0))
        if open_amount <= 0:
            continue
        paid = min(open_amount, remaining)
        receivable["received"] = money_round(float(receivable.get("received") or 0) + paid)
        receivable["lastPaymentAt"] = movements[0]["createdAt"] if movements else utc_now()
        receivable["updatedAt"] = receivable["lastPaymentAt"]
        receivable["payments"] = [*receivable.get("payments", []), {
            "id": os.urandom(16).hex(),
            "receivableId": receivable.get("id", ""),
            "saleId": receivable.get("saleId", ""),
            "customerId": receivable.get("customerId", ""),
            "method": receivable.get("method", "card"),
            "amount": paid,
            "createdAt": receivable["lastPaymentAt"],
            "note": "Recebimento de cartão",
        }]
        if money_round(float(receivable.get("amount") or 0) - float(receivable.get("received") or 0)) <= 0.01:
            receivable["status"] = "paid"
            receivable["paidAt"] = receivable["lastPaymentAt"]
        changed_receivables.append(receivable)
        remaining = money_round(remaining - paid)
    write_state(state)
    return changed_receivables


def persist_cash_movement(movement: dict, store_id: str = "matriz") -> str:
    updated_at = utc_now()
    with connect_db() as conn:
        conn.execute(
            """
            INSERT INTO cash_movements (
                id, store_id, direction, type, description, method, amount, ref_id, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                movement["id"],
                store_id,
                movement["direction"],
                movement["type"],
                movement["description"],
                movement["method"],
                float(movement["amount"]),
                movement["refId"],
                movement["createdAt"],
            ),
        )

        lock_clause = " FOR UPDATE" if USE_POSTGRES else ""
        row = conn.execute(f"SELECT data FROM app_state WHERE id = 1{lock_clause}").fetchone()
        if row:
            try:
                state = json.loads(row["data"])
            except json.JSONDecodeError:
                state = default_state()
        else:
            state = default_state()
        if not isinstance(state, dict):
            state = default_state()
        current_cash = state.get("cash")
        state["cash"] = [movement, *(current_cash if isinstance(current_cash, list) else [])]
        conn.execute(
            """
            INSERT INTO app_state (id, data, updated_at)
            VALUES (1, ?, ?)
            ON CONFLICT(id) DO UPDATE SET data = excluded.data, updated_at = excluded.updated_at
            """,
            (json.dumps(state, ensure_ascii=False), updated_at),
        )
        record_audit("create", "cash", movement["id"], {"movement": movement}, conn=conn)
    return updated_at


def persist_cash_closing(closing: dict, store_id: str = "matriz") -> str:
    updated_at = utc_now()
    with connect_db() as conn:
        conn.execute(
            """
            INSERT INTO cash_closings (
                id, store_id, date, expected_cash, informed_cash, difference, total_balance,
                cash_in, cash_out, notes, user_id, user_name, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                closing["id"],
                store_id,
                closing["date"],
                float(closing["expectedCash"]),
                float(closing["informedCash"]),
                float(closing["difference"]),
                float(closing["totalBalance"]),
                float(closing["cashIn"]),
                float(closing["cashOut"]),
                closing["notes"],
                closing["userId"],
                closing["userName"],
                closing["createdAt"],
            ),
        )

        lock_clause = " FOR UPDATE" if USE_POSTGRES else ""
        row = conn.execute(f"SELECT data FROM app_state WHERE id = 1{lock_clause}").fetchone()
        if row:
            try:
                state = json.loads(row["data"])
            except json.JSONDecodeError:
                state = default_state()
        else:
            state = default_state()
        if not isinstance(state, dict):
            state = default_state()
        current_closings = state.get("cashClosings")
        state["cashClosings"] = [closing, *(current_closings if isinstance(current_closings, list) else [])]
        conn.execute(
            """
            INSERT INTO app_state (id, data, updated_at)
            VALUES (1, ?, ?)
            ON CONFLICT(id) DO UPDATE SET data = excluded.data, updated_at = excluded.updated_at
            """,
            (json.dumps(state, ensure_ascii=False), updated_at),
        )
        record_audit("create", "cash_closing", closing["id"], {"closing": closing}, conn=conn)
    return updated_at


def cash_closing_metrics(state: dict, date: str) -> dict:
    until_date = str(date or "")[:10]
    movements_until = [item for item in state.get("cash", []) if str(item.get("createdAt", ""))[:10] <= until_date]
    movements_day = [item for item in state.get("cash", []) if str(item.get("createdAt", ""))[:10] == until_date]
    def signed_total(items, method: str | None = None) -> float:
        filtered = [item for item in items if method is None or item.get("method") == method]
        return money_round(sum(
            float(item.get("amount") or 0) if item.get("direction") == "in" else -float(item.get("amount") or 0)
            for item in filtered
        ))
    return {
        "expectedCash": signed_total(movements_until, "cash"),
        "totalBalance": signed_total(movements_until),
        "cashIn": money_round(sum(float(item.get("amount") or 0) for item in movements_day if item.get("direction") == "in" and item.get("method") == "cash")),
        "cashOut": money_round(sum(float(item.get("amount") or 0) for item in movements_day if item.get("direction") == "out" and item.get("method") == "cash")),
    }


def simple_table_config(kind: str) -> tuple[str, str]:
    if kind == "brands":
        return "brands", "brand"
    if kind == "categories":
        return "categories", "category"
    raise ValueError("Cadastro inválido.")


def sync_simple_name_to_state(kind: str, name: str | None = None, previous: str | None = None, deleted_name: str | None = None) -> None:
    state, _ = read_state()
    collection, product_field = simple_table_config(kind)
    if deleted_name:
        state[collection] = [item for item in state.get(collection, []) if item != deleted_name]
    elif name:
        items = [item for item in state.get(collection, []) if item != previous and item != name]
        state[collection] = [*items, name]
        if previous:
            state["products"] = [
                {**product, product_field: name} if product.get(product_field) == previous else product
                for product in state.get("products", [])
            ]
    write_app_state_only(state)


@app.get("/")
def index():
    return send_from_directory(APP_DIR, "index.html")


@app.get("/uploads/products/<path:filename>")
def uploaded_product_image(filename: str):
    return send_from_directory(PRODUCT_UPLOAD_DIR, filename)


@app.get("/api/health")
def health():
    database_name = "PostgreSQL" if USE_POSTGRES else os.path.basename(DB_PATH)
    return jsonify({"ok": True, "message": "Mova Sports ativo.", "database": database_name})


@app.get("/api/backups")
def list_backups_api():
    _, error_response = require_admin()
    if error_response:
        return error_response
    return jsonify({"ok": True, "data": list_database_backups()})


@app.get("/api/database/status")
def database_status_api():
    _, error_response = require_admin()
    if error_response:
        return error_response
    return jsonify({"ok": True, "data": database_status()})


@app.get("/api/export")
def export_data_api():
    _, error_response = require_admin()
    if error_response:
        return error_response
    state, updated_at = read_state()
    safe_state = sanitize_credentials(state)
    exported_at = utc_now()
    payload = {
        "system": "Mova Sports",
        "version": 1,
        "database": "PostgreSQL" if USE_POSTGRES else "SQLite",
        "exportedAt": exported_at,
        "stateUpdatedAt": updated_at,
        "data": safe_state,
    }
    record_audit(
        "export",
        "state",
        "manual-json",
        {
            "exportedAt": exported_at,
            "products": len(safe_state.get("products", [])),
            "customers": len(safe_state.get("customers", [])),
            "sales": len(safe_state.get("sales", [])),
        },
    )
    response = jsonify(payload)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    response.headers["Content-Disposition"] = f'attachment; filename="mova-sports-export-{stamp}.json"'
    return response


def normalize_import_payload(payload: dict) -> tuple[dict | None, str | None]:
    source = payload.get("data") if isinstance(payload.get("data"), dict) else payload
    if not isinstance(source, dict):
        return None, "Arquivo de importacao invalido."
    defaults = default_state()
    imported = {}
    for key, default_value in defaults.items():
        if key == "users":
            continue
        value = source.get(key, default_value)
        if not isinstance(value, list):
            return None, f"O campo {key} deve ser uma lista."
        imported[key] = value
    current_state, _ = read_state()
    imported["users"] = current_state.get("users") or defaults["users"]
    return {**defaults, **imported}, None


@app.post("/api/import")
def import_data_api():
    _, error_response = require_data_import_reset_permission("import")
    if error_response:
        return error_response
    confirmation = ""
    payload = None
    uploaded = request.files.get("file")
    if uploaded:
        confirmation = str(request.form.get("confirmation") or "").strip()
        try:
            payload = json.loads(uploaded.read().decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return jsonify({"ok": False, "error": "Arquivo JSON invalido."}), 400
    else:
        body = request.get_json(silent=True) or {}
        confirmation = str(body.get("confirmation") or "").strip()
        payload = body.get("payload")
    if confirmation != "RESTAURAR":
        return jsonify({"ok": False, "error": "Digite RESTAURAR para confirmar a importacao."}), 400
    state, error = normalize_import_payload(payload if isinstance(payload, dict) else {})
    if error:
        return jsonify({"ok": False, "error": error}), 400
    updated_at = write_state(state)
    summary = {
        "products": len(state.get("products", [])),
        "customers": len(state.get("customers", [])),
        "sales": len(state.get("sales", [])),
        "cash": len(state.get("cash", [])),
        "receivables": len(state.get("receivables", [])),
        "payables": len(state.get("payables", [])),
        "updatedAt": updated_at,
    }
    record_audit("import", "state", "manual-json", summary)
    return jsonify({"ok": True, "data": summary})


@app.post("/api/reset")
def reset_data_api():
    _, error_response = require_data_import_reset_permission("reset")
    if error_response:
        return error_response
    payload = request.get_json(silent=True) or {}
    confirmation = str(payload.get("confirmation") or "").strip()
    if confirmation != "ZERAR":
        return jsonify({"ok": False, "error": "Digite ZERAR para confirmar a limpeza do sistema."}), 400
    updated_at, summary = reset_business_data()
    summary["updatedAt"] = updated_at
    return jsonify({"ok": True, "data": summary})


@app.post("/api/backups")
def create_backup_api():
    _, error_response = require_admin()
    if error_response:
        return error_response
    payload = request.get_json(silent=True) or {}
    try:
        backup = create_database_backup(str(payload.get("reason") or "manual"))
    except RuntimeError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    prune_database_backups()
    record_audit("create", "backup", backup["filename"], {"reason": backup["reason"], "size": backup["size"]})
    return jsonify({"ok": True, "data": backup}), 201


@app.post("/api/uploads/product-photo")
def upload_product_photo_api():
    file_storage = request.files.get("photo")
    try:
        saved = save_product_image(file_storage)
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    record_audit(
        "upload",
        "product_photo",
        saved["filename"],
        {"filename": saved["filename"], "size": saved["size"], "url": saved["url"]},
    )
    return jsonify({"ok": True, "data": saved}), 201


@app.get("/api/audit-logs")
def list_audit_logs_api():
    _, error_response = require_admin()
    if error_response:
        return error_response
    try:
        limit = max(1, min(500, int(float(request.args.get("limit", 100)))))
    except ValueError:
        limit = 100
    module = str(request.args.get("module", "") or "").strip()
    action = str(request.args.get("action", "") or "").strip()
    filters = ["store_id = ?"]
    params: list = ["matriz"]
    if module:
        filters.append("module = ?")
        params.append(module)
    if action:
        filters.append("action = ?")
        params.append(action)
    params.append(limit)
    init_db()
    with connect_db() as conn:
        rows = conn.execute(
            f"""
            SELECT id, user_id AS userId, user_name AS userName, user_role AS userRole,
                   action, module, ref_id AS refId, details, created_at AS createdAt
            FROM audit_logs
            WHERE {' AND '.join(filters)}
            ORDER BY created_at DESC
            LIMIT ?
            """,
            tuple(params),
        ).fetchall()
    data = []
    for row in rows:
        item = dict(row)
        try:
            item["details"] = json.loads(item.get("details") or "{}")
        except json.JSONDecodeError:
            item["details"] = {}
        data.append(item)
    return jsonify({"ok": True, "data": data})


@app.get("/api/dashboard")
def dashboard_api():
    try:
        days = max(1, min(365, int(float(request.args.get("range", 30)))))
    except ValueError:
        days = 30
    today = parse_date_input(request.args.get("date", ""))
    state, _ = read_state()
    return jsonify({"ok": True, "data": build_dashboard_summary(state, days, today)})


@app.get("/api/reports")
def reports_api():
    today = parse_date_input(request.args.get("today", ""))
    start = parse_date_input(request.args.get("start", ""), today)
    end = parse_date_input(request.args.get("end", ""), start)
    state, _ = read_state()
    return jsonify({"ok": True, "data": build_reports_summary(state, start, end, today)})


@app.post("/api/login")
def api_login():
    payload = request.get_json(silent=True) or {}
    login = str(payload.get("login", "")).strip()
    password = str(payload.get("password", ""))
    if not login or not password:
        return jsonify({"ok": False, "error": "Informe usuário e senha."}), 400
    if login_blocked(login):
        return jsonify({"ok": False, "error": "Muitas tentativas de login. Aguarde alguns minutos e tente novamente."}), 429
    init_db()
    with connect_db() as conn:
        row = conn.execute(
            """
            SELECT id, name, login, password_hash, role, active
            FROM users
            WHERE store_id = ? AND login = ?
            """,
            ("matriz", login),
        ).fetchone()
    if not row or not row["active"] or not password_matches(row["password_hash"], password):
        register_login_failure(login)
        return jsonify({"ok": False, "error": "Usuário ou senha inválidos."}), 401
    clear_login_failures(login)
    user = public_user(row)
    session.clear()
    session.permanent = True
    session["user"] = user
    record_audit("login", "auth", user["id"], {"login": user["login"]})
    return jsonify({"ok": True, "user": user, "capabilities": data_import_reset_capabilities(user)})


@app.post("/api/logout")
def api_logout():
    user = session.get("user")
    if user:
        record_audit("logout", "auth", user.get("id", ""), {"login": user.get("login", "")})
    session.pop("user", None)
    return jsonify({"ok": True, "capabilities": data_import_reset_capabilities(None)})


@app.get("/api/session")
def api_session():
    user = refresh_session_user() if session.get("user") else None
    if session.get("user") and not user:
        session.clear()
    return jsonify({"ok": True, "user": user, "capabilities": data_import_reset_capabilities(user)})


@app.post("/api/me/password")
def change_own_password_api():
    current_user = session.get("user")
    if not current_user:
        return jsonify({"ok": False, "error": "Login obrigatorio."}), 401
    payload = request.get_json(silent=True) or {}
    current_password = str(payload.get("currentPassword") or "")
    new_password = str(payload.get("newPassword") or "")
    confirm_password = str(payload.get("confirmPassword") or "")
    if not current_password or not new_password:
        return jsonify({"ok": False, "error": "Informe a senha atual e a nova senha."}), 400
    if new_password != confirm_password:
        return jsonify({"ok": False, "error": "A confirmacao da senha nao confere."}), 400
    password_error = validate_password_strength(new_password)
    if password_error:
        return jsonify({"ok": False, "error": password_error}), 400
    init_db()
    with connect_db() as conn:
        row = conn.execute(
            """
            SELECT id, name, login, password_hash, role, active
            FROM users
            WHERE store_id = ? AND id = ?
            """,
            ("matriz", current_user.get("id")),
        ).fetchone()
        if not row or not row["active"]:
            return jsonify({"ok": False, "error": "Usuario nao encontrado ou inativo."}), 404
        if not password_matches(row["password_hash"], current_password):
            return jsonify({"ok": False, "error": "Senha atual incorreta."}), 401
        now = utc_now()
        conn.execute(
            "UPDATE users SET password_hash = ?, updated_at = ? WHERE store_id = ? AND id = ?",
            (generate_password_hash(new_password), now, "matriz", row["id"]),
        )
        record_audit("update", "auth", row["id"], {"changedPassword": True}, conn)
    sync_user_to_state({
        "id": row["id"],
        "name": row["name"],
        "login": row["login"],
        "role": row["role"],
        "active": bool(row["active"]),
    })
    return jsonify({"ok": True})


@app.get("/api/users")
def list_users():
    init_db()
    with connect_db() as conn:
        rows = conn.execute(
            """
            SELECT id, name, login, role, active
            FROM users
            WHERE store_id = ?
            ORDER BY name COLLATE NOCASE
            """,
            ("matriz",),
        ).fetchall()
    return jsonify({"ok": True, "data": [public_user(row) for row in rows]})


@app.post("/api/users")
def create_user():
    _, error_response = require_admin()
    if error_response:
        return error_response
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"ok": False, "error": "Envie um JSON válido."}), 400
    user = normalize_user_payload(payload)
    error = validate_user_payload(user, creating=True)
    if error:
        return jsonify({"ok": False, "error": error}), 400
    init_db()
    with connect_db() as conn:
        duplicate = conn.execute(
            """
            SELECT id FROM users
            WHERE store_id = ? AND login = ? AND id <> ?
            """,
            ("matriz", user["login"], user["id"]),
        ).fetchone()
        if duplicate:
            return jsonify({"ok": False, "error": "Usuário já cadastrado."}), 409
        conn.execute(
            """
            INSERT INTO users (id, store_id, name, login, password_hash, role, active, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user["id"],
                "matriz",
                user["name"],
                user["login"],
                generate_password_hash(user["password"]),
                user["role"],
                1 if user["active"] else 0,
                user["updatedAt"],
            ),
        )
        public = public_user(user)
        record_audit("create", "user", user["id"], {"user": public}, conn)
    sync_user_to_state(public)
    return jsonify({"ok": True, "data": public}), 201


@app.put("/api/users/<user_id>")
def update_user(user_id: str):
    current_user, error_response = require_admin()
    if error_response:
        return error_response
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"ok": False, "error": "Envie um JSON válido."}), 400
    init_db()
    with connect_db() as conn:
        row = conn.execute(
            """
            SELECT id, name, login, role, active, password_hash
            FROM users
            WHERE store_id = ? AND id = ?
            """,
            ("matriz", user_id),
        ).fetchone()
        if not row:
            return jsonify({"ok": False, "error": "Usuário não encontrado."}), 404
        user = normalize_user_payload(payload, dict(row))
        user["id"] = user_id
        error = validate_user_payload(user)
        if error:
            return jsonify({"ok": False, "error": error}), 400
        duplicate = conn.execute(
            """
            SELECT id FROM users
            WHERE store_id = ? AND login = ? AND id <> ?
            """,
            ("matriz", user["login"], user_id),
        ).fetchone()
        if duplicate:
            return jsonify({"ok": False, "error": "Usuário já cadastrado."}), 409
        password_hash = generate_password_hash(user["password"]) if user["password"] else row["password_hash"]
        conn.execute(
            """
            UPDATE users
            SET name = ?, login = ?, password_hash = ?, role = ?, active = ?, updated_at = ?
            WHERE store_id = ? AND id = ?
            """,
            (
                user["name"],
                user["login"],
                password_hash,
                user["role"],
                1 if user["active"] else 0,
                user["updatedAt"],
                "matriz",
                user_id,
            ),
        )
        updated = conn.execute(
            """
            SELECT id, name, login, role, active
            FROM users
            WHERE store_id = ? AND id = ?
            """,
            ("matriz", user_id),
        ).fetchone()
        record_audit("update", "user", user_id, {"user": public_user(user)}, conn)
    sync_user_to_state(public_user(user))
    public = public_user(updated)
    if current_user and current_user.get("id") == user_id:
        session["user"] = public
    return jsonify({"ok": True, "data": public})


@app.delete("/api/users/<user_id>")
def delete_user_api(user_id: str):
    current_user, error_response = require_admin()
    if error_response:
        return error_response
    if current_user and current_user.get("id") == user_id:
        return jsonify({"ok": False, "error": "Não é possível excluir o usuário logado."}), 409
    init_db()
    with connect_db() as conn:
        row = conn.execute(
            "SELECT id, role FROM users WHERE store_id = ? AND id = ?",
            ("matriz", user_id),
        ).fetchone()
        if not row:
            return jsonify({"ok": False, "error": "Usuário não encontrado."}), 404
        if row["role"] == "admin":
            admin_count = conn.execute(
                "SELECT COUNT(*) AS total FROM users WHERE store_id = ? AND role = 'admin' AND active = 1",
                ("matriz",),
            ).fetchone()["total"]
            if admin_count <= 1:
                return jsonify({"ok": False, "error": "Não é possível excluir o último administrador."}), 409
        conn.execute("DELETE FROM users WHERE store_id = ? AND id = ?", ("matriz", user_id))
        record_audit("delete", "user", user_id, {"role": row["role"]}, conn)
    sync_user_to_state(deleted_id=user_id)
    return jsonify({"ok": True})


@app.get("/api/state")
def get_state():
    state, updated_at = read_state()
    return jsonify({"ok": True, "data": sanitize_credentials(state), "updatedAt": updated_at})


@app.get("/api/products")
def list_products():
    init_db()
    with connect_db() as conn:
        rows = conn.execute(
            """
            SELECT id, barcode, name, size, color, gender, category_name AS category,
                   brand_name AS brand, stock, min_stock AS minStock, description,
                   active, cost, price, photo, updated_at AS updatedAt
            FROM products
            WHERE store_id = ?
            ORDER BY name COLLATE NOCASE
            """,
            ("matriz",),
        ).fetchall()
    products = [product_from_row(row) for row in rows]
    return jsonify({"ok": True, "data": products})


@app.post("/api/products")
def create_product():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"ok": False, "error": "Envie um JSON válido."}), 400
    product = normalize_product_payload(payload)
    error = validate_product(product)
    if error:
        return jsonify({"ok": False, "error": error}), 400
    init_db()
    with connect_db() as conn:
        duplicate = conn.execute(
            """
            SELECT id FROM products
            WHERE store_id = ? AND barcode = ? AND id <> ?
            """,
            ("matriz", product["barcode"], product["id"]),
        ).fetchone()
        if duplicate:
            return jsonify({"ok": False, "error": "Código de barras já cadastrado."}), 409
        upsert_product(conn, product)
        record_audit("create", "product", product["id"], {"product": product}, conn)
    sync_product_to_state(product=product)
    return jsonify({"ok": True, "data": product}), 201


@app.put("/api/products/<product_id>")
def update_product(product_id: str):
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"ok": False, "error": "Envie um JSON válido."}), 400
    init_db()
    with connect_db() as conn:
        row = conn.execute(
            """
            SELECT id, barcode, name, size, color, gender, category_name AS category,
                   brand_name AS brand, stock, min_stock AS minStock, description,
                   active, cost, price, photo, updated_at AS updatedAt
            FROM products
            WHERE store_id = ? AND id = ?
            """,
            ("matriz", product_id),
        ).fetchone()
        if not row:
            return jsonify({"ok": False, "error": "Produto não encontrado."}), 404
        product = normalize_product_payload(payload, product_from_row(row))
        product["id"] = product_id
        error = validate_product(product)
        if error:
            return jsonify({"ok": False, "error": error}), 400
        duplicate = conn.execute(
            """
            SELECT id FROM products
            WHERE store_id = ? AND barcode = ? AND id <> ?
            """,
            ("matriz", product["barcode"], product_id),
        ).fetchone()
        if duplicate:
            return jsonify({"ok": False, "error": "Código de barras já cadastrado."}), 409
        upsert_product(conn, product)
        record_audit("update", "product", product["id"], {"product": product}, conn)
    sync_product_to_state(product=product)
    return jsonify({"ok": True, "data": product})


@app.delete("/api/products/<product_id>")
def delete_product_api(product_id: str):
    init_db()
    with connect_db() as conn:
        row = conn.execute(
            "SELECT id FROM products WHERE store_id = ? AND id = ?",
            ("matriz", product_id),
        ).fetchone()
        if not row:
            return jsonify({"ok": False, "error": "Produto não encontrado."}), 404
        linked_sale = conn.execute(
            "SELECT id FROM sale_items WHERE product_id = ? LIMIT 1",
            (product_id,),
        ).fetchone()
        linked_return = conn.execute(
            "SELECT id FROM sale_return_items WHERE product_id = ? LIMIT 1",
            (product_id,),
        ).fetchone()
        if linked_sale or linked_return:
            return jsonify({"ok": False, "error": "Produto possui historico de venda, troca ou devolucao e nao pode ser excluido."}), 409
        conn.execute("DELETE FROM products WHERE store_id = ? AND id = ?", ("matriz", product_id))
        record_audit("delete", "product", product_id, {}, conn)
    sync_product_to_state(deleted_id=product_id)
    return jsonify({"ok": True})


@app.get("/api/brands")
def list_brands():
    init_db()
    with connect_db() as conn:
        rows = conn.execute(
            "SELECT name FROM brands WHERE store_id = ? ORDER BY name COLLATE NOCASE",
            ("matriz",),
        ).fetchall()
    return jsonify({"ok": True, "data": [row["name"] for row in rows]})


@app.post("/api/brands")
def create_brand():
    return upsert_simple_name_api("brands")


@app.put("/api/brands/<path:previous_name>")
def update_brand(previous_name: str):
    return upsert_simple_name_api("brands", previous_name)


@app.delete("/api/brands/<path:name>")
def delete_brand(name: str):
    return delete_simple_name_api("brands", name)


@app.get("/api/categories")
def list_categories():
    init_db()
    with connect_db() as conn:
        rows = conn.execute(
            "SELECT name FROM categories WHERE store_id = ? ORDER BY name COLLATE NOCASE",
            ("matriz",),
        ).fetchall()
    return jsonify({"ok": True, "data": [row["name"] for row in rows]})


@app.post("/api/categories")
def create_category():
    return upsert_simple_name_api("categories")


@app.put("/api/categories/<path:previous_name>")
def update_category(previous_name: str):
    return upsert_simple_name_api("categories", previous_name)


@app.delete("/api/categories/<path:name>")
def delete_category(name: str):
    return delete_simple_name_api("categories", name)


def upsert_simple_name_api(kind: str, previous_name: str | None = None):
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"ok": False, "error": "Envie um JSON válido."}), 400
    name = str(payload.get("name", "")).strip()
    if not name:
        return jsonify({"ok": False, "error": "Nome é obrigatório."}), 400
    table, product_field = simple_table_config(kind)
    now = utc_now()
    item_id = f"matriz:{product_field}:{name.casefold()}"
    previous_id = f"matriz:{product_field}:{previous_name.casefold()}" if previous_name else item_id
    init_db()
    with connect_db() as conn:
        duplicate = conn.execute(
            f"SELECT id FROM {table} WHERE store_id = ? AND name = ? AND id <> ?",
            ("matriz", name, previous_id),
        ).fetchone()
        if duplicate:
            return jsonify({"ok": False, "error": "Nome já cadastrado."}), 409
        if previous_name:
            row = conn.execute(
                f"SELECT id FROM {table} WHERE store_id = ? AND name = ?",
                ("matriz", previous_name),
            ).fetchone()
            if not row:
                return jsonify({"ok": False, "error": "Cadastro não encontrado."}), 404
            conn.execute(f"DELETE FROM {table} WHERE store_id = ? AND name = ?", ("matriz", previous_name))
            column = "brand_name" if kind == "brands" else "category_name"
            conn.execute(f"UPDATE products SET {column} = ?, updated_at = ? WHERE store_id = ? AND {column} = ?", (name, now, "matriz", previous_name))
        conn.execute(
            f"""
            INSERT INTO {table} (id, store_id, name, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET name = excluded.name, updated_at = excluded.updated_at
            """,
            (item_id, "matriz", name, now),
        )
        record_audit("update" if previous_name else "create", kind, name, {"name": name, "previous": previous_name}, conn)
    sync_simple_name_to_state(kind, name=name, previous=previous_name)
    return jsonify({"ok": True, "data": name}), 201 if not previous_name else 200


def delete_simple_name_api(kind: str, name: str):
    table, product_field = simple_table_config(kind)
    column = "brand_name" if kind == "brands" else "category_name"
    init_db()
    with connect_db() as conn:
        linked = conn.execute(
            f"SELECT id FROM products WHERE store_id = ? AND {column} = ? LIMIT 1",
            ("matriz", name),
        ).fetchone()
        if linked:
            return jsonify({"ok": False, "error": "Cadastro em uso por produto e não pode ser excluído."}), 409
        row = conn.execute(
            f"SELECT id FROM {table} WHERE store_id = ? AND name = ?",
            ("matriz", name),
        ).fetchone()
        if not row:
            return jsonify({"ok": False, "error": "Cadastro não encontrado."}), 404
        conn.execute(f"DELETE FROM {table} WHERE store_id = ? AND name = ?", ("matriz", name))
        record_audit("delete", kind, name, {"name": name}, conn)
    sync_simple_name_to_state(kind, deleted_name=name)
    return jsonify({"ok": True})


@app.get("/api/suppliers")
def list_suppliers():
    init_db()
    with connect_db() as conn:
        rows = conn.execute(
            """
            SELECT id, name, cnpj, phone, email, address, updated_at AS updatedAt
            FROM suppliers
            WHERE store_id = ?
            ORDER BY name COLLATE NOCASE
            """,
            ("matriz",),
        ).fetchall()
    return jsonify({"ok": True, "data": [dict(row) for row in rows]})


@app.post("/api/suppliers")
def create_supplier():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"ok": False, "error": "Envie um JSON válido."}), 400
    supplier = normalize_supplier_payload(payload)
    error = validate_supplier(supplier)
    if error:
        return jsonify({"ok": False, "error": error}), 400
    init_db()
    with connect_db() as conn:
        upsert_supplier(conn, supplier)
        record_audit("create", "supplier", supplier["id"], {"supplier": supplier}, conn)
    sync_supplier_to_state(supplier=supplier)
    return jsonify({"ok": True, "data": supplier}), 201


@app.put("/api/suppliers/<supplier_id>")
def update_supplier(supplier_id: str):
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"ok": False, "error": "Envie um JSON válido."}), 400
    init_db()
    with connect_db() as conn:
        row = conn.execute(
            """
            SELECT id, name, cnpj, phone, email, address, updated_at AS updatedAt
            FROM suppliers
            WHERE store_id = ? AND id = ?
            """,
            ("matriz", supplier_id),
        ).fetchone()
        if not row:
            return jsonify({"ok": False, "error": "Fornecedor não encontrado."}), 404
        supplier = normalize_supplier_payload(payload, supplier_from_row(row))
        supplier["id"] = supplier_id
        error = validate_supplier(supplier)
        if error:
            return jsonify({"ok": False, "error": error}), 400
        upsert_supplier(conn, supplier)
        record_audit("update", "supplier", supplier["id"], {"supplier": supplier}, conn)
    sync_supplier_to_state(supplier=supplier)
    return jsonify({"ok": True, "data": supplier})


@app.delete("/api/suppliers/<supplier_id>")
def delete_supplier_api(supplier_id: str):
    init_db()
    with connect_db() as conn:
        row = conn.execute(
            "SELECT id, name FROM suppliers WHERE store_id = ? AND id = ?",
            ("matriz", supplier_id),
        ).fetchone()
        if not row:
            return jsonify({"ok": False, "error": "Fornecedor não encontrado."}), 404
        linked_payable = conn.execute(
            "SELECT id FROM payables WHERE store_id = ? AND supplier = ? LIMIT 1",
            ("matriz", row["name"]),
        ).fetchone()
        if linked_payable:
            return jsonify({"ok": False, "error": "Fornecedor possui conta a pagar vinculada e nao pode ser excluido."}), 409
        conn.execute("DELETE FROM suppliers WHERE store_id = ? AND id = ?", ("matriz", supplier_id))
        record_audit("delete", "supplier", supplier_id, {}, conn)
    sync_supplier_to_state(deleted_id=supplier_id)
    return jsonify({"ok": True})


@app.get("/api/customers")
def list_customers():
    init_db()
    with connect_db() as conn:
        rows = conn.execute(
            """
            SELECT id, code, name, cpf, rg, birth, whatsapp, email, address,
                   city, district, zip, credit_limit AS "limit", status, updated_at AS updatedAt
            FROM customers
            WHERE store_id = ?
            ORDER BY name COLLATE NOCASE
            """,
            ("matriz",),
        ).fetchall()
    return jsonify({"ok": True, "data": [dict(row) for row in rows]})


@app.post("/api/customers")
def create_customer():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"ok": False, "error": "Envie um JSON válido."}), 400
    customer = normalize_customer_payload(payload)
    error = validate_customer(customer)
    if error:
        return jsonify({"ok": False, "error": error}), 400
    init_db()
    with connect_db() as conn:
        duplicate = conn.execute(
            """
            SELECT id FROM customers
            WHERE store_id = ? AND cpf = ? AND cpf <> '' AND id <> ?
            """,
            ("matriz", customer["cpf"], customer["id"]),
        ).fetchone()
        if duplicate:
            return jsonify({"ok": False, "error": "CPF já cadastrado."}), 409
        upsert_customer(conn, customer)
        record_audit("create", "customer", customer["id"], {"customer": customer}, conn)
    sync_customer_to_state(customer=customer)
    return jsonify({"ok": True, "data": customer}), 201


@app.put("/api/customers/<customer_id>")
def update_customer(customer_id: str):
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"ok": False, "error": "Envie um JSON válido."}), 400
    init_db()
    with connect_db() as conn:
        row = conn.execute(
            """
            SELECT id, code, name, cpf, rg, birth, whatsapp, email, address,
                   city, district, zip, credit_limit AS "limit", status, updated_at AS updatedAt
            FROM customers
            WHERE store_id = ? AND id = ?
            """,
            ("matriz", customer_id),
        ).fetchone()
        if not row:
            return jsonify({"ok": False, "error": "Cliente não encontrado."}), 404
        customer = normalize_customer_payload(payload, customer_from_row(row))
        customer["id"] = customer_id
        error = validate_customer(customer)
        if error:
            return jsonify({"ok": False, "error": error}), 400
        duplicate = conn.execute(
            """
            SELECT id FROM customers
            WHERE store_id = ? AND cpf = ? AND cpf <> '' AND id <> ?
            """,
            ("matriz", customer["cpf"], customer_id),
        ).fetchone()
        if duplicate:
            return jsonify({"ok": False, "error": "CPF já cadastrado."}), 409
        upsert_customer(conn, customer)
        record_audit("update", "customer", customer["id"], {"customer": customer}, conn)
    sync_customer_to_state(customer=customer)
    return jsonify({"ok": True, "data": customer})


@app.delete("/api/customers/<customer_id>")
def delete_customer_api(customer_id: str):
    init_db()
    with connect_db() as conn:
        row = conn.execute(
            "SELECT id FROM customers WHERE store_id = ? AND id = ?",
            ("matriz", customer_id),
        ).fetchone()
        if not row:
            return jsonify({"ok": False, "error": "Cliente não encontrado."}), 404
        linked_sale = conn.execute(
            "SELECT id FROM sales WHERE store_id = ? AND customer_id = ? LIMIT 1",
            ("matriz", customer_id),
        ).fetchone()
        linked_receivable = conn.execute(
            "SELECT id FROM receivables WHERE store_id = ? AND customer_id = ? LIMIT 1",
            ("matriz", customer_id),
        ).fetchone()
        linked_payment = conn.execute(
            "SELECT id FROM receivable_payments WHERE store_id = ? AND customer_id = ? LIMIT 1",
            ("matriz", customer_id),
        ).fetchone()
        if linked_sale or linked_receivable or linked_payment:
            return jsonify({"ok": False, "error": "Cliente possui histórico financeiro e não pode ser excluído."}), 409
        conn.execute("DELETE FROM customers WHERE store_id = ? AND id = ?", ("matriz", customer_id))
        record_audit("delete", "customer", customer_id, {}, conn)
    sync_customer_to_state(deleted_id=customer_id)
    return jsonify({"ok": True})


@app.get("/api/sales")
def list_sales():
    init_db()
    with connect_db() as conn:
        sales = conn.execute(
            """
            SELECT id, customer_id AS customerId, customer_name AS customerName,
                   subtotal, discount, total, cost_total AS costTotal,
                   status, created_at AS createdAt, updated_at AS updatedAt
            FROM sales
            WHERE store_id = ?
            ORDER BY created_at DESC
            """,
            ("matriz",),
        ).fetchall()
        items = conn.execute(
            """
            SELECT sale_id AS saleId, product_id AS productId, barcode, name, brand,
                   quantity, unit_cost AS unitCost, unit_price AS unitPrice, total
            FROM sale_items
            WHERE sale_id IN (SELECT id FROM sales WHERE store_id = ?)
            ORDER BY id
            """,
            ("matriz",),
        ).fetchall()
        payments = conn.execute(
            """
            SELECT sale_id AS saleId, method, amount, installments, status, created_at AS createdAt
            FROM sale_payments
            WHERE sale_id IN (SELECT id FROM sales WHERE store_id = ?)
            ORDER BY id
            """,
            ("matriz",),
        ).fetchall()

    items_by_sale: dict[str, list[dict]] = {}
    for item in items:
        row = dict(item)
        items_by_sale.setdefault(row.pop("saleId"), []).append(row)

    payments_by_sale: dict[str, list[dict]] = {}
    for payment in payments:
        row = dict(payment)
        payments_by_sale.setdefault(row.pop("saleId"), []).append(row)

    data = []
    for sale in sales:
        row = dict(sale)
        row["items"] = items_by_sale.get(row["id"], [])
        row["payments"] = payments_by_sale.get(row["id"], [])
        data.append(row)
    return jsonify({"ok": True, "data": data})


@app.post("/api/sales")
def create_sale():
    if not session.get("user"):
        return jsonify({"ok": False, "error": "Login obrigatório."}), 401
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"ok": False, "error": "Envie um JSON válido."}), 400
    init_db()
    product_ids = [str(item.get("productId", "")).strip() for item in (payload.get("items") or []) if item.get("productId")]
    if not product_ids:
        return jsonify({"ok": False, "error": "Adicione produtos."}), 400
    placeholders = ",".join("?" for _ in product_ids)
    with connect_db() as conn:
        product_rows = conn.execute(
            f"""
            SELECT id, barcode, name, size, color, gender, category_name AS category,
                   brand_name AS brand, stock, min_stock AS minStock, description,
                   active, cost, price, photo, updated_at AS updatedAt
            FROM products
            WHERE store_id = ? AND id IN ({placeholders})
            """,
            ("matriz", *product_ids),
        ).fetchall()
        products_by_id = {row["id"]: row for row in product_rows}
        sale_id = str(payload.get("id") or "").strip() or next_sale_code_db(conn)
        existing = conn.execute("SELECT id FROM sales WHERE store_id = ? AND id = ?", ("matriz", sale_id)).fetchone()
        if existing:
            sale_id = next_sale_code_db(conn)
        state, _ = read_state()
        reserved_by_product = conditional_reserved_quantities(state)
        sale, error = build_sale_from_payload(payload, products_by_id, sale_id, reserved_by_product)
        if error:
            return jsonify({"ok": False, "error": error}), 400

        store_credit = money_round(sum(payment["amount"] for payment in sale["payments"] if payment["method"] == "storeCredit"))
        customer_row = None
        if store_credit > 0:
            if not sale["customerId"]:
                return jsonify({"ok": False, "error": "Crediário exige cliente cadastrado."}), 400
            customer_row = conn.execute(
                """
                SELECT id, name, credit_limit AS "limit", status
                FROM customers
                WHERE store_id = ? AND id = ?
                """,
                ("matriz", sale["customerId"]),
            ).fetchone()
            if not customer_row:
                return jsonify({"ok": False, "error": "Cliente não encontrado."}), 400
            if customer_row["status"] == "blocked":
                return jsonify({"ok": False, "error": "Cliente bloqueado para crediário."}), 409
            open_debt = conn.execute(
                """
                SELECT COALESCE(SUM(amount - received), 0) AS total
                FROM receivables
                WHERE store_id = ? AND customer_id = ? AND method = 'storeCredit' AND status <> 'cancelled'
                """,
                ("matriz", sale["customerId"]),
            ).fetchone()["total"]
            if float(open_debt or 0) + store_credit > float(customer_row["limit"] or 0) and session.get("user", {}).get("role") != "admin":
                return jsonify({"ok": False, "error": "Limite de crédito ultrapassado."}), 409
            sale["customerName"] = customer_row["name"]

        installments = max(1, int(float(payload.get("storeCreditInstallments", 1) or 1)))
        cash, receivables = build_financial_from_sale(sale, installments)
        updated_products = []
        for item in sale["items"]:
            row = products_by_id[item["productId"]]
            product = product_from_row(row)
            product["stock"] = int(product["stock"] or 0) - int(item["quantity"] or 0)
            product["updatedAt"] = utc_now()
            updated_products.append(product)

    sync_sale_to_state(sale, updated_products, cash, receivables)
    record_audit("create", "sale", sale["id"], {"total": sale["total"], "items": sale["items"], "payments": sale["payments"]})
    return jsonify({"ok": True, "data": {"sale": sale, "products": updated_products, "cash": cash, "receivables": receivables}}), 201


@app.post("/api/sales/<sale_id>/cancel")
def cancel_sale_api(sale_id: str):
    if not session.get("user"):
        return jsonify({"ok": False, "error": "Login obrigatório."}), 401
    init_db()
    with connect_db() as conn:
        sale_row = conn.execute(
            """
            SELECT id, customer_id AS customerId, customer_name AS customerName,
                   subtotal, discount, total, cost_total AS costTotal,
                   status, created_at AS createdAt, updated_at AS updatedAt
            FROM sales
            WHERE store_id = ? AND id = ?
            """,
            ("matriz", sale_id),
        ).fetchone()
        if not sale_row:
            return jsonify({"ok": False, "error": "Venda não encontrada."}), 404
        if sale_row["status"] == "cancelled":
            return jsonify({"ok": False, "error": "Venda já cancelada."}), 409
        items = conn.execute(
            """
            SELECT product_id AS productId, barcode, name, brand, quantity,
                   unit_cost AS unitCost, unit_price AS unitPrice, total
            FROM sale_items
            WHERE sale_id = ?
            ORDER BY id
            """,
            (sale_id,),
        ).fetchall()
        payments = conn.execute(
            """
            SELECT method, amount, installments, status, created_at AS createdAt
            FROM sale_payments
            WHERE sale_id = ?
            ORDER BY id
            """,
            (sale_id,),
        ).fetchall()
        product_ids = [item["productId"] for item in items if item["productId"]]
        updated_products = []
        if product_ids:
            placeholders = ",".join("?" for _ in product_ids)
            product_rows = conn.execute(
                f"""
                SELECT id, barcode, name, size, color, gender, category_name AS category,
                       brand_name AS brand, stock, min_stock AS minStock, description,
                       active, cost, price, photo, updated_at AS updatedAt
                FROM products
                WHERE store_id = ? AND id IN ({placeholders})
                """,
                ("matriz", *product_ids),
            ).fetchall()
            products_by_id = {row["id"]: row for row in product_rows}
            for item in items:
                row = products_by_id.get(item["productId"])
                if not row:
                    continue
                product = product_from_row(row)
                product["stock"] = int(product["stock"] or 0) + int(item["quantity"] or 0)
                product["updatedAt"] = utc_now()
                updated_products.append(product)

    cash_refund = money_round(sum(float(payment["amount"] or 0) for payment in payments if payment["method"] == "cash"))
    cash = []
    if cash_refund > 0:
        cash.append({
            "id": os.urandom(16).hex(),
            "direction": "out",
            "type": "cancelamento",
            "description": f"Cancelamento venda {sale_id}",
            "method": "cash",
            "amount": cash_refund,
            "refId": sale_id,
            "createdAt": utc_now(),
        })
    sale, receivables = sync_cancel_sale_to_state(sale_id, updated_products, cash)
    if not sale:
        sale = dict(sale_row)
        sale["status"] = "cancelled"
        sale["items"] = [dict(item) for item in items]
        sale["payments"] = [dict(payment) for payment in payments]
    record_audit("cancel", "sale", sale_id, {"cashRefund": cash_refund, "items": sale.get("items", [])})
    return jsonify({"ok": True, "data": {"sale": sale, "products": updated_products, "cash": cash, "receivables": receivables}})


@app.get("/api/returns")
def list_returns():
    init_db()
    with connect_db() as conn:
        returns = conn.execute(
            """
            SELECT id, sale_id AS saleId, customer_name AS customerName,
                   total, reason, notes, created_at AS createdAt
            FROM sale_returns
            WHERE store_id = ?
            ORDER BY created_at DESC
            """,
            ("matriz",),
        ).fetchall()
        items = conn.execute(
            """
            SELECT return_id AS returnId, product_id AS productId, product_name AS productName,
                   action, quantity, unit_price AS unitPrice, total
            FROM sale_return_items
            WHERE return_id IN (SELECT id FROM sale_returns WHERE store_id = ?)
            ORDER BY id
            """,
            ("matriz",),
        ).fetchall()
    items_by_return: dict[str, list[dict]] = {}
    for item in items:
        row = dict(item)
        items_by_return.setdefault(row.pop("returnId"), []).append(row)
    data = []
    for return_row in returns:
        row = dict(return_row)
        row["items"] = items_by_return.get(row["id"], [])
        data.append(row)
    return jsonify({"ok": True, "data": data})


@app.get("/api/conditionals")
def list_conditionals():
    state, _ = read_state()
    data = sorted(state.get("conditionals", []) or [], key=lambda item: item.get("createdAt", ""), reverse=True)
    return jsonify({"ok": True, "data": data})


@app.post("/api/conditionals")
def create_conditional_api():
    if not session.get("user"):
        return jsonify({"ok": False, "error": "Login obrigatório."}), 401
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"ok": False, "error": "Envie um JSON válido."}), 400
    state, _ = read_state()
    conditional_id = str(payload.get("id") or "").strip() or next_conditional_code(state)
    if any(str(item.get("id", "")) == conditional_id for item in state.get("conditionals", []) or []):
        conditional_id = next_conditional_code(state)
    conditional, error = build_conditional_from_payload(payload, state, conditional_id)
    if error:
        return jsonify({"ok": False, "error": error}), 400
    state["conditionals"] = [conditional, *[item for item in state.get("conditionals", []) if item.get("id") != conditional["id"]]]
    write_app_state_only(state)
    record_audit("create", "conditional", conditional["id"], {"conditional": conditional})
    return jsonify({"ok": True, "data": conditional}), 201


@app.put("/api/conditionals/<conditional_id>")
def update_conditional_api(conditional_id: str):
    if not session.get("user"):
        return jsonify({"ok": False, "error": "Login obrigatório."}), 401
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"ok": False, "error": "Envie um JSON válido."}), 400
    state, _ = read_state()
    conditionals = state.get("conditionals", []) or []
    conditional = next((item for item in conditionals if str(item.get("id", "")) == conditional_id), None)
    if not conditional:
        return jsonify({"ok": False, "error": "Condicional não encontrado."}), 404
    if conditional.get("status") == "finalized":
        return jsonify({"ok": False, "error": "Condicional já finalizado."}), 409

    selected_ids = {str(item.get("productId", "")) for item in payload.get("finalItems") or []}
    final_items = [item for item in conditional.get("items", []) or [] if str(item.get("productId", "")) in selected_ids]
    updated = {
        **conditional,
        "status": "finalized",
        "finalItems": final_items,
        "finalizedAt": utc_now(),
        "updatedAt": utc_now(),
    }
    state["conditionals"] = [updated if str(item.get("id", "")) == conditional_id else item for item in conditionals]
    write_app_state_only(state)
    record_audit("update", "conditional", conditional_id, {"finalItems": final_items, "status": "finalized"})
    return jsonify({"ok": True, "data": updated})


@app.post("/api/returns")
def create_return_api():
    if not session.get("user"):
        return jsonify({"ok": False, "error": "Login obrigatório."}), 401
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"ok": False, "error": "Envie um JSON válido."}), 400
    sale_id = str(payload.get("saleId", "")).strip()
    items_payload = payload.get("items") or []
    if not sale_id or not items_payload:
        return jsonify({"ok": False, "error": "Informe a venda e os itens da devolução."}), 400
    init_db()
    with connect_db() as conn:
        sale_row = conn.execute(
            """
            SELECT id, customer_name AS customerName, status
            FROM sales
            WHERE store_id = ? AND id = ?
            """,
            ("matriz", sale_id),
        ).fetchone()
        if not sale_row:
            return jsonify({"ok": False, "error": "Venda não encontrada."}), 404
        if sale_row["status"] == "cancelled":
            return jsonify({"ok": False, "error": "Venda cancelada não pode ter devolução."}), 409
        sold_rows = conn.execute(
            """
            SELECT product_id AS productId, name, unit_price AS unitPrice, quantity
            FROM sale_items
            WHERE sale_id = ?
            """,
            (sale_id,),
        ).fetchall()
        sold_by_product = {row["productId"]: row for row in sold_rows}
        return_items = []
        for item in items_payload:
            product_id = str(item.get("productId", "")).strip()
            action = str(item.get("action", "")).strip()
            quantity = max(0, int(float(item.get("quantity", 0) or 0)))
            sold = sold_by_product.get(product_id)
            if action not in {"return", "exchange"} or not sold or quantity <= 0 or quantity > int(sold["quantity"] or 0):
                return jsonify({"ok": False, "error": "Item de devolução inválido."}), 400
            unit_price = float(item.get("unitPrice", sold["unitPrice"]) or 0)
            return_items.append({
                "productId": product_id,
                "productName": str(item.get("productName", sold["name"]) or ""),
                "action": action,
                "quantity": quantity,
                "unitPrice": unit_price,
                "total": money_round(quantity * unit_price),
            })
        if not return_items:
            return jsonify({"ok": False, "error": "Informe ao menos um item para devolver."}), 400

        product_ids = [item["productId"] for item in return_items]
        placeholders = ",".join("?" for _ in product_ids)
        product_rows = conn.execute(
            f"""
            SELECT id, barcode, name, size, color, gender, category_name AS category,
                   brand_name AS brand, stock, min_stock AS minStock, description,
                   active, cost, price, photo, updated_at AS updatedAt
            FROM products
            WHERE store_id = ? AND id IN ({placeholders})
            """,
            ("matriz", *product_ids),
        ).fetchall()
        products_by_id = {row["id"]: row for row in product_rows}
        updated_products = []
        for item in return_items:
            row = products_by_id.get(item["productId"])
            if not row:
                continue
            product = product_from_row(row)
            product["stock"] = int(product["stock"] or 0) + int(item["quantity"] or 0)
            product["updatedAt"] = utc_now()
            updated_products.append(product)

        return_doc = {
            "id": str(payload.get("id") or os.urandom(16).hex()),
            "saleId": sale_id,
            "customerName": sale_row["customerName"] or "",
            "items": return_items,
            "total": money_round(sum(item["total"] for item in return_items)),
            "reason": str(payload.get("reason", "") or "").strip(),
            "notes": str(payload.get("notes", "") or "").strip(),
            "createdAt": str(payload.get("createdAt") or utc_now()),
        }

    sync_return_to_state(return_doc, updated_products)
    record_audit("create", "return", return_doc["id"], {"return": return_doc})
    return jsonify({"ok": True, "data": {"return": return_doc, "products": updated_products}}), 201


@app.get("/api/cash-movements")
def list_cash_movements():
    init_db()
    with connect_db() as conn:
        rows = conn.execute(
            """
            SELECT id, direction, type, description, method, amount,
                   ref_id AS refId, created_at AS createdAt
            FROM cash_movements
            WHERE store_id = ?
            ORDER BY created_at DESC
            """,
            ("matriz",),
        ).fetchall()
    return jsonify({"ok": True, "data": [dict(row) for row in rows]})


@app.post("/api/cash-movements")
def create_cash_movement_api():
    if not session.get("user"):
        return jsonify({"ok": False, "error": "Login obrigatório."}), 401
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"ok": False, "error": "Envie um JSON válido."}), 400
    movement = normalize_cash_movement_payload(payload)
    if movement["direction"] not in {"in", "out"}:
        return jsonify({"ok": False, "error": "Tipo de movimentação inválido."}), 400
    if movement["amount"] <= 0:
        return jsonify({"ok": False, "error": "Valor deve ser maior que zero."}), 400
    if not movement["description"]:
        return jsonify({"ok": False, "error": "Descrição é obrigatória."}), 400
    if movement["direction"] == "out" and movement["type"] in {"", "manual"}:
        return jsonify({"ok": False, "error": "Tipo de despesa obrigatorio para saidas."}), 400
    persist_cash_movement(movement)
    return jsonify({"ok": True, "data": {"cash": [movement], "receivables": []}}), 201


@app.get("/api/cash-closings")
def list_cash_closings_api():
    init_db()
    with connect_db() as conn:
        rows = conn.execute(
            """
            SELECT id, date, expected_cash AS expectedCash, informed_cash AS informedCash,
                   difference, total_balance AS totalBalance, cash_in AS cashIn, cash_out AS cashOut,
                   notes, user_id AS userId, user_name AS userName, created_at AS createdAt
            FROM cash_closings
            WHERE store_id = ?
            ORDER BY date DESC, created_at DESC
            """,
            ("matriz",),
        ).fetchall()
    return jsonify({"ok": True, "data": [dict(row) for row in rows]})


@app.post("/api/cash-closings")
def create_cash_closing_api():
    if not session.get("user"):
        return jsonify({"ok": False, "error": "Login obrigatório."}), 401
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"ok": False, "error": "Envie um JSON válido."}), 400
    date = str(payload.get("date") or datetime.now().date().isoformat()).strip()[:10]
    informed_cash = money_round(payload.get("informedCash", 0))
    notes = str(payload.get("notes", "") or "").strip()
    state, _ = read_state()
    metrics = cash_closing_metrics(state, date)
    user = session.get("user") or {}
    closing = {
        "id": os.urandom(16).hex(),
        "date": date,
        "expectedCash": metrics["expectedCash"],
        "informedCash": informed_cash,
        "difference": money_round(informed_cash - metrics["expectedCash"]),
        "totalBalance": metrics["totalBalance"],
        "cashIn": metrics["cashIn"],
        "cashOut": metrics["cashOut"],
        "notes": notes,
        "userId": user.get("id", ""),
        "userName": user.get("name", ""),
        "createdAt": utc_now(),
    }
    persist_cash_closing(closing)
    return jsonify({"ok": True, "data": closing}), 201


@app.post("/api/card-receipts")
def create_card_receipt_api():
    if not session.get("user"):
        return jsonify({"ok": False, "error": "Login obrigatório."}), 401
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"ok": False, "error": "Envie um JSON válido."}), 400
    description = str(payload.get("description", "") or "Recebimento de cartão").strip()
    created_at = str(payload.get("createdAt") or utc_now())
    credit = money_round(payload.get("credit", 0))
    debit = money_round(payload.get("debit", 0))
    generic_amount = money_round(payload.get("amount", 0))
    movements = []
    if credit > 0:
        movements.append(normalize_cash_movement_payload({
            "direction": "in",
            "type": payload.get("type", "conta bancária"),
            "description": f"{description} - Crédito",
            "method": "card",
            "amount": credit,
            "createdAt": created_at,
        }))
    if debit > 0:
        movements.append(normalize_cash_movement_payload({
            "direction": "in",
            "type": payload.get("type", "conta bancária"),
            "description": f"{description} - Débito",
            "method": "card",
            "amount": debit,
            "createdAt": created_at,
        }))
    if generic_amount > 0 and not movements:
        movements.append(normalize_cash_movement_payload({
            "direction": "in",
            "type": payload.get("type", "receber cartoes"),
            "description": description,
            "method": "card",
            "amount": generic_amount,
            "createdAt": created_at,
        }))
    total = money_round(sum(movement["amount"] for movement in movements))
    if total <= 0:
        return jsonify({"ok": False, "error": "Informe um valor recebido."}), 400
    receivables = sync_cash_movements_to_state(movements, settle_card_amount=total)
    record_audit("create", "card_receipt", "", {"total": total, "movements": movements, "receivables": receivables})
    return jsonify({"ok": True, "data": {"cash": movements, "receivables": receivables}}), 201


@app.get("/api/receivables")
def list_receivables():
    init_db()
    with connect_db() as conn:
        rows = conn.execute(
            """
            SELECT id, sale_id AS saleId, customer_id AS customerId, customer_name AS customerName,
                   method, amount, received, status, due_date AS dueDate,
                   paid_at AS paidAt, last_payment_at AS lastPaymentAt,
                   installment, created_at AS createdAt, updated_at AS updatedAt
            FROM receivables
            WHERE store_id = ?
            ORDER BY COALESCE(due_date, created_at), created_at
            """,
            ("matriz",),
        ).fetchall()
        payment_rows = conn.execute(
            """
            SELECT id, receivable_id AS receivableId, sale_id AS saleId, customer_id AS customerId,
                   method, amount, created_at AS createdAt, note
            FROM receivable_payments
            WHERE store_id = ?
            ORDER BY created_at, id
            """,
            ("matriz",),
        ).fetchall()
    payments_by_receivable: dict[str, list[dict]] = {}
    for payment in payment_rows:
        row = dict(payment)
        payments_by_receivable.setdefault(row.pop("receivableId"), []).append(row)
    data = []
    for row in rows:
        item = dict(row)
        item["payments"] = payments_by_receivable.get(item["id"], [])
        data.append(item)
    return jsonify({"ok": True, "data": data})


@app.post("/api/receivables/payments")
def pay_receivables_api():
    if not session.get("user"):
        return jsonify({"ok": False, "error": "Login obrigatório."}), 401
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"ok": False, "error": "Envie um JSON válido."}), 400
    customer_id = str(payload.get("customerId", "") or "").strip()
    method = str(payload.get("method", "") or "").strip()
    created_at = str(payload.get("createdAt") or utc_now())
    rows = payload.get("payments") or []
    if method not in {"cash", "pix", "debit", "credit"}:
        return jsonify({"ok": False, "error": "Forma de pagamento inválida."}), 400
    if not customer_id or not rows:
        return jsonify({"ok": False, "error": "Informe cliente e parcelas."}), 400

    state, _ = read_state()
    customer = next((item for item in state.get("customers", []) if item.get("id") == customer_id), None)
    if not customer:
        return jsonify({"ok": False, "error": "Cliente não encontrado."}), 404

    payments_by_id = {
        str(item.get("receivableId", "") or ""): money_round(item.get("amount", 0))
        for item in rows
        if money_round(item.get("amount", 0)) > 0
    }
    if not payments_by_id:
        return jsonify({"ok": False, "error": "Informe pelo menos um valor para receber."}), 400

    changed_receivables = []
    total = 0.0
    for receivable in state.get("receivables", []):
        amount = payments_by_id.get(receivable.get("id"))
        if not amount:
            continue
        if receivable.get("customerId") != customer_id or receivable.get("method") != "storeCredit" or receivable.get("status") == "cancelled":
            return jsonify({"ok": False, "error": "Parcela inválida para este cliente."}), 400
        balance = money_round(float(receivable.get("amount") or 0) - float(receivable.get("received") or 0))
        if amount > balance + 0.01:
            return jsonify({"ok": False, "error": "Valor recebido maior que o saldo da parcela."}), 400
        receivable["received"] = money_round(float(receivable.get("received") or 0) + amount)
        receivable["lastPaymentAt"] = created_at
        receivable["updatedAt"] = created_at
        payment_entry = {
            "id": os.urandom(16).hex(),
            "receivableId": receivable.get("id", ""),
            "saleId": receivable.get("saleId", ""),
            "customerId": customer_id,
            "method": method,
            "amount": amount,
            "createdAt": created_at,
            "note": str(payload.get("description", "") or "").strip(),
        }
        receivable["payments"] = [*receivable.get("payments", []), payment_entry]
        if money_round(float(receivable.get("amount") or 0) - float(receivable.get("received") or 0)) <= 0.01:
            receivable["status"] = "paid"
            receivable["paidAt"] = created_at
        else:
            receivable["status"] = "open"
        changed_receivables.append(receivable)
        total = money_round(total + amount)

    if len(changed_receivables) != len(payments_by_id):
        return jsonify({"ok": False, "error": "Uma ou mais parcelas não foram encontradas."}), 404

    cash = []
    created_receivables = []
    description = str(payload.get("description", "") or f"Recebimento crediário - {customer.get('name', '')}").strip()
    if method in {"cash", "pix"}:
        cash.append(normalize_cash_movement_payload({
            "direction": "in",
            "type": "crediario",
            "description": description,
            "method": method,
            "amount": total,
            "refId": customer_id,
            "createdAt": created_at,
        }))
        state["cash"] = [*cash, *state.get("cash", [])]
    else:
        created = {
            "id": os.urandom(16).hex(),
            "saleId": "",
            "customerId": customer_id,
            "customerName": customer.get("name", ""),
            "method": method,
            "amount": total,
            "received": 0,
            "status": "cardPending",
            "dueDate": created_at[:10],
            "paidAt": "",
            "lastPaymentAt": "",
            "installment": "",
            "createdAt": created_at,
            "updatedAt": created_at,
        }
        created_receivables.append(created)
        state["receivables"] = [created, *state.get("receivables", [])]

    write_state(state)
    record_audit("pay", "receivable", customer_id, {"customerId": customer_id, "method": method, "total": total, "receivables": changed_receivables, "cash": cash, "createdReceivables": created_receivables})
    return jsonify({"ok": True, "data": {"receivables": [*changed_receivables, *created_receivables], "cash": cash}})


@app.get("/api/payables")
def list_payables():
    init_db()
    with connect_db() as conn:
        rows = conn.execute(
            """
            SELECT id, supplier, category, amount, issue_date AS issueDate,
                   due_date AS dueDate, notes, paid_amount AS paidAmount,
                   fee, discount, status, paid_at AS paidAt, created_at AS createdAt,
                   updated_at AS updatedAt
            FROM payables
            WHERE store_id = ?
            ORDER BY due_date, created_at
            """,
            ("matriz",),
        ).fetchall()
    return jsonify({"ok": True, "data": [payable_from_row(row) for row in rows]})


@app.post("/api/payables")
def create_payable_api():
    if not session.get("user"):
        return jsonify({"ok": False, "error": "Login obrigatório."}), 401
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"ok": False, "error": "Envie um JSON válido."}), 400
    payable = normalize_payable_payload(payload)
    error = validate_payable(payable)
    if error:
        return jsonify({"ok": False, "error": error}), 400
    sync_payable_to_state(payable)
    record_audit("create", "payable", payable["id"], {"payable": payable})
    return jsonify({"ok": True, "data": payable}), 201


@app.put("/api/payables/<payable_id>")
def update_payable_api(payable_id: str):
    if not session.get("user"):
        return jsonify({"ok": False, "error": "Login obrigatório."}), 401
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"ok": False, "error": "Envie um JSON válido."}), 400
    init_db()
    with connect_db() as conn:
        row = conn.execute(
            """
            SELECT id, supplier, category, amount, issue_date AS issueDate,
                   due_date AS dueDate, notes, paid_amount AS paidAmount,
                   fee, discount, status, paid_at AS paidAt, created_at AS createdAt,
                   updated_at AS updatedAt
            FROM payables
            WHERE store_id = ? AND id = ?
            """,
            ("matriz", payable_id),
        ).fetchone()
    if not row:
        return jsonify({"ok": False, "error": "Conta não encontrada."}), 404
    payable = normalize_payable_payload(payload, payable_from_row(row))
    payable["id"] = payable_id
    error = validate_payable(payable)
    if error:
        return jsonify({"ok": False, "error": error}), 400
    sync_payable_to_state(payable)
    record_audit("update", "payable", payable["id"], {"payable": payable})
    return jsonify({"ok": True, "data": payable})


@app.post("/api/payables/<payable_id>/pay")
def pay_payable_api(payable_id: str):
    if not session.get("user"):
        return jsonify({"ok": False, "error": "Login obrigatório."}), 401
    payload = request.get_json(silent=True) or {}
    init_db()
    with connect_db() as conn:
        row = conn.execute(
            """
            SELECT id, supplier, category, amount, issue_date AS issueDate,
                   due_date AS dueDate, notes, paid_amount AS paidAmount,
                   fee, discount, status, paid_at AS paidAt, created_at AS createdAt,
                   updated_at AS updatedAt
            FROM payables
            WHERE store_id = ? AND id = ?
            """,
            ("matriz", payable_id),
        ).fetchone()
    if not row:
        return jsonify({"ok": False, "error": "Conta não encontrada."}), 404
    payable = payable_from_row(row)
    if payable["status"] == "paid":
        return jsonify({"ok": False, "error": "Conta já está paga."}), 409
    fee = money_round(payload.get("fee", payable.get("fee", 0)))
    discount = money_round(payload.get("discount", payable.get("discount", 0)))
    total_due = money_round(payable["amount"] + fee - discount)
    open_amount = max(0, money_round(total_due - float(payable.get("paidAmount") or 0)))
    payment_amount = money_round(payload.get("amount", open_amount))
    if payment_amount <= 0:
        return jsonify({"ok": False, "error": "Valor pago deve ser maior que zero."}), 400
    if payment_amount - open_amount > 0.01:
        return jsonify({"ok": False, "error": "Valor pago nao pode ser maior que o saldo em aberto."}), 400
    paid_at = str(payload.get("paidAt") or utc_now())
    method = str(payload.get("method") or "pix").strip()
    payable["fee"] = fee
    payable["discount"] = discount
    payable["paidAmount"] = money_round(float(payable.get("paidAmount") or 0) + payment_amount)
    payable["status"] = "paid" if payable["paidAmount"] + 0.01 >= total_due else "pending"
    payable["paidAt"] = paid_at
    payable["updatedAt"] = utc_now()
    movement = normalize_cash_movement_payload({
        "direction": "out",
        "type": "contas a pagar",
        "description": f"{payable['category']}{' - ' + str(payload.get('note')).strip() if payload.get('note') else ''}",
        "method": method,
        "amount": payment_amount,
        "refId": payable_id,
        "createdAt": paid_at,
    })
    sync_payable_to_state(payable, [movement])
    record_audit("pay", "payable", payable_id, {"payable": payable, "cash": [movement]})
    return jsonify({"ok": True, "data": {"payable": payable, "cash": [movement]}})


@app.put("/api/state")
def put_state():
    _, error_response = require_data_import_reset_permission("state_replace")
    if error_response:
        return error_response
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"ok": False, "error": "Envie um JSON valido."}), 400
    state = {**default_state(), **payload}
    if not state.get("users"):
        state["users"] = default_state()["users"]
    updated_at = write_state(state)
    record_audit("replace", "state", "app_state", {"updatedAt": updated_at})
    return jsonify({"ok": True, "updatedAt": updated_at})


if __name__ == "__main__":
    init_db()
    ensure_startup_backup()
    host = os.environ.get("HOST", "127.0.0.1")
    try:
        port = int(float(os.environ.get("PORT", "5005") or 5005))
    except ValueError:
        port = 5005
    app.run(host=host, port=port, debug=not IS_PRODUCTION, use_reloader=False)
