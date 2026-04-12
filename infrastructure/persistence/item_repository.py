from domain import Item, IRepository
from infrastructure import BaseRepository
from typing import List, Optional

class ItemRepository(BaseRepository, IRepository):
    
    # ---------- Schema Setup ----------

    async def init_database(self):
        """
        initalizes the database schema for the items table. Called automatically on first use. Override in child classes to create tables.
        connection is managed by BaseRepository, so we can use super() to execute our schema setup queries.
        """
        conn = await super().acquire_connection()

        await conn.execute("""
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

        await conn.commit()
    
    # ---------- Teardown ----------

    async def drop_table(self):
        """
        Drops the items table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        await super().execute(f"DROP TABLE IF EXISTS items")

    async def clear_all(self) -> bool:
        """
        Clears all data from the items table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        affected = await super().delete(
            "DELETE FROM items"
        )
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "items")
        return affected > 0

    # ---------- Queries ----------

    async def get_by_id(self, item_id: int) -> Optional[Item]:
        row = await super().fetchrow(
            "SELECT * FROM items WHERE item_id = ?",
            item_id
        )
        return Item(data=dict(row)) if row else None

    async def get_all(self) -> List[Item]:
        rows = await super().fetch("SELECT * FROM items")
        return [Item(data=dict(row)) for row in rows]
    
    # ---------- Additional Queries ----------

    async def get_count(self, server_id: int) -> int:
        row = await super().fetchrow(
            "SELECT COUNT(*) FROM items WHERE server_id = ?", 
            server_id
        )
        return row[0] if row else 0
    
    # ---------- Existence Checks ----------

    async def exists(self, item_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM items WHERE item_id = ?",
            item_id
        )
        return row is not None
    
    # ---------- Additional Existence Checks ----------

    # ---------- Mutations ----------

    async def insert(self, item: Item) -> int:
        return await super().insert(
            "INSERT INTO items (server_id, name, category, icon, price, description, stock, inventory, usable, sellable) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
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
        )

    async def update(self, item: Item) -> bool:
        affected = await super().update(
            "UPDATE items SET server_id = ?, name = ?, category = ?, icon = ?, price = ?, description = ?, stock = ?, inventory = ?, usable = ?, sellable = ? WHERE item_id = ?",
            item.server_id,
            item.name,
            item.category,
            item.icon,
            item.price,
            item.description,
            item.stock,
            item.inventory,
            item.usable,
            item.sellable,
            item.item_id
        )
        return affected > 0

    async def delete(self, item: Item) -> bool:
        affected = await super().delete(
            "DELETE FROM items WHERE item_id = ?",
            item.item_id
        )
        return affected > 0
    
    async def delete_all(self, server_id: int) -> bool:
        # Delete_all and clear_all do the same in this repository since there are no environment variables to restrict by.
        affected = await super().delete(
            "DELETE FROM items WHERE server_id = ?",
            server_id
        )
        return affected > 0