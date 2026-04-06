from domain import InventoryInstance
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class InventoryInstanceRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    async def init_database(self):
        await self.execute("""
                CREATE TABLE IF NOT EXISTS inventory_instances (
                    instance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER NOT NULL,
                    item_id INTEGER NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY(player_id) REFERENCES players(player_id),
                    FOREIGN KEY(item_id) REFERENCES items(item_id)
                )
            """)
        await self.execute("PRAGMA journal_mode=WAL;")

    # ---------- Queries ----------

    async def get_by_id(self, instance_id: int) -> Optional[InventoryInstance]:
        row = await self.fetchrow(
            "SELECT * FROM inventory_instances WHERE instance_id = ?", (instance_id,)
        )
        return InventoryInstance(data=dict(row)) if row else None

    async def get_all(self) -> List[InventoryInstance]:
        rows = await self.fetch("SELECT * FROM inventory_instances")
        return [InventoryInstance(data=dict(row)) for row in rows]

    # ---------- Mutations ----------

    async def add(self, inventory_instance: InventoryInstance) -> tuple[bool, int]:
        last_id = await self.insert("""
            INSERT INTO inventory_instances (
                player_id, item_id, metadata
            )
            VALUES (?, ?, ?)
        """, (
            inventory_instance.player_id,
            inventory_instance.item_id,
            str(inventory_instance.metadata)
        ))
        return (last_id > 0, last_id)

    async def update(self, inventory_instance: InventoryInstance) -> bool:
        last_id = await self.update("""
            UPDATE inventory_instances
            SET player_id = ?, item_id = ?, metadata = ?
            WHERE instance_id = ?
            """, (
                inventory_instance.player_id,
                inventory_instance.item_id,
                str(inventory_instance.metadata),
                inventory_instance.instance_id
            ))
        return last_id > 0

    async def delete(self, inventory_instance: InventoryInstance) -> bool:
        last_id = await self.delete(
            "DELETE FROM inventory_instances WHERE instance_id = ?",
            (inventory_instance.instance_id,)
        )
        return last_id > 0

    async def exists(self, instance_id: int) -> bool:
        row = await self.fetchrow(
            "SELECT 1 FROM inventory_instances WHERE instance_id = ?", (instance_id,)
        )
        return row is not None