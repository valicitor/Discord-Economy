from domain import UnitStat
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class UnitStatRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    async def init_database(self):
        await self.execute("""
                CREATE TABLE IF NOT EXISTS unit_stats (
                    unit_stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    unit_id INTEGER NOT NULL,
                    stat_key TEXT NOT NULL,
                    stat_value REAL NOT NULL,
                    FOREIGN KEY(unit_id) REFERENCES units(unit_id)
                )
            """)
        await self.execute("PRAGMA journal_mode=WAL;")

    # ---------- Queries ----------

    async def get_by_id(self, unit_stat_id: int) -> Optional[UnitStat]:
        query = "SELECT * FROM unit_stats WHERE unit_stat_id = ?"
        params = (unit_stat_id,)
        row = await self.fetchrow(query, params)
        return UnitStat(data=dict(row)) if row else None
    
    async def get_by_key(self, stat_key: str, unit_id: int) -> Optional[UnitStat]:
        query = "SELECT * FROM unit_stats WHERE stat_key = ? AND unit_id = ?"
        params = (stat_key, unit_id)
        row = await self.fetchrow(query, params)
        return UnitStat(data=dict(row)) if row else None

    async def get_all(self) -> List[UnitStat]:
        query = "SELECT * FROM unit_stats"
        rows = await self.fetch(query)
        return [UnitStat(data=dict(row)) for row in rows]

    # ---------- Mutations ----------

    async def add(self, unit_stat: UnitStat) -> tuple[bool, int]:
        query = """
            INSERT INTO unit_stats (
                unit_id, stat_key, stat_value
            )
            VALUES (?, ?, ?)
        """
        params = (
            unit_stat.unit_id,
            unit_stat.stat_key,
            unit_stat.stat_value
        )
        last_id = await self.insert(query, params)
        return (last_id > 0, last_id)

    async def update(self, unit_stat: UnitStat) -> bool:
        query = """
            UPDATE unit_stats
            SET unit_id = ?, stat_key = ?, stat_value = ?
            WHERE unit_stat_id = ?
        """
        params = (
            unit_stat.unit_id,
            unit_stat.stat_key,
            unit_stat.stat_value,
            unit_stat.unit_stat_id
        )
        last_id = await self.update(query, params)
        return last_id > 0

    async def delete(self, unit_stat: UnitStat) -> bool:
        query = "DELETE FROM unit_stats WHERE unit_stat_id = ?"
        params = (unit_stat.unit_stat_id,)
        last_id = await self.delete(query, params)
        return last_id > 0
    
    async def delete_all(self) -> bool:
        query = "DELETE FROM unit_stats"
        last_id = await self.delete(query)
        return last_id > 0

    async def exists(self, unit_stat_id: int) -> bool:
        query = "SELECT 1 FROM unit_stats WHERE unit_stat_id = ?"
        params = (unit_stat_id,)
        rows = await self.fetch(query, params)
        return len(rows) > 0