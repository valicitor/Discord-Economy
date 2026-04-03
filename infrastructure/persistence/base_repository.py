import sqlite3
from threading import Lock
import atexit

class BaseRepository:
    _instance = None
    _instance_lock = Lock()

    _connections = {}

    def __new__(cls, *args, **kwargs):
        with cls._instance_lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, seeder=None, db_path: str = None):
        if not hasattr(self, "_initialized"):
            self.db_path = db_path or "repository.db"
            
            if self.db_path not in self._connections:
                self._connections[self.db_path] = sqlite3.connect(self.db_path, check_same_thread=False)

            self.conn = self._connections[db_path]
            self.conn.row_factory = sqlite3.Row

            self._lock = Lock()

            self.init_database()

            atexit.register(self.close)

            self._initialized = True

            if seeder: 
                seeder()

    def _ensure_connection(self):
        if self.conn is None:
            raise RuntimeError("Database connection is closed")

    def close(self):
        with self._lock:
            if self.conn:
                self.conn.close()
                self.conn = None