from domain import PlayerInventory
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class PlayerInventoryRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    async def init_database(self):
        await self.execute("""
                CREATE TABLE IF NOT EXISTS player_inventory (
                    inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER NOT NULL,
                    item_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 1,
                    FOREIGN KEY(player_id) REFERENCES players(player_id),
                    FOREIGN KEY(item_id) REFERENCES items(item_id)
                )
            """)
        await self.execute("PRAGMA journal_mode=WAL;")

    # ---------- Queries ----------

    async def get_by_id(self, inventory_id: int) -> Optional[PlayerInventory]:
        row = await self.fetchrow(
            "SELECT * FROM player_inventory WHERE inventory_id = ?", (inventory_id,)
        )
        return PlayerInventory(data=dict(row)) if row else None

    async def get_all(self) -> List[PlayerInventory]:
        rows = await self.fetch("SELECT * FROM player_inventory")
        return [PlayerInventory(data=dict(row)) for row in rows]

    # ---------- Mutations ----------

    async def add(self, player_inventory: PlayerInventory) -> tuple[bool, int]:
        last_id = await self.insert("""
            INSERT INTO player_inventory (
                player_id, item_id, quantity
            )
                VALUES (?, ?, ?)
            """, (
                player_inventory.player_id,
                player_inventory.item_id,
                player_inventory.quantity
            ))

        return (last_id > 0, last_id)

    async def update(self, player_inventory: PlayerInventory) -> bool:
        last_id = await self.update("""
            UPDATE player_inventory
            SET quantity = ?
            WHERE inventory_id = ?
        """, (
            player_inventory.quantity,
            player_inventory.inventory_id
        ))

        return last_id > 0

    async def delete(self, player_inventory: PlayerInventory) -> bool:
        last_id = await self.delete(
            "DELETE FROM player_inventory WHERE inventory_id = ?",
            (player_inventory.inventory_id,)
        )

        return last_id > 0

    async def exists(self, inventory_id: int) -> bool:
        row = await self.fetchrow(
            "SELECT 1 FROM player_inventory WHERE inventory_id = ?", (inventory_id,)
        )
        return row is not None