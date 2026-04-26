import json

from domain import PlayerUnit, IRepository
from infrastructure import BaseRepository
from typing import List, Optional

class PlayerUnitRepository(BaseRepository, IRepository):
    
    # ---------- Schema Setup ----------

    async def init_database(self):
        """
        initalizes the database schema for the player_units table. Called automatically on first use. Override in child classes to create tables.
        connection is managed by BaseRepository, so we can use super() to execute our schema setup queries.
        """
        conn = await super().acquire_connection()

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS player_units (
                unit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                metadata TEXT,
                FOREIGN KEY(player_id) REFERENCES players(player_id),
                UNIQUE(name, player_id)
            )
        """)

        await conn.commit()
    
    # ---------- Teardown ----------

    async def drop_table(self):
        """
        Drops the units table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        await super().execute(f"DROP TABLE IF EXISTS player_units")

    async def clear_all(self) -> bool:
        """
        Clears all data from the units table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        affected = await super().delete(
            "DELETE FROM player_units"
        )
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "player_units")
        return affected > 0

    # ---------- Queries ----------

    async def get_by_id(self, unit_id: int) -> Optional[PlayerUnit]:
        row = await super().fetchrow(
            "SELECT * FROM player_units WHERE unit_id = ?",
            unit_id
        )
        return PlayerUnit(data=dict(row)) if row else None

    async def get_all(self) -> List[PlayerUnit]:
        rows = await super().fetch("SELECT * FROM player_units")
        return [PlayerUnit(data=dict(row)) for row in rows]
    
    # ---------- Additional Queries ----------
    
    async def get_by_name(self, name: str, player_id: int) -> Optional[PlayerUnit]:
        row = await super().fetchrow(
            "SELECT * FROM player_units WHERE name = ? AND player_id = ?",
            name,
            player_id
        )
        return PlayerUnit(data=dict(row)) if row else None
    
    async def get_all_by_player_id(self, player_id: int) -> List[PlayerUnit]:
        rows = await super().fetch("SELECT * FROM player_units WHERE player_id = ?", player_id)
        return [PlayerUnit(data=dict(row)) for row in rows]

    # ---------- Existence Checks ----------

    async def exists(self, unit_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM player_units WHERE unit_id = ?",
            unit_id
        )
        return row is not None
    
    # ---------- Additional Existence Checks ----------

    async def exists_by_name_player_id(self, name: str, player_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM player_units WHERE name = ? AND player_id = ?",
            name,
            player_id
        )
        return row is not None

    # ---------- Mutations ----------

    async def insert(self, unit: PlayerUnit) -> int:
        return await super().insert(
            "INSERT INTO player_units (player_id, name, quantity, metadata) VALUES (?, ?, ?, ?)",
            unit.player_id,
            unit.name,
            unit.quantity,
            json.dumps(unit.metadata)
        )

    async def update(self, unit: PlayerUnit) -> bool:
        affected = await super().update(
            "UPDATE player_units SET player_id = ?, name = ?, quantity = ?, metadata = ? WHERE unit_id = ?",
            unit.player_id,
            unit.name,
            unit.quantity,
            json.dumps(unit.metadata),
            unit.unit_id
        )
        return affected > 0

    async def delete(self, unit: PlayerUnit) -> bool:
        affected = await super().delete(
            "DELETE FROM player_units WHERE unit_id = ?",
            unit.unit_id
        )
        return affected > 0
    
    async def delete_all(self, unit_id: int) -> bool:
        # Delete_all and clear_all do the same in this repository since there are no environment variables to restrict by.
        affected = await super().delete(
            "DELETE FROM player_units WHERE unit_id = ?",
            unit_id
        )
        return affected > 0