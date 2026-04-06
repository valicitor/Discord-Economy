from domain import Equipment
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class EquipmentRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    async def init_database(self):
        await self.execute("""
                CREATE TABLE IF NOT EXISTS equipment (
                    equipment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    slot TEXT DEFAULT '',
                    metadata TEXT,
                    FOREIGN KEY(server_id) REFERENCES servers(server_id),
                    UNIQUE(name, server_id)
                )
            """)
        await self.execute("PRAGMA journal_mode=WAL;")

    # ---------- Queries ----------

    async def get_by_id(self, equipment_id: int) -> Optional[Equipment]:
        row = await self.fetchrow(
            "SELECT * FROM equipment WHERE equipment_id = ?", (equipment_id,)
        )
        return Equipment(data=dict(row)) if row else None
    
    async def get_by_name(self, name: str, server_id: int) -> Optional[Equipment]:
        row = await self.fetchrow(
            "SELECT * FROM equipment WHERE name = ? AND server_id = ?", (name, server_id)
        )
        return Equipment(data=dict(row)) if row else None

    async def get_all(self, server_id: int) -> List[Equipment]:
        rows = await self.fetch("SELECT * FROM equipment WHERE server_id = ?", (server_id,))
        return [Equipment(data=dict(row)) for row in rows]

    # ---------- Mutations ----------

    async def add(self, equipment: Equipment) -> tuple[bool, int]:
        last_id = await self.insert("""
            INSERT INTO equipment (
                server_id, name, description, slot, metadata
                    )
                VALUES (?, ?, ?, ?, ?)
            """, (
                equipment.server_id,
                equipment.name,
                equipment.description,
                equipment.slot,
                str(equipment.metadata)
            ))

        return (last_id > 0, last_id)

    async def update(self, equipment: Equipment) -> bool:
        rowcount = await self.update("""
            UPDATE equipment
            SET server_id = ?, name = ?, description = ?, slot = ?, metadata = ?
            WHERE equipment_id = ?
        """, (
            equipment.server_id,
            equipment.name,
            equipment.description,
            equipment.slot,
            str(equipment.metadata),
            equipment.equipment_id
        ))

        return rowcount > 0

    async def delete(self, equipment: Equipment) -> bool:
        rowcount = await self.delete(
            "DELETE FROM equipment WHERE equipment_id = ?",
            (equipment.equipment_id,)
        )
        return rowcount > 0
    
    async def delete_all(self, server_id: int) -> bool:
        rowcount = await self.delete("DELETE FROM equipment WHERE server_id = ?", (server_id,))
        return rowcount > 0

    async def exists(self, equipment_id: int) -> bool:
        row = await self.fetchrow(
            "SELECT 1 FROM equipment WHERE equipment_id = ?",
            (equipment_id,)
        )
        return row is not None