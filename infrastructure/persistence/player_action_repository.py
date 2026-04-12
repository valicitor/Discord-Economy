from domain import PlayerAction, IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class PlayerActionRepository(BaseRepository, IRepository):
    
    # ---------- Schema Setup ----------

    async def init_database(self):
        """
        initalizes the database schema for the player_actions table. Called automatically on first use. Override in child classes to create tables.
        connection is managed by BaseRepository, so we can use super() to execute our schema setup queries.
        """
        conn = await super().acquire_connection()

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS player_actions (
                player_action_id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                last_used_at DATETIME,
                FOREIGN KEY(player_id) REFERENCES players(player_id),
                UNIQUE(player_id, type)
            )
        """)

        await conn.commit()
    
    # ---------- Teardown ----------

    async def drop_table(self):
        """
        Drops the player_actions table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        await super().execute(f"DROP TABLE IF EXISTS player_actions")

    async def clear_all(self) -> bool:
        """
        Clears all data from the player_actions table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        affected = await super().delete(
            "DELETE FROM player_actions"
        )
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "player_actions")
        return affected > 0

    # ---------- Queries ----------

    async def get_by_id(self, player_action_id: int) -> Optional[PlayerAction]:
        row = await super().fetchrow(
            "SELECT * FROM player_actions WHERE player_action_id = ?",
            player_action_id
        )
        return PlayerAction(data=dict(row)) if row else None

    async def get_all(self) -> List[PlayerAction]:
        rows = await super().fetch("SELECT * FROM player_actions")
        return [PlayerAction(data=dict(row)) for row in rows]
    
    # ---------- Additional Queries ----------

    async def get_by_type(self, action_type: str, player_id: int) -> Optional[PlayerAction]:
        row = await super().fetchrow(
            "SELECT * FROM player_actions WHERE player_id = ? AND type = ?", 
            player_id, 
            action_type
        )
        return PlayerAction(data=dict(row)) if row else None
    
    async def get_all_by_player_id(self, player_id: int) -> List[PlayerAction]:
        rows = await super().fetch("SELECT * FROM player_actions WHERE player_id = ?", player_id)
        return [PlayerAction(data=dict(row)) for row in rows]
    
    # ---------- Existence Checks ----------

    async def exists(self, player_action_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM player_actions WHERE player_action_id = ?",
            player_action_id
        )
        return row is not None
    
    # ---------- Additional Existence Checks ----------

    # ---------- Mutations ----------

    async def insert(self, player_action: PlayerAction) -> int:
        return await super().insert(
            "INSERT INTO player_actions (player_id, type, last_used_at) VALUES (?, ?, ?)",
            player_action.player_id,
            player_action.type,
            player_action.last_used_at
        )
    
    async def update(self, player_action: PlayerAction) -> bool:
        affected = await super().update(
            "UPDATE player_actions SET player_id = ?, type = ?, last_used_at = ? WHERE player_action_id = ?",
            player_action.player_id,
            player_action.type,
            player_action.last_used_at,
            player_action.player_action_id
        )
        return affected > 0

    async def delete(self, player_action: PlayerAction) -> bool:
        affected = await super().delete(
            "DELETE FROM player_actions WHERE player_action_id = ?",
            player_action.player_action_id
        )
        return affected > 0
    
    async def delete_all(self, player_id: int) -> bool:
        # Delete_all and clear_all do the same in this repository since there are no environment variables to restrict by.
        affected = await super().delete(
            "DELETE FROM player_actions WHERE player_id = ?",
            player_id
        )
        return affected > 0