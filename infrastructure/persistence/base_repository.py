import sqlite3
from threading import Lock, RLock
import atexit

class BaseRepository:
    _instance = None
    _instance_lock = Lock()

    # Shared transaction state per db_path
    _transaction_active_by_db_path = {}

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

            self._connections[self.db_path].row_factory = sqlite3.Row

            # Initialize shared transaction state for this db_path
            if self.db_path not in self._transaction_active_by_db_path:
                self._transaction_active_by_db_path[self.db_path] = False

            self._lock = RLock()  # Use reentrant lock to prevent self-deadlocks

            self.init_database()

            atexit.register(self.close)

            self._initialized = True

            if seeder: 
                seeder.Seed()
    
    def _acquire_lock(self, timeout=5):
        if not self._lock.acquire(timeout=timeout):
            raise RuntimeError("Failed to acquire lock within timeout")

    def _release_lock(self):
        try:
            self._lock.release()
        except RuntimeError:
            raise RuntimeError("Failed to release lock")

    def cursor(self):
        self._acquire_lock()
        try:
            self._ensure_connection()
            return self._connections[self.db_path].cursor()
        finally:
            self._release_lock()

    def commit(self):
        self._acquire_lock()
        try:
            self._ensure_connection()
            # Check shared transaction state
            if not self._transaction_active_by_db_path[self.db_path]:
                self._connections[self.db_path].commit()
        finally:
            self._release_lock()

    def execute(self, query: str):
        self._acquire_lock()
        try:
            self._ensure_connection()
            self._connections[self.db_path].execute(query)
        finally:
            self._release_lock()

    def _ensure_connection(self):
        if self._connections[self.db_path] is None:
            raise RuntimeError("Database connection is closed")

    def close(self):
        with self._lock:
            if self._connections[self.db_path]:
                self._connections[self.db_path].close()
                self._connections[self.db_path] = None

    def begin_transaction(self):
        self._acquire_lock()
        try:
            self._ensure_connection()
            if not self._transaction_active_by_db_path[self.db_path]:
                self._connections[self.db_path].execute("BEGIN")
                self._transaction_active_by_db_path[self.db_path] = True
        finally:
            self._release_lock()

    def commit_transaction(self):
        self._acquire_lock()
        try:
            self._ensure_connection()
            if self._transaction_active_by_db_path[self.db_path]:
                self._connections[self.db_path].commit()
                self._transaction_active_by_db_path[self.db_path] = False
        finally:
            self._release_lock()

    def rollback_transaction(self):
        self._acquire_lock()
        try:
            self._ensure_connection()
            if self._transaction_active_by_db_path[self.db_path]:
                self._connections[self.db_path].execute("ROLLBACK")
                self._transaction_active_by_db_path[self.db_path] = False
        finally:
            self._release_lock()

    def init_database(self):
        """Placeholder for child classes to override."""
        pass