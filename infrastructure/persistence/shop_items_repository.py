from infrastructure.interfaces.i_shop_items_repository import IShopItemsRepository
from typing import List
import sqlite3
from threading import Lock

class ShopItemsRepository(IShopItemsRepository):
    _instance = None  # Class-level instance token
    _lock = Lock()  # Lock for thread-safe singleton

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(ShopItemsRepository, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_path=None):
        if not hasattr(self, '_initialized'):
            self.db_path = db_path or 'shop_items.db'
            self.init_database()
            self._initialized = True  # Mark as initialized
    
    def _get_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def init_database(self):
        conn = self._get_connection()
        try:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS shop_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    name TEXT NOT NULL UNIQUE,
                    category TEXT NOT NULL,
                    price INTEGER NOT NULL,
                    description TEXT DEFAULT '',
                    role_id INTEGER DEFAULT NULL
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
            c.execute('SELECT * FROM shop_items WHERE id = ?', (id,))
            row = c.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    async def get_all(self, guild_id: str) -> List[dict]:
        conn = self._get_connection()
        try:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute('SELECT * FROM shop_items WHERE guild_id = ?', (guild_id,))
            rows = c.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    async def add(self, entity: dict) -> bool:
        conn = self._get_connection()
        try:
            c = conn.cursor()
            c.execute('''
                INSERT INTO shop_items (guild_id, name, category, price, description, role_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (entity['guild_id'], entity['name'], entity['category'], entity['price'], entity['description'], entity['role_id']))
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
                UPDATE shop_items
                SET name = ?, category = ?, price = ?, description = ?, role_id = ?
                WHERE guild_id = ? AND id = ?
            ''', (entity['name'], entity['category'], entity['price'], entity['description'], entity['role_id'], entity['guild_id'], entity['id']))
            updated_count = c.rowcount
            conn.commit()
            return updated_count > 0
        finally:
            conn.close()

    async def delete(self, entity: dict) -> bool:
        conn = self._get_connection()
        try:
            c = conn.cursor()
            c.execute('DELETE FROM shop_items WHERE id = ?', (entity['id'],))
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
            c.execute('DELETE FROM shop_items WHERE guild_id = ?', (guild_id,))
            deleted_count = c.rowcount  # number of rows deleted
            conn.commit()
            return deleted_count
        finally:
            conn.close()

    async def exists(self, id: str, guild_id: str) -> bool:
        conn = self._get_connection()
        try:
            c = conn.cursor()
            c.execute('SELECT 1 FROM shop_items WHERE id = ? AND guild_id = ?', (str(id), str(guild_id)))
            return c.fetchone() is not None
        finally:
            conn.close()