from domain import Race, IRepository
from infrastructure import BaseRepository
from typing import List, Optional

class RaceRepository(BaseRepository, IRepository):
    
    # ---------- Schema Setup ----------

    async def init_database(self):
        """
        initalizes the database schema for the actions table. Called automatically on first use. Override in child classes to create tables.
        connection is managed by BaseRepository, so we can use super() to execute our schema setup queries.
        """
        conn = await super().acquire_connection()

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS races (
                race_id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                metadata TEXT,
                FOREIGN KEY(server_id) REFERENCES servers(server_id),
                UNIQUE(name, server_id)
            )
        """)

        await conn.commit()
    
    # ---------- Teardown ----------

    async def drop_table(self):
        """
        Drops the races table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        await super().execute(f"DROP TABLE IF EXISTS races")

    async def clear_all(self) -> bool:
        """
        Clears all data from the races table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        affected = await super().delete(
            "DELETE FROM races"
        )
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "races")
        return affected > 0

    # ---------- Queries ----------

    async def get_by_id(self, race_id: int) -> Optional[Race]:
        row = await super().fetchrow(
            "SELECT * FROM races WHERE race_id = ?",
            race_id
        )
        return Race(data=dict(row)) if row else None

    async def get_all(self, server_id: int) -> List[Race]:
        rows = await super().fetch("SELECT * FROM races WHERE server_id = ?", server_id)
        return [Race(data=dict(row)) for row in rows]
    
    # ---------- Additional Queries ----------

    async def get_by_name(self, name: str, server_id: int) -> Optional[Race]:
        row = await super().fetchrow(
            "SELECT * FROM races WHERE name = ? AND server_id = ?", 
            name, 
            server_id
        )
        return Race(data=dict(row)) if row else None
    
    # ---------- Existence Checks ----------

    async def exists(self, race_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM races WHERE race_id = ?",
            race_id
        )
        return row is not None
    
    # ---------- Additional Existence Checks ----------

    # ---------- Mutations ----------

    async def insert(self, race: Race) -> int:
        return await super().insert(
            "INSERT INTO races (server_id, name, description, metadata) VALUES (?, ?, ?, ?)",
            race.server_id,
            race.name,
            race.description,
            str(race.metadata)
        )
    
    async def update(self, race: Race) -> bool:
        affected = await super().update(
            "UPDATE races SET server_id = ?, name = ?, description = ?, metadata = ? WHERE race_id = ?",
            race.server_id,
            race.name,
            race.description,
            str(race.metadata),
            race.race_id
        )
        return affected > 0

    async def delete(self, race: Race) -> bool:
        affected = await super().delete(
            "DELETE FROM races WHERE race_id = ?",
            race.race_id
        )
        return affected > 0
    
    async def delete_all(self, server_id: int) -> bool:
        # Delete_all and clear_all do the same in this repository since there are no environment variables to restrict by.
        affected = await super().delete(
            "DELETE FROM races WHERE server_id = ?",
            server_id
        )
        return affected > 0