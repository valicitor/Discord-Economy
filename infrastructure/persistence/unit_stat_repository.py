from domain import UnitStat, IRepository
from infrastructure import BaseRepository
from typing import List, Optional

class UnitStatRepository(BaseRepository, IRepository):
    
    # ---------- Schema Setup ----------

    async def init_database(self):
        """
        initalizes the database schema for the actions table. Called automatically on first use. Override in child classes to create tables.
        connection is managed by BaseRepository, so we can use super() to execute our schema setup queries.
        """
        conn = await super().acquire_connection()

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS unit_stats (
                unit_stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                unit_id INTEGER NOT NULL,
                stat_key TEXT NOT NULL,
                stat_value REAL NOT NULL,
                FOREIGN KEY(unit_id) REFERENCES units(unit_id)
            )
        """)

        await conn.commit()
    
    # ---------- Teardown ----------

    async def drop_table(self):
        """
        Drops the unit_stats table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        await super().execute(f"DROP TABLE IF EXISTS unit_stats")

    async def clear_all(self) -> bool:
        """
        Clears all data from the unit_stats table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        affected = await super().delete(
            "DELETE FROM unit_stats"
        )
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "unit_stats")
        return affected > 0

    # ---------- Queries ----------

    async def get_by_id(self, unit_stat_id: int) -> Optional[UnitStat]:
        row = await super().fetchrow(
            "SELECT * FROM unit_stats WHERE unit_stat_id = ?",
            unit_stat_id
        )
        return UnitStat(data=dict(row)) if row else None

    async def get_all(self, unit_id: int|None = None) -> List[UnitStat]:
        if unit_id is not None:
            rows = await super().fetch("SELECT * FROM unit_stats WHERE unit_id = ?", unit_id)
        else:
            rows = await super().fetch("SELECT * FROM unit_stats")
        return [UnitStat(data=dict(row)) for row in rows]
    
    # ---------- Additional Queries ----------

    async def get_by_key(self, stat_key: str, unit_id: int) -> Optional[UnitStat]:
        row = await super().fetchrow(
            "SELECT * FROM unit_stats WHERE stat_key = ? AND unit_id = ?", 
            stat_key, 
            unit_id
        )
        return UnitStat(data=dict(row)) if row else None
    
    # ---------- Existence Checks ----------

    async def exists(self, unit_stat_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM unit_stats WHERE unit_stat_id = ?",
            unit_stat_id
        )
        return row is not None
    
    # ---------- Additional Existence Checks ----------

    # ---------- Mutations ----------

    async def insert(self, unit_stat: UnitStat) -> int:
        return await super().insert(
            "INSERT INTO unit_stats (unit_id, stat_key, stat_value) VALUES (?, ?, ?)",
            unit_stat.unit_id,
            unit_stat.stat_key,
            unit_stat.stat_value
        )
    
    async def update(self, unit_stat: UnitStat) -> bool:
        affected = await super().update(
            "UPDATE unit_stats SET unit_id = ?, stat_key = ?, stat_value = ? WHERE unit_stat_id = ?",
            unit_stat.unit_id,
            unit_stat.stat_key,
            unit_stat.stat_value,
            unit_stat.unit_stat_id
        )
        return affected > 0

    async def delete(self, unit_stat: UnitStat) -> bool:
        affected = await super().delete(
            "DELETE FROM unit_stats WHERE unit_stat_id = ?",
            unit_stat.unit_stat_id
        )
        return affected > 0
    
    async def delete_all(self) -> bool:
        # Delete_all and clear_all do the same in this repository since there are no environment variables to restrict by.
        affected = await super().delete(
            "DELETE FROM unit_stats"
        )
        return affected > 0