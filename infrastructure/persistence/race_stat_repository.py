from domain import RaceStat
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class RaceStatRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    async def init_database(self):
        await self.execute("""
                CREATE TABLE IF NOT EXISTS race_stats (
                    race_stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    race_id INTEGER NOT NULL,
                    stat_key TEXT NOT NULL,
                    stat_value TEXT NOT NULL,
                    FOREIGN KEY(race_id) REFERENCES races(race_id)
                )
            """)
        await self.execute("PRAGMA journal_mode=WAL;")

    # ---------- Queries ----------

    async def get_by_id(self, race_stat_id: int) -> Optional[RaceStat]:
        query = "SELECT * FROM race_stats WHERE race_stat_id = ?"
        params = (race_stat_id,)
        row = await self.fetchrow(query, params)
        return RaceStat(data=dict(row)) if row else None
    
    async def get_by_key(self, stat_key: str, race_id: int) -> Optional[RaceStat]:
        query = "SELECT * FROM race_stats WHERE stat_key = ? AND race_id = ?"
        params = (stat_key, race_id)
        row = await self.fetchrow(query, params)
        return RaceStat(data=dict(row)) if row else None

    async def get_all(self, race_id: int|None = None) -> List[RaceStat]:
        if race_id is not None:
            query = "SELECT * FROM race_stats WHERE race_id = ?"
            params = (race_id,)
        else:
            query = "SELECT * FROM race_stats"
            params = ()
        rows = await self.fetch(query, params)
        return [RaceStat(data=dict(row)) for row in rows]

    # ---------- Mutations ----------

    async def add(self, race_stat: RaceStat) -> tuple[bool, int]:
        query = """
            INSERT INTO race_stats (
                race_id, stat_key, stat_value
            )
            VALUES (?, ?, ?)
        """
        params = (
            race_stat.race_id,
            race_stat.stat_key,
            race_stat.stat_value
        )
        last_id = await self.insert(query, params)
        return (last_id > 0, last_id)

    async def update(self, race_stat: RaceStat) -> bool:
        query = """
            UPDATE race_stats
            SET race_id = ?, stat_key = ?, stat_value = ?
            WHERE race_stat_id = ?
        """
        params = (
            race_stat.race_id,
            race_stat.stat_key,
            race_stat.stat_value,
            race_stat.race_stat_id
        )
        last_id = await self.update(query, params)
        return last_id > 0

    async def delete(self, race_stat: RaceStat) -> bool:
        query = "DELETE FROM race_stats WHERE race_stat_id = ?"
        params = (race_stat.race_stat_id,)
        last_id = await self.delete(query, params)
        return last_id > 0
    
    async def delete_all(self) -> bool:
        query = "DELETE FROM race_stats"
        params = ()
        last_id = await self.delete(query, params)
        return last_id > 0

    async def exists(self, race_stat_id: int) -> bool:
        query = "SELECT 1 FROM race_stats WHERE race_stat_id = ?"
        params = (race_stat_id,)
        rows = await self.fetch(query, params)
        return len(rows) > 0