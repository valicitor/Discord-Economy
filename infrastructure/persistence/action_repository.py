from domain import Action
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class ActionRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    async def init_database(self):
        await self.execute("""
            CREATE TABLE IF NOT EXISTS actions (
                action_id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id INTEGER,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                cooldown_seconds INTEGER DEFAULT 86400,
                base_reward INTEGER DEFAULT 0,
                risk_rate REAL DEFAULT 0.0,
                fine_amount INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 1.0,
                success_message TEXT DEFAULT "You successfully completed the action!",
                failure_message TEXT DEFAULT "You failed to complete the action.",
                FOREIGN KEY(business_id) REFERENCES businesses(business_id)
            )
        """)
        await self.execute("PRAGMA journal_mode=WAL;")

    # ---------- Queries ----------

    async def get_by_id(self, action_id: int) -> Optional[Action]:
        row = await self.fetchrow(
            "SELECT * FROM actions WHERE action_id = ?", action_id
        )
        return Action(data=dict(row)) if row else None

    async def get_all(self) -> List[Action]:
        rows = await self.fetch("SELECT * FROM actions")
        return [Action(data=dict(row)) for row in rows]

    # ---------- Mutations ----------

    async def add(self, action: Action) -> tuple[bool, int]:
        last_id = await self.insert("""
            INSERT INTO actions (
                business_id, name, type, cooldown_seconds, base_reward, risk_rate, fine_amount, success_rate, success_message, failure_message
            )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                action.business_id,
                action.name,
                action.type,
                action.cooldown_seconds,
                action.base_reward,
                action.risk_rate,
                action.fine_amount,
                action.success_rate,
                action.success_message,
                action.failure_message
            ))

        return (last_id > 0, last_id)

    async def update(self, action: Action) -> bool:
        rowcount = await self.update("""
            UPDATE actions
            SET  business_id = ?, name = ?, type = ?, cooldown_seconds = ?, base_reward = ?, risk_rate = ?, fine_amount = ?, success_rate = ?, success_message = ?, failure_message = ?
            WHERE action_id = ?
        """, (
                action.business_id,
                action.name,
                action.type,
                action.cooldown_seconds,
                action.base_reward,
                action.risk_rate,
                action.fine_amount,
                action.success_rate,
                action.success_message,
                action.failure_message,
                action.action_id
            ))

        return rowcount > 0

    async def delete(self, action: Action) -> bool:
        rowcount = await self.delete(
            "DELETE FROM actions WHERE action_id = ?",
            (action.action_id,)
        )

        return rowcount > 0
    
    async def delete_all(self) -> bool:
        rowcount = await self.delete("DELETE FROM actions")
        return rowcount > 0

    async def exists(self, action_id: int) -> bool:
        row = await self.fetchrow(
            "SELECT 1 FROM actions WHERE action_id = ?",
            (action_id,)
        )
        return row is not None