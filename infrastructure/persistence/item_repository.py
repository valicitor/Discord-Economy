from domain import Item
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional

class ItemRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    # ---------- Database Setup ----------

    async def init_database(self):
        await self.execute("""
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
        await self.execute("""
            CREATE INDEX IF NOT EXISTS idx_items_server_item_id ON items(server_id, item_id);
        """)

        await self.execute("PRAGMA journal_mode=WAL;")

    # ---------- Queries ----------

    async def get_by_id(self, server_id: int, item_id: int) -> Optional[Item]:
        row = await self.fetchrow(
            "SELECT * FROM items WHERE item_id = ? AND server_id = ?", (item_id, server_id)
        )
        return Item(data=dict(row)) if row else None

    async def get_all(self, server_id: int) -> List[Item]:
        rows = await self.fetch("SELECT * FROM items WHERE server_id = ?", (server_id,))
        return [Item(data=dict(row)) for row in rows]

    async def get_count(self, server_id: int) -> int:
        row = await self.fetchrow(
            "SELECT COUNT(*) FROM items WHERE server_id = ?", (server_id,)
        )
        return row[0] if row else 0

    # ---------- Mutations ----------

    async def add(self, item: Item) -> tuple[bool, int]:
        last_id = await self.insert("""
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
        return (last_id > 0, last_id)

    async def update(self, item: Item) -> bool:
        last_id = await self.update("""
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
        return last_id > 0

    async def delete(self, item: Item) -> bool:
        last_id = await self.delete(
            "DELETE FROM items WHERE item_id = ? AND server_id = ?",
            (item.item_id, item.server_id)
        )
        return last_id > 0

    async def delete_all(self, server_id: int) -> int:
        last_id = await self.delete(
            "DELETE FROM items WHERE server_id = ?",
            (server_id,)
        )
        return last_id
    
    async def exists(self, item_id: int, server_id: int) -> bool:
        row = await self.fetchrow(
            "SELECT 1 FROM items WHERE item_id = ? AND server_id = ?", (item_id, server_id)
        )
        return row is not None