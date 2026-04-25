from domain import Location, IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class LocationRepository(BaseRepository, IRepository):
    
    # ---------- Schema Setup ----------

    async def init_database(self):
        """
        initalizes the database schema for the locations table. Called automatically on first use. Override in child classes to create tables.
        connection is managed by BaseRepository, so we can use super() to execute our schema setup queries.
        """
        conn = await super().acquire_connection()

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS locations (
                location_id INTEGER PRIMARY KEY AUTOINCREMENT,
                poi_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                x REAL NOT NULL,
                y REAL NOT NULL,
                owner_player_id INTEGER,
                FOREIGN KEY(poi_id) REFERENCES points_of_interest(poi_id),
                FOREIGN KEY(owner_player_id) REFERENCES players(player_id)
            )
        """)

        await conn.commit()
    
    # ---------- Teardown ----------

    async def drop_table(self):
        """
        Drops the locations table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        await super().execute(f"DROP TABLE IF EXISTS locations")

    async def clear_all(self) -> bool:
        """
        Clears all data from the locations table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        affected = await super().delete(
            "DELETE FROM locations"
        )
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "locations")
        return affected > 0

    # ---------- Queries ----------

    async def get_by_id(self, location_id: int) -> Optional[Location]:
        row = await super().fetchrow(
            "SELECT * FROM locations WHERE location_id = ?",
            location_id
        )
        return Location(data=dict(row)) if row else None

    async def get_all(self, poi_id: int|None = None) -> List[Location]:
        if poi_id is not None:
            rows = await super().fetch("SELECT * FROM locations WHERE poi_id = ?", poi_id)
        else:
            rows = await super().fetch("SELECT * FROM locations")
        return [Location(data=dict(row)) for row in rows]
    
    # ---------- Additional Queries ----------

    async def get_by_name(self, name: str, server_id: int) -> Optional[Location]:
        row = await super().fetchrow(
            """
            SELECT l.* FROM locations l
            LEFT JOIN points_of_interest p ON l.poi_id = p.poi_id
            WHERE l.name = ? AND p.server_id = ?
            """,
            name, 
            server_id
        )
        return Location(data=dict(row)) if row else None

    # ---------- Existence Checks ----------

    async def exists(self, location_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM locations WHERE location_id = ?",
            location_id
        )
        return row is not None
    
    # ---------- Additional Existence Checks ----------

    async def exists_by_name(self, name: str, server_id: int) -> bool:
        row = await super().fetchrow(
            """
            SELECT 1 FROM locations l
            LEFT JOIN points_of_interest p ON l.poi_id = p.poi_id
            WHERE l.name = ? AND p.server_id = ?
            """,
            name,
            server_id
        )
        return row is not None

    # ---------- Mutations ----------

    async def insert(self, location: Location) -> int:
        return await super().insert(
            "INSERT INTO locations (poi_id, name, type, x, y, owner_player_id) VALUES (?, ?, ?, ?, ?, ?)",
            location.poi_id,
            location.name,
            location.type,
            location.x,
            location.y,
            location.owner_player_id
        )

    async def update(self, location: Location) -> bool:
        affected = await super().update(
            "UPDATE locations SET poi_id = ?, name = ?, type = ?, x = ?, y = ?, owner_player_id = ? WHERE location_id = ?",
            location.poi_id,
            location.name,
            location.type,
            location.x,
            location.y,
            location.owner_player_id,
            location.location_id
        )
        return affected > 0

    async def delete(self, location: Location) -> bool:
        affected = await super().delete(
            "DELETE FROM locations WHERE location_id = ?",
            location.location_id
        )
        return affected > 0
    
    async def delete_all(self) -> bool:
        # Delete_all and clear_all do the same in this repository since there are no environment variables to restrict by.
        affected = await super().delete(
            "DELETE FROM locations",
        )
        return affected > 0