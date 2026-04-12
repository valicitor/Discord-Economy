from domain import RaceStat, IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class RaceStatRepository(BaseRepository, IRepository):
    
    # ---------- Schema Setup ----------

    async def init_database(self):
        """
        initalizes the database schema for the actions table. Called automatically on first use. Override in child classes to create tables.
        connection is managed by BaseRepository, so we can use super() to execute our schema setup queries.
        """
        conn = await super().acquire_connection()

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS race_stats (
                race_stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                race_id INTEGER NOT NULL,
                stat_key TEXT NOT NULL,
                stat_value TEXT NOT NULL,
                FOREIGN KEY(race_id) REFERENCES races(race_id)
            )
        """)

        await conn.commit()
    
    # ---------- Teardown ----------

    async def drop_table(self):
        """
        Drops the race_stats table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        await super().execute(f"DROP TABLE IF EXISTS race_stats")

    async def clear_all(self) -> bool:
        """
        Clears all data from the race_stats table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        affected = await super().delete(
            "DELETE FROM race_stats"
        )
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "race_stats")
        return affected > 0

    # ---------- Queries ----------

    async def get_by_id(self, race_stat_id: int) -> Optional[RaceStat]:
        row = await super().fetchrow(
            "SELECT * FROM race_stats WHERE race_stat_id = ?",
            race_stat_id
        )
        return RaceStat(data=dict(row)) if row else None

    async def get_all(self, race_id: int|None = None) -> List[RaceStat]:
        if race_id is not None:
            rows = await super().fetch("SELECT * FROM race_stats WHERE race_id = ?", race_id)
        else:
            rows = await super().fetch("SELECT * FROM race_stats")
        return [RaceStat(data=dict(row)) for row in rows]
    
    # ---------- Additional Queries ----------

    async def get_by_key(self, stat_key: str, race_id: int) -> Optional[RaceStat]:
        row = await super().fetchrow(
            "SELECT * FROM race_stats WHERE stat_key = ? AND race_id = ?", 
            stat_key, 
            race_id
        )
        return RaceStat(data=dict(row)) if row else None
    
    # ---------- Existence Checks ----------

    async def exists(self, race_stat_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM race_stats WHERE race_stat_id = ?",
            race_stat_id
        )
        return row is not None
    
    # ---------- Additional Existence Checks ----------

    # ---------- Mutations ----------

    async def insert(self, race_stat: RaceStat) -> int:
        return await super().insert(
            "INSERT INTO race_stats (race_id, stat_key, stat_value) VALUES (?, ?, ?)",
            race_stat.race_id,
            race_stat.stat_key,
            race_stat.stat_value
        )
    
    async def update(self, race_stat: RaceStat) -> bool:
        affected = await super().update(
            "UPDATE race_stats SET race_id = ?, stat_key = ?, stat_value = ? WHERE race_stat_id = ?",
            race_stat.race_id,
            race_stat.stat_key,
            race_stat.stat_value,
            race_stat.race_stat_id
        )
        return affected > 0

    async def delete(self, race_stat: RaceStat) -> bool:
        affected = await super().delete(
            "DELETE FROM race_stats WHERE race_stat_id = ?",
            race_stat.race_stat_id
        )
        return affected > 0
    
    async def delete_all(self) -> bool:
        # Delete_all and clear_all do the same in this repository since there are no environment variables to restrict by.
        affected = await super().delete(
            "DELETE FROM race_stats"
        )
        return affected > 0