from infrastructure.interfaces.i_inventory_repository import IInventoryRepository
from typing import List
import sqlite3
from threading import Lock

class InventoryRepository(IInventoryRepository):
    _instance = None  # Class-level instance token
    _lock = Lock()  # Lock for thread-safe singleton

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(InventoryRepository, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_path=None):
        if not hasattr(self, '_initialized'):
            self.db_path = db_path or 'inventory.db'
            self.init_database()
            self._initialized = True  # Mark as initialized

    def _get_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def init_database(self):
        conn = self._get_connection()
        try:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS inventory (
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    item_name TEXT NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (user_id, guild_id, item_name)
                )
            ''')
            conn.commit()
        finally:
            conn.close()

    async def get_by_id(self, id: str):
        conn = self._get_connection()
        try:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute('SELECT * FROM inventory WHERE user_id = ?', (id,))
            row = c.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    async def get_all(self, guild_id: str) -> List[dict]:
        conn = self._get_connection()
        try:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute('SELECT * FROM inventory WHERE guild_id = ?', (guild_id,))
            rows = c.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    async def add(self, entity: dict) -> bool:
        conn = self._get_connection()
        try:
            c = conn.cursor()
            c.execute('''
                INSERT INTO inventory (user_id, guild_id, item_name, quantity)
                VALUES (?, ?, ?, ?)
            ''', (entity['user_id'], entity['guild_id'], entity['item_name'], entity['quantity']))
            add_count = c.rowcount
            conn.commit()
            return add_count > 0
        finally:
            conn.close()

    async def update(self, entity: dict) -> bool:
        conn = self._get_connection()
        try:
            c = conn.cursor()
            c.execute('''
                UPDATE inventory
                SET quantity = ?
                WHERE user_id = ? AND item_name = ? AND guild_id = ?
            ''', (entity['quantity'], entity['user_id'], entity['item_name'], entity['guild_id']))
            updated_count = c.rowcount
            conn.commit()
            return updated_count > 0
        finally:
            conn.close()

    async def delete(self, entity: dict) -> bool:
        conn = self._get_connection()
        try:
            c = conn.cursor()
            c.execute('DELETE FROM inventory WHERE user_id = ? AND item_name = ? AND guild_id = ?', (entity['user_id'], entity['item_name'], entity['guild_id']))
            deleted_count = c.rowcount
            conn.commit()
            return deleted_count > 0
        finally:
            conn.close()

    async def delete_all(self, guild_id: str) -> int:
        """Delete all shop items for a guild and return the number of deleted records"""
        conn = self._get_connection()
        try:
            c = conn.cursor()
            c.execute('DELETE FROM inventory WHERE guild_id = ?', (guild_id,))
            deleted_count = c.rowcount  # number of rows deleted
            conn.commit()
            return deleted_count
        finally:
            conn.close()

    async def exists(self, id: str, guild_id: str) -> bool:
        conn = self._get_connection()
        try:
            c = conn.cursor()
            c.execute('SELECT 1 FROM inventory WHERE user_id = ? AND item_name = ? AND guild_id = ?', (str(id), str(guild_id), str(guild_id)))
            return c.fetchone() is not None
        finally:
            conn.close()