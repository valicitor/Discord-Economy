from domain import Item
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional

class ItemRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(db_path=db_path or "dynamic_resources.db")
        if seeder: 
            seeder(self)

    # ---------- Database Setup ----------

    def init_database(self):
        with self._lock:
            c = self.conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    icon TEXT NOT NULL,
                    price INTEGER NOT NULL,
                    description TEXT DEFAULT '',
                    stock INTEGER NOT NULL DEFAULT -1,
                    inventory BOOLEAN NOT NULL DEFAULT 1,
                    usable BOOLEAN NOT NULL DEFAULT 1,
                    sellable BOOLEAN NOT NULL DEFAULT 1,
                    FOREIGN KEY(server_id) REFERENCES servers(server_id)
                )
            """)
            c.execute("""
                CREATE INDEX IF NOT EXISTS idx_items_server_item_id ON items(server_id, item_id);
            """)

            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.commit()

    # ---------- Helpers ----------

    def _ensure_connection(self):
        if self.conn is None:
            raise RuntimeError("Database connection is closed")

    # ---------- Queries ----------

    def get_by_id(self, server_id: int, item_id: int) -> Optional[Item]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("SELECT * FROM items WHERE item_id = ? AND server_id = ?", (item_id, server_id))

            row = c.fetchone()
            return Item(data=dict(row)) if row else None

    def get_all(self, server_id: int) -> List[Item]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("SELECT * FROM items WHERE server_id = ?", (server_id,))

            return [Item(data=dict(row)) for row in c.fetchall()]

    def get_count(self, server_id: int) -> int:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT COUNT(*) FROM items WHERE server_id = ?",
                (server_id,)
            )
            return c.fetchone()[0]

    # ---------- Mutations ----------

    def add(self, item: Item) -> tuple[bool, int]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                INSERT INTO items (
                    server_id, name, category, icon, price, description, stock, inventory, usable, sellable
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.server_id,
                item.name,
                item.category,
                item.icon,
                item.price,
                item.description,
                item.stock,
                item.inventory,
                item.usable,
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
                SET name = ?, category = ?, icon = ?, price = ?, description = ?, stock = ?, inventory = ?, usable = ?, sellable = ?
                WHERE item_id = ? AND server_id = ?
            """, (
                item.name,
                item.category,
                item.icon,
                item.price,
                item.description,
                item.stock,
                item.inventory,
                item.usable,
                item.sellable,
                
                item.item_id,
                item.server_id
            ))

            self.conn.commit()
            return c.rowcount > 0

    def delete(self, item: Item) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "DELETE FROM items WHERE item_id = ? AND server_id = ?",
                (item.item_id, item.server_id)
            )

            self.conn.commit()
            return c.rowcount > 0

    def delete_all(self, server_id: int) -> int:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "DELETE FROM items WHERE server_id = ?",
                (server_id,)
            )

            self.conn.commit()
            return c.rowcount

    def exists(self, item_id: int, server_id: int) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT 1 FROM items WHERE item_id = ? AND server_id = ?",
                (item_id, server_id)
            )
            return c.fetchone() is not None