from domain import Item
from infrastructure import IItemRepository
from typing import List, Optional
import sqlite3
from threading import Lock
import atexit

class ItemRepository(IItemRepository):
    _instance = None
    _instance_lock = Lock()

    def __new__(cls, *args, **kwargs):
        with cls._instance_lock:
            if not cls._instance:
                cls._instance = super(ItemRepository, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_path: str = None):
        if not hasattr(self, "_initialized"):
            self.db_path = db_path or "items.db"
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self._lock = Lock()

            self.init_database()

            atexit.register(self.close)
            self._initialized = True

    # ---------- Database Setup ----------

    def init_database(self):
        with self._lock:
            c = self.conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    icon TEXT NOT NULL,
                    price INTEGER NOT NULL,
                    description TEXT DEFAULT '',
                    stock INTEGER NOT NULL DEFAULT -1,
                    inventory BOOLEAN NOT NULL DEFAULT 1,
                    useable BOOLEAN NOT NULL DEFAULT 1,
                    sellable BOOLEAN NOT NULL DEFAULT 1
                )
            """)
            c.execute("""
                CREATE INDEX idx_items_guild_item_id ON items(guild_id, item_id);
            """)

            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.commit()

    # ---------- Helpers ----------

    def _ensure_connection(self):
        if self.conn is None:
            raise RuntimeError("Database connection is closed")

    # ---------- Queries ----------

    def get_by_id(self, guild_id: int, item_id: int) -> Optional[Item]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("SELECT * FROM items WHERE item_id = ? AND guild_id = ?", (item_id, guild_id))

            row = c.fetchone()
            return Item(data=dict(row)) if row else None

    def get_all(self, guild_id: int) -> List[Item]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("SELECT * FROM items WHERE guild_id = ?", (guild_id))

            return [Item(data=dict(row)) for row in c.fetchall()]

    def get_count(self, guild_id: int) -> int:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT COUNT(*) FROM items WHERE guild_id = ?",
                (guild_id,)
            )
            return c.fetchone()[0]

    # ---------- Mutations ----------

    def add(self, item: Item) -> tuple[bool, int]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                INSERT INTO items (
                    guild_id, name, category, icon, price, description, stock, inventory, useable, sellable
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.guild_id,
                item.name,
                item.category,
                item.icon,
                item.price,
                item.description,
                item.stock,
                item.inventory,
                item.useable,
                item.sellable
            ))
            self.conn.commit()

            return (c.rowcount > 0), c.lastrowid

    def update(self, item: Item) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                UPDATE items
                SET name = ?, category = ?, icon = ?, price = ?, description = ?, stock = ?, inventory = ?, useable = ?, sellable = ?
                WHERE item_id = ? AND guild_id = ?
            """, (
                item.name,
                item.category,
                item.icon,
                item.price,
                item.description,
                item.stock,
                item.inventory,
                item.useable,
                item.sellable,
                
                item.item_id,
                item.guild_id
            ))

            self.conn.commit()
            return c.rowcount > 0

    def delete(self, item: Item) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "DELETE FROM items WHERE item_id = ? AND guild_id = ?",
                (item.item_id, item.guild_id)
            )

            self.conn.commit()
            return c.rowcount > 0

    def delete_all(self, guild_id: int) -> int:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "DELETE FROM items WHERE guild_id = ?",
                (guild_id,)
            )

            self.conn.commit()
            return c.rowcount

    def exists(self, item_id: int, guild_id: int) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT 1 FROM items WHERE item_id = ? AND guild_id = ?",
                (item_id, guild_id)
            )
            return c.fetchone() is not None

    # ---------- Cleanup ----------

    def close(self):
        with self._lock:
            if self.conn:
                self.conn.close()
                self.conn = None