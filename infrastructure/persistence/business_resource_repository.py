from domain import BusinessInventory, IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class BusinessInventoryRepository(BaseRepository, IRepository):

    async def init_database(self):
        conn = await super().acquire_connection()
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS business_inventory (
                inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER,
                business_id INTEGER NOT NULL,
                catalogue_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0,
                last_updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(business_id) REFERENCES businesses(business_id),
                FOREIGN KEY(catalogue_id) REFERENCES catalogue(catalogue_id),
                UNIQUE(business_id, catalogue_id)
            )
        """)
        await conn.commit()

    async def drop_table(self):
        await super().execute("DROP TABLE IF EXISTS business_inventory")

    async def clear_all(self) -> bool:
        affected = await super().delete("DELETE FROM business_inventory")
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "business_inventory")
        return affected > 0

    async def get_by_id(self, inventory_id: int) -> Optional[BusinessInventory]:
        row = await super().fetchrow("SELECT * FROM business_inventory WHERE inventory_id = ?", inventory_id)
        return BusinessInventory(data=dict(row)) if row else None

    async def get_all(self) -> List[BusinessInventory]:
        rows = await super().fetch("SELECT * FROM business_inventory")
        return [BusinessInventory(data=dict(row)) for row in rows]

    async def get_all_by_business(self, business_id: int) -> List[BusinessInventory]:
        rows = await super().fetch("SELECT * FROM business_inventory WHERE business_id = ?", business_id)
        return [BusinessInventory(data=dict(row)) for row in rows]

    async def get_by_business_catalogue(self, business_id: int, catalogue_id: int) -> Optional[BusinessInventory]:
        row = await super().fetchrow(
            "SELECT * FROM business_inventory WHERE business_id = ? AND catalogue_id = ?",
            business_id, catalogue_id
        )
        return BusinessInventory(data=dict(row)) if row else None

    async def get_nonempty_by_server(self, server_id: int, exclude_business_id: int) -> List[BusinessInventory]:
        rows = await super().fetch(
            """
            SELECT bi.* FROM business_inventory bi
            JOIN businesses b ON bi.business_id = b.business_id
            WHERE b.server_id = ? AND bi.quantity > 0 AND bi.business_id != ?
            """,
            server_id, exclude_business_id
        )
        return [BusinessInventory(data=dict(row)) for row in rows]

    async def exists(self, inventory_id: int) -> bool:
        row = await super().fetchrow("SELECT 1 FROM business_inventory WHERE inventory_id = ?", inventory_id)
        return row is not None

    async def insert(self, inventory: BusinessInventory) -> int:
        return await super().insert(
            "INSERT INTO business_inventory (server_id, business_id, catalogue_id, quantity, last_updated_at) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
            inventory.server_id, inventory.business_id, inventory.catalogue_id, inventory.quantity
        )

    async def update(self, inventory: BusinessInventory) -> bool:
        affected = await super().update(
            "UPDATE business_inventory SET server_id = ?, business_id = ?, catalogue_id = ?, quantity = ?, last_updated_at = CURRENT_TIMESTAMP WHERE inventory_id = ?",
            inventory.server_id, inventory.business_id, inventory.catalogue_id, inventory.quantity, inventory.inventory_id
        )
        return affected > 0

    async def delete(self, inventory: BusinessInventory) -> bool:
        affected = await super().delete("DELETE FROM business_inventory WHERE inventory_id = ?", inventory.inventory_id)
        return affected > 0

    async def delete_all(self, business_id: int = None) -> bool:
        if business_id:
            affected = await super().delete("DELETE FROM business_inventory WHERE business_id = ?", business_id)
        else:
            affected = await super().delete("DELETE FROM business_inventory")
        return affected > 0
