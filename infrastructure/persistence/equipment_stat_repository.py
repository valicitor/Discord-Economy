from domain import EquipmentStat, IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class EquipmentStatRepository(BaseRepository, IRepository):
    
    # ---------- Schema Setup ----------

    async def init_database(self):
        """
        initalizes the database schema for the actions table. Called automatically on first use. Override in child classes to create tables.
        connection is managed by BaseRepository, so we can use super() to execute our schema setup queries.
        """
        conn = await super().acquire_connection()

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS equipment_stats (
                equipment_stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                equipment_id INTEGER NOT NULL,
                stat_key TEXT NOT NULL,
                stat_value TEXT NOT NULL,
                FOREIGN KEY(equipment_id) REFERENCES equipment(equipment_id)
            )
        """)

        await conn.commit()
    
    # ---------- Teardown ----------

    async def drop_table(self):
        """
        Drops the equipment_stats table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        await super().execute(f"DROP TABLE IF EXISTS equipment_stats")

    async def clear_all(self) -> bool:
        """
        Clears all data from the equipment_stats table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        affected = await super().delete(
            "DELETE FROM equipment_stats"
        )
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "equipment_stats")
        return affected > 0

    # ---------- Queries ----------

    async def get_by_id(self, equipment_stat_id: int) -> Optional[EquipmentStat]:
        row = await super().fetchrow(
            "SELECT * FROM equipment_stats WHERE equipment_stat_id = ?",
            equipment_stat_id
        )
        return EquipmentStat(data=dict(row)) if row else None

    async def get_all(self, equipment_id: int|None = None) -> List[EquipmentStat]:
        if equipment_id is not None:
            rows = await super().fetch("SELECT * FROM equipment_stats WHERE equipment_id = ?", equipment_id)
        else:
            rows = await super().fetch("SELECT * FROM equipment_stats")
        return [EquipmentStat(data=dict(row)) for row in rows]
    
    # ---------- Additional Queries ----------

    async def get_by_key(self, stat_key: str, equipment_id: int) -> Optional[EquipmentStat]:
        row = await super().fetchrow(
            "SELECT * FROM equipment_stats WHERE stat_key = ? AND equipment_id = ?", 
            stat_key, 
            equipment_id
        )
        return EquipmentStat(data=dict(row)) if row else None
    
    # ---------- Existence Checks ----------

    async def exists(self, equipment_stat_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM equipment_stats WHERE equipment_stat_id = ?",
            equipment_stat_id
        )
        return row is not None
    
    # ---------- Additional Existence Checks ----------

    # ---------- Mutations ----------

    async def insert(self, equipment: EquipmentStat) -> int:
        return await super().insert(
            "INSERT INTO equipment_stats (equipment_id, stat_key, stat_value) VALUES (?, ?, ?)",
            equipment.equipment_id,
            equipment.stat_key,
            equipment.stat_value
        )
    
    async def update(self, equipment: EquipmentStat) -> bool:
        affected = await super().update(
            "UPDATE equipment_stats SET equipment_id = ?, stat_key = ?, stat_value = ? WHERE equipment_stat_id = ?",
            equipment.equipment_id,
            equipment.stat_key,
            equipment.stat_value,
            equipment.equipment_stat_id
        )
        return affected > 0

    async def delete(self, equipment: EquipmentStat) -> bool:
        affected = await super().delete(
            "DELETE FROM equipment_stats WHERE equipment_stat_id = ?",
            equipment.equipment_stat_id
        )
        return affected > 0
    
    async def delete_all(self) -> bool:
        # Delete_all and clear_all do the same in this repository since there are no environment variables to restrict by.
        affected = await super().delete(
            "DELETE FROM equipment_stats"
        )
        return affected > 0