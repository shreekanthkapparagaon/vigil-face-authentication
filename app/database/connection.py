import sqlite3
from pathlib import Path

from app.config import DATABASE_PATH


# ---------------------------------------------------------
# Database schema
# ---------------------------------------------------------

CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_code TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL DEFAULT '',
    email TEXT NOT NULL DEFAULT '',
    phone TEXT NOT NULL DEFAULT '',
    face_embedding BLOB NOT NULL,
    embedding_dimension INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_authenticated_at TEXT,
    is_active INTEGER NOT NULL DEFAULT 1
);
"""


# ---------------------------------------------------------
# Connection
# ---------------------------------------------------------


def get_connection() -> sqlite3.Connection:
    """
    Create and return a SQLite database connection.

    Row objects are returned as sqlite3.Row so database
    columns can be accessed by name.
    """
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=10.0,
    )

    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON;")
    connection.execute("PRAGMA journal_mode = WAL;")
    connection.execute("PRAGMA synchronous = NORMAL;")
    connection.execute("PRAGMA busy_timeout = 5000;")

    return connection


# ---------------------------------------------------------
# Initialization
# ---------------------------------------------------------


def initialize_database() -> None:
    """Create the application's database tables."""
    with get_connection() as connection:
        connection.execute(CREATE_USERS_TABLE)
        connection.commit()