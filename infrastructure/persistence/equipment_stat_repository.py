from domain import EquipmentStat
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class EquipmentStatRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    async def init_database(self):
        await self.execute("""
                CREATE TABLE IF NOT EXISTS equipment_stats (
                    equipment_stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    equipment_id INTEGER NOT NULL,
                    stat_key TEXT NOT NULL,
                    stat_value TEXT NOT NULL,
                    FOREIGN KEY(equipment_id) REFERENCES equipment(equipment_id)
                )
            """)
        await self.execute("PRAGMA journal_mode=WAL;")

    # ---------- Queries ----------

    async def get_by_id(self, equipment_stat_id: int) -> Optional[EquipmentStat]:
        row = await self.fetchrow(
            "SELECT * FROM equipment_stats WHERE equipment_stat_id = ?", (equipment_stat_id,)
        )
        return EquipmentStat(data=dict(row)) if row else None
    
    async def get_by_key(self, stat_key: str, equipment_id: int) -> Optional[EquipmentStat]:
        row = await self.fetchrow(
            "SELECT * FROM equipment_stats WHERE stat_key = ? AND equipment_id = ?", (stat_key, equipment_id)
        )
        return EquipmentStat(data=dict(row)) if row else None

    async def get_all(self, equipment_id: int|None = None) -> List[EquipmentStat]:
        if equipment_id is not None:
            rows = await self.fetch("SELECT * FROM equipment_stats WHERE equipment_id = ?", (equipment_id,))
        else:
            rows = await self.fetch("SELECT * FROM equipment_stats")
        return [EquipmentStat(data=dict(row)) for row in rows]

    async def get_all(self, equipment_id: int|None = None) -> List[EquipmentStat]:
        if equipment_id is not None:
            rows = await self.fetch("SELECT * FROM equipment_stats WHERE equipment_id = ?", (equipment_id,))
        else:
            rows = await self.fetch("SELECT * FROM equipment_stats")
        return [EquipmentStat(data=dict(row)) for row in rows]

    # ---------- Mutations ----------

    async def add(self, equipment_stat: EquipmentStat) -> tuple[bool, int]:
        last_id = await self.insert("""
            INSERT INTO equipment_stats (
                equipment_id, stat_key, stat_value
            )
            VALUES (?, ?, ?)
        """, (
            equipment_stat.equipment_id,
            equipment_stat.stat_key,
            equipment_stat.stat_value
        ))

        return (last_id > 0, last_id)

    async def update(self, equipment_stat: EquipmentStat) -> bool:
        rowcount = await self.update("""
            UPDATE equipment_stats
            SET equipment_id = ?, stat_key = ?, stat_value = ?
                WHERE equipment_stat_id = ?
            """, (
                equipment_stat.equipment_id,
                equipment_stat.stat_key,
                equipment_stat.stat_value,
                equipment_stat.equipment_stat_id
            ))

        return rowcount > 0

    async def delete(self, equipment_stat: EquipmentStat) -> bool:
        rowcount = await self.delete(
            "DELETE FROM equipment_stats WHERE equipment_stat_id = ?",
            (equipment_stat.equipment_stat_id,)
        )
        return rowcount > 0 

    async def delete_all(self) -> bool:
        rowcount = await self.delete("DELETE FROM equipment_stats")
        return rowcount > 0

    async def exists(self, equipment_stat_id: int) -> bool:
        row = await self.fetchrow(
            "SELECT 1 FROM equipment_stats WHERE equipment_stat_id = ?",
            (equipment_stat_id,)
        )
        return row is not None