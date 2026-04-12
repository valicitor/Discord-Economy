from domain import UnitGarrison, IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class UnitGarrisonRepository(BaseRepository, IRepository):
    
    # ---------- Schema Setup ----------

    async def init_database(self):
        """
        initalizes the database schema for the unit_garrisons table. Called automatically on first use. Override in child classes to create tables.
        connection is managed by BaseRepository, so we can use super() to execute our schema setup queries.
        """
        conn = await super().acquire_connection()

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS unit_garrisons (
                garrison_id INTEGER PRIMARY KEY AUTOINCREMENT,
                unit_id INTEGER NOT NULL,
                poi_id INTEGER NOT NULL,
                assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(unit_id) REFERENCES units(unit_id),
                FOREIGN KEY(poi_id) REFERENCES points_of_interest(poi_id)
            )
        """)

        await conn.commit()
    
    # ---------- Teardown ----------

    async def drop_table(self):
        """
        Drops the unit_garrisons table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        await super().execute(f"DROP TABLE IF EXISTS unit_garrisons")

    async def clear_all(self) -> bool:
        """
        Clears all data from the unit_garrisons table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        affected = await super().delete(
            "DELETE FROM unit_garrisons"
        )
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "unit_garrisons")
        return affected > 0

    # ---------- Queries ----------

    async def get_by_id(self, garrison_id: int) -> Optional[UnitGarrison]:
        row = await super().fetchrow(
            "SELECT * FROM unit_garrisons WHERE garrison_id = ?",
            garrison_id
        )
        return UnitGarrison(data=dict(row)) if row else None

    async def get_all(self) -> List[UnitGarrison]:
        rows = await super().fetch("SELECT * FROM unit_garrisons")
        return [UnitGarrison(data=dict(row)) for row in rows]
    
    # ---------- Additional Queries ----------
    
    # ---------- Existence Checks ----------

    async def exists(self, garrison_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM unit_garrisons WHERE garrison_id = ?",
            garrison_id
        )
        return row is not None
    
    # ---------- Additional Existence Checks ----------

    # ---------- Mutations ----------

    async def insert(self, garrison: UnitGarrison) -> int:
        return await super().insert(
            "INSERT INTO unit_garrisons (unit_id, poi_id, assigned_at) VALUES (?, ?, ?)",
            garrison.unit_id,
            garrison.poi_id,
            garrison.assigned_at
        )

    async def update(self, garrison: UnitGarrison) -> bool:
        affected = await super().update(
            "UPDATE unit_garrisons SET unit_id = ?, poi_id = ?, assigned_at = ? WHERE garrison_id = ?",
            garrison.unit_id,
            garrison.poi_id,
            garrison.assigned_at,
            garrison.garrison_id
        )
        return affected > 0

    async def delete(self, garrison: UnitGarrison) -> bool:
        affected = await super().delete(
            "DELETE FROM unit_garrisons WHERE garrison_id = ?",
            garrison.garrison_id
        )
        return affected > 0
    
    async def delete_all(self, unit_id: int) -> bool:
        # Delete_all and clear_all do the same in this repository since there are no environment variables to restrict by.
        affected = await super().delete(
            "DELETE FROM unit_garrisons WHERE unit_id = ?",
            unit_id
        )
        return affected > 0