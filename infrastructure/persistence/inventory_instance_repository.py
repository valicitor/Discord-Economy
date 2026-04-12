from domain import InventoryInstance, IRepository
from infrastructure import BaseRepository
from typing import List, Optional

class InventoryInstanceRepository(BaseRepository, IRepository):
    
    # ---------- Schema Setup ----------

    async def init_database(self):
        """
        initalizes the database schema for the inventory_instances table. Called automatically on first use. Override in child classes to create tables.
        connection is managed by BaseRepository, so we can use super() to execute our schema setup queries.
        """
        conn = await super().acquire_connection()

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS inventory_instances (
                instance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                item_id INTEGER NOT NULL,
                metadata TEXT,
                FOREIGN KEY(player_id) REFERENCES players(player_id),
                FOREIGN KEY(item_id) REFERENCES items(item_id)
            )
        """)

        await conn.commit()
    
    # ---------- Teardown ----------

    async def drop_table(self):
        """
        Drops the inventory_instances table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        await super().execute(f"DROP TABLE IF EXISTS inventory_instances")

    async def clear_all(self) -> bool:
        """
        Clears all data from the inventory_instances table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        affected = await super().delete(
            "DELETE FROM inventory_instances"
        )
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "inventory_instances")
        return affected > 0

    # ---------- Queries ----------

    async def get_by_id(self, instance_id: int) -> Optional[InventoryInstance]:
        row = await super().fetchrow(
            "SELECT * FROM inventory_instances WHERE instance_id = ?",
            instance_id
        )
        return InventoryInstance(data=dict(row)) if row else None

    async def get_all(self) -> List[InventoryInstance]:
        rows = await super().fetch("SELECT * FROM inventory_instances")
        return [InventoryInstance(data=dict(row)) for row in rows]
    
    # ---------- Additional Queries ----------
    
    # ---------- Existence Checks ----------

    async def exists(self, instance_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM inventory_instances WHERE instance_id = ?",
            instance_id
        )
        return row is not None
    
    # ---------- Additional Existence Checks ----------

    # ---------- Mutations ----------

    async def insert(self, inventory_instance: InventoryInstance) -> int:
        return await super().insert(
            "INSERT INTO inventory_instances (player_id, item_id, metadata) VALUES (?, ?, ?)",
            inventory_instance.player_id,
            inventory_instance.item_id,
            str(inventory_instance.metadata)
        )

    async def update(self, inventory_instance: InventoryInstance) -> bool:
        affected = await super().update(
            "UPDATE inventory_instances SET player_id = ?, item_id = ?, metadata = ? WHERE instance_id = ?",
            inventory_instance.player_id,
            inventory_instance.item_id,
            str(inventory_instance.metadata),
            inventory_instance.instance_id
        )
        return affected > 0

    async def delete(self, inventory_instance: InventoryInstance) -> bool:
        affected = await super().delete(
            "DELETE FROM inventory_instances WHERE instance_id = ?",
            inventory_instance.instance_id
        )
        return affected > 0
    
    async def delete_all(self, player_id: int) -> bool:
        # Delete_all and clear_all do the same in this repository since there are no environment variables to restrict by.
        affected = await super().delete(
            "DELETE FROM inventory_instances WHERE player_id = ?",
            player_id
        )
        return affected > 0