# src/server/db/__init__.py

import os
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path

try:
    import config as netcfg
except ImportError:
    from .. import config as netcfg

from .schema import init_db

DEFAULT_DB_PATH = getattr(netcfg, "DB_PATH", "noxc2.db")


class Database:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Database, cls).__new__(cls)
            return cls._instance

    def __init__(self, db_path=None):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self.db_path = str(db_path or DEFAULT_DB_PATH)
        self._ensure_dir()
        self._init_sqlite()
        self._initialized = True

    def _ensure_dir(self):
        parent_dir = Path(self.db_path).parent
        if parent_dir and not parent_dir.exists():
            parent_dir.mkdir(parents=True, exist_ok=True)

    def _init_sqlite(self):
        with self.get_connection() as conn:
            init_db(conn)

    @contextmanager
    def get_connection(self):
        """
        Context manager providing an SQLite connection with WAL mode and foreign keys enabled.
        Automatically commits on completion, rolls back on exceptions, and closes the connection.
        """
        conn = sqlite3.connect(
            self.db_path,
            timeout=15.0,
            check_same_thread=False
        )
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA busy_timeout = 15000;")
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


# Singleton Instance
db = Database()

from .repository import (
    AgentRepository,
    TaskRepository,
    FileTransferRepository,
    LogRepository,
)

