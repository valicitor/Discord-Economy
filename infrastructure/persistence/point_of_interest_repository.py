from domain import PointOfInterest
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class PointOfInterestRepository(BaseRepository, IRepository):
    
    # ---------- Schema Setup ----------

    async def init_database(self):
        """
        initalizes the database schema for the points_of_interest table. Called automatically on first use. Override in child classes to create tables.
        connection is managed by BaseRepository, so we can use super() to execute our schema setup queries.
        """
        conn = await super().acquire_connection()

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS points_of_interest (
                poi_id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                icon TEXT NOT NULL,
                size INTEGER NOT NULL,
                FOREIGN KEY(server_id) REFERENCES servers(server_id)
            )
        """)

        await conn.commit()
    
    # ---------- Teardown ----------

    async def drop_table(self):
        """
        Drops the points_of_interest table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        await super().execute(f"DROP TABLE IF EXISTS points_of_interest")

    async def clear_all(self) -> bool:
        """
        Clears all data from the points_of_interest table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        affected = await super().delete(
            "DELETE FROM points_of_interest"
        )
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "points_of_interest")
        return affected > 0

    # ---------- Queries ----------

    async def get_by_id(self, poi_id: int) -> Optional[PointOfInterest]:
        row = await super().fetchrow(
            "SELECT * FROM points_of_interest WHERE poi_id = ?",
            poi_id
        )
        return PointOfInterest(data=dict(row)) if row else None

    async def get_all(self, server_id: int) -> List[PointOfInterest]:
        rows = await super().fetch("SELECT * FROM points_of_interest WHERE server_id = ?", server_id)
        return [PointOfInterest(data=dict(row)) for row in rows]
    
    # ---------- Additional Queries ----------
    
    async def get_by_name(self, name: str, server_id: int) -> Optional[PointOfInterest]:
        row = await super().fetchrow(
            "SELECT * FROM points_of_interest WHERE name = ? AND server_id = ?", 
            name, 
            server_id
        )
        return PointOfInterest(data=dict(row)) if row else None

    # ---------- Existence Checks ----------

    async def exists(self, poi_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM points_of_interest WHERE poi_id = ?",
            poi_id
        )
        return row is not None
    
    # ---------- Additional Existence Checks ----------

    # ---------- Mutations ----------

    async def insert(self, poi: PointOfInterest) -> int:
        return await super().insert(
            "INSERT INTO points_of_interest (server_id, name, icon, size) VALUES (?, ?, ?, ?)",
            poi.server_id,
            poi.name,
            poi.icon,
            poi.size
        )

    async def update(self, poi: PointOfInterest) -> bool:
        affected = await super().update(
            "UPDATE points_of_interest SET server_id = ?, name = ?, icon = ?, size = ? WHERE poi_id = ?",
            poi.server_id,
            poi.name,
            poi.icon,
            poi.size,
            poi.poi_id
        )
        return affected > 0

    async def delete(self, poi: PointOfInterest) -> bool:
        affected = await super().delete(
            "DELETE FROM points_of_interest WHERE poi_id = ?",
            poi.poi_id
        )
        return affected > 0
    
    async def delete_all(self, server_id: int) -> bool:
        # Delete_all and clear_all do the same in this repository since there are no environment variables to restrict by.
        affected = await super().delete(
            "DELETE FROM points_of_interest WHERE server_id = ?",
            server_id
        )
        return affected > 0