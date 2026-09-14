from pathlib import Path
import logging as log
import sqlite3

# Minimal sqlite migration framework
# https://www.pythonlore.com/implementing-sqlite3-database-schema-migrations

BASE_DIR = Path(__file__).resolve().parent
MIGRATIONS_DIR = BASE_DIR / "migrations"


def get_applied_migrations(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY
        )
    """)
    cursor = conn.execute("SELECT version FROM schema_migrations")
    return {row[0] for row in cursor.fetchall()}


def apply_migration(conn, version, sql):
    log.debug(f"Applying migration {version}...")
    conn.executescript(sql)
    conn.execute("INSERT INTO schema_migrations (version) VALUES (?)", (version,))
    conn.commit()
    log.debug(f"Migration {version} applied.")


def init_database(db_path: Path):
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    applied = get_applied_migrations(conn)

    migrations = sorted(MIGRATIONS_DIR.glob("*.sql"))
    for migration in migrations:
        version = migration.stem.split("_")[0]
        if version not in applied:
            sql = migration.read_text()
            apply_migration(conn, version, sql)
        else:
            log.debug(f"Migration {version} already applied, skipping.")

    return conn
