from domain import PlayerAction
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class PlayerActionRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    async def init_database(self):
        await self.execute("""
                CREATE TABLE IF NOT EXISTS player_actions (
                    player_action_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    last_used_at DATETIME,
                    FOREIGN KEY(player_id) REFERENCES players(player_id),
                    UNIQUE(player_id, type)
                )
            """)
        await self.execute("PRAGMA journal_mode=WAL;")

    # ---------- Queries ----------

    async def get_by_id(self, player_action_id: int) -> Optional[PlayerAction]:
        row = await self.fetchrow(
            "SELECT * FROM player_actions WHERE player_action_id = ?", (player_action_id,)
        )
        return PlayerAction(data=dict(row)) if row else None

    async def get_by_type(self, action_type: str, player_id: int) -> Optional[PlayerAction]:
        row = await self.fetchrow(
            "SELECT * FROM player_actions WHERE player_id = ? AND type = ?", (player_id, action_type)
        )
        return PlayerAction(data=dict(row)) if row else None

    async def get_all(self) -> List[PlayerAction]:
        rows = await self.fetch("SELECT * FROM player_actions")
        return [PlayerAction(data=dict(row)) for row in rows]
    
    async def get_all_by_player_id(self, player_id: int) -> List[PlayerAction]:
        rows = await self.fetch("SELECT * FROM player_actions WHERE player_id = ?", (player_id,))
        return [PlayerAction(data=dict(row)) for row in rows]

    # ---------- Mutations ----------

    async def add(self, player_action: PlayerAction) -> tuple[bool, int]:
        last_id = await self.insert("""
            INSERT INTO player_actions (
                player_id, type, last_used_at
            )
                VALUES (?, ?, ?)
            """, (
                player_action.player_id,
                player_action.type,
                player_action.last_used_at
            ))

        return (last_id > 0, last_id)

    async def update(self, player_action: PlayerAction) -> bool:
        last_id = await self.update("""
            UPDATE player_actions
            SET player_id = ?, type = ?, last_used_at = ?
            WHERE player_action_id = ?
        """, (
            player_action.player_id,
                player_action.type,
                player_action.last_used_at,
                player_action.player_action_id
            ))

        return last_id > 0

    async def delete(self, player_action: PlayerAction) -> bool:
        last_id = await self.delete(
            "DELETE FROM player_actions WHERE player_action_id = ?",
            (player_action.player_action_id,)
        )
        return last_id > 0
    
    async def delete_all(self, player_id: int) -> bool:
        last_id = await self.delete("DELETE FROM player_actions WHERE player_id = ?", (player_id,))
        return last_id > 0

    async def exists(self, player_action_id: int) -> bool:
        row = await self.fetchrow(
            "SELECT 1 FROM player_actions WHERE player_action_id = ?", (player_action_id,)
        )
        return row is not None