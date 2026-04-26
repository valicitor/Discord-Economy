from domain import PlayerInventory, IRepository
from infrastructure import BaseRepository
from typing import List, Optional

class PlayerInventoryRepository(BaseRepository, IRepository):
    
    # ---------- Schema Setup ----------

    async def init_database(self):
        """
        initalizes the database schema for the action_logs table. Called automatically on first use. Override in child classes to create tables.
        connection is managed by BaseRepository, so we can use super() to execute our schema setup queries.
        """
        conn = await super().acquire_connection()

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS player_inventory (
                inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                catalogue_id INTEGER NOT NULL,
                status TEXT DEFAULT 'active',
                quantity INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY(player_id) REFERENCES players(player_id),
                FOREIGN KEY(catalogue_id) REFERENCES catalogue(catalogue_id)
                UNIQUE(player_id, catalogue_id, status)
            )
        """)

        await conn.commit()
    
    # ---------- Teardown ----------

    async def drop_table(self):
        """
        Drops the player_inventory table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        await super().execute(f"DROP TABLE IF EXISTS player_inventory")

    async def clear_all(self) -> bool:
        """
        Clears all data from the player_inventory table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        affected = await super().delete(
            "DELETE FROM player_inventory"
        )
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "player_inventory")
        return affected > 0

    # ---------- Queries ----------

    async def get_by_id(self, inventory_id: int) -> Optional[PlayerInventory]:
        row = await super().fetchrow(
            "SELECT * FROM player_inventory WHERE inventory_id = ?",
            inventory_id
        )
        return PlayerInventory(data=dict(row)) if row else None

    async def get_all(self) -> List[PlayerInventory]:
        rows = await super().fetch("SELECT * FROM player_inventory")
        return [PlayerInventory(data=dict(row)) for row in rows]
    
    # ---------- Additional Queries ----------

    async def get_all_by_player_id(self, player_id: int) -> List[PlayerInventory]:
        rows = await super().fetch("SELECT * FROM player_inventory WHERE player_id = ?", player_id)
        return [PlayerInventory(data=dict(row)) for row in rows]
    
    async def get_by_player_catalogue_id(self, player_id: int, catalogue_id: int, status: str) -> Optional[PlayerInventory]:
        row = await super().fetchrow(
            "SELECT * FROM player_inventory WHERE player_id = ? AND catalogue_id = ? AND status = ?",
            player_id,
            catalogue_id,
            status
        )
        return PlayerInventory(data=dict(row)) if row else None
    
    # ---------- Existence Checks ----------

    async def exists(self, inventory_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM player_inventory WHERE inventory_id = ?",
            inventory_id
        )
        return row is not None
    
    # ---------- Additional Existence Checks ----------

    async def exists_by_player_catalogue_id(self, player_id: int, catalogue_id: int, status: str) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM player_inventory WHERE player_id = ? AND catalogue_id = ? AND status = ?",
            player_id,
            catalogue_id,
            status
        )
        return row is not None

    # ---------- Mutations ----------

    async def insert(self, player_inventory: PlayerInventory) -> int:
        return await super().insert(
            "INSERT INTO player_inventory (player_id, catalogue_id, quantity, status) VALUES (?, ?, ?, ?)",
            player_inventory.player_id,
            player_inventory.catalogue_id,
            player_inventory.quantity,
            player_inventory.status
        )

    async def update(self, player_inventory: PlayerInventory) -> bool:
        affected = await super().update(
            "UPDATE player_inventory SET player_id = ?, catalogue_id = ?, quantity = ?, status = ? WHERE inventory_id = ?",
            player_inventory.player_id,
            player_inventory.catalogue_id,
            player_inventory.quantity,
            player_inventory.status,
            player_inventory.inventory_id
        )
        return affected > 0

    async def delete(self, player_inventory: PlayerInventory) -> bool:
        affected = await super().delete(
            "DELETE FROM player_inventory WHERE inventory_id = ?",
            player_inventory.inventory_id
        )
        return affected > 0
    
    async def delete_all(self, player_id: int) -> bool:
        # Delete_all and clear_all do the same in this repository since there are no environment variables to restrict by.
        affected = await super().delete(
            "DELETE FROM player_inventory WHERE player_id = ?",
            player_id
        )
        return affected > 0