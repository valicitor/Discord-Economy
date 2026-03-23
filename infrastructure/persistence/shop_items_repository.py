from infrastructure.interfaces.i_shop_items_repository import IShopItemsRepository
from typing import List
import sqlite3

class ShopItemsRepository(IShopItemsRepository):
    _instance = None  # Class-level instance token

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ShopItemsRepository, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_path='shop_items.db'):
        if not hasattr(self, '_initialized'):
            self.db_path = db_path
            self.init_database()
            self._initialized = True  # Mark as initialized

    def init_database(self):
        conn = sqlite3.connect(self.db_path)
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
        conn.close()

    async def get_by_id(self, id: str):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM shop_items WHERE id = ?', (id,))
            return c.fetchone()

    async def get_all(self, guild_id: str) -> List[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute('SELECT * FROM shop_items WHERE guild_id = ?', (guild_id,))
            rows = c.fetchall()
            return [dict(row) for row in rows]

    async def list(self, guild_id: str) -> List[dict]:
        return await self.get_all(guild_id)

    async def add(self, entity: dict) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO shop_items (guild_id, name, category, price, description, role_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (entity['guild_id'], entity['name'], entity['category'], entity['price'], entity['description'], entity['role_id']))
            add_count = c.rowcount
            conn.commit()
            return add_count > 0

    async def update(self, entity: dict) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''
                UPDATE shop_items
                SET name = ?, category = ?, price = ?, description = ?, role_id = ?
                WHERE guild_id = ? AND id = ?
            ''', (entity['name'], entity['category'], entity['price'], entity['description'], entity['role_id'], entity['guild_id'], entity['id']))
            updated_count = c.rowcount
            conn.commit()
            return updated_count > 0

    async def delete(self, entity: dict) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('DELETE FROM shop_items WHERE id = ?', (entity['id'],))
            deleted_count = c.rowcount
            conn.commit()
            return deleted_count > 0

    async def delete_all(self, guild_id: str) -> int:
        """Delete all shop items for a guild and return the number of deleted records"""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('DELETE FROM shop_items WHERE guild_id = ?', (guild_id,))
            deleted_count = c.rowcount  # number of rows deleted
            conn.commit()
            return deleted_count

    async def exists(self, id: str, guild_id: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('SELECT 1 FROM shop_items WHERE id = ? AND guild_id = ?', (str(id), str(guild_id)))
            return c.fetchone() is not None