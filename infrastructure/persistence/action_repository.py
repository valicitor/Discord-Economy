from domain import Action, IRepository
from infrastructure import BaseRepository
from typing import List, Optional

class ActionRepository(BaseRepository, IRepository):
    
    # ---------- Schema Setup ----------

    async def init_database(self):
        """
        initalizes the database schema for the actions table. Called automatically on first use. Override in child classes to create tables.
        connection is managed by BaseRepository, so we can use super() to execute our schema setup queries.
        """
        conn = await super().acquire_connection()

        await conn.execute("""
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

        await conn.commit()
    
    # ---------- Teardown ----------

    async def drop_table(self):
        """
        Drops the actions table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        await super().execute(f"DROP TABLE IF EXISTS actions")

    async def clear_all(self) -> bool:
        """
        Clears all data from the actions table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        affected = await super().delete(
            "DELETE FROM actions"
        )
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "actions")
        return affected > 0

    # ---------- Queries ----------

    async def get_by_id(self, action_id: int) -> Optional[Action]:
        row = await super().fetchrow(
            "SELECT * FROM actions WHERE action_id = ?",
            action_id
        )
        return Action(data=dict(row)) if row else None

    async def get_all(self) -> List[Action]:
        rows = await super().fetch("SELECT * FROM actions")
        return [Action(data=dict(row)) for row in rows]
    
    # ---------- Additional Queries ----------

    async def get_all_by_business_id(self, action_type: str, business_id: int) -> List[Action]:
        rows = await super().fetch(
            "SELECT * FROM actions WHERE type =? AND business_id = ?",
            action_type,
            business_id
        )
        return [Action(data=dict(row)) for row in rows]
    
    # ---------- Existence Checks ----------

    async def exists(self, action_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM actions WHERE action_id = ?",
            action_id
        )
        return row is not None
    
    # ---------- Additional Existence Checks ----------

    # ---------- Mutations ----------

    async def insert(self, action: Action) -> int:
        return await super().insert(
            "INSERT INTO actions (business_id, name, type, cooldown_seconds, base_reward, risk_rate, fine_amount, success_rate, success_message, failure_message) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
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
        )

    async def update(self, action: Action) -> bool:
        affected = await super().update(
            "UPDATE actions SET business_id = ?, name = ?, type = ?, cooldown_seconds = ?, base_reward = ?, risk_rate = ?, fine_amount = ?, success_rate = ?, success_message = ?, failure_message = ? WHERE action_id = ?",
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
        )
        return affected > 0

    async def delete(self, action: Action) -> bool:
        affected = await super().delete(
            "DELETE FROM actions WHERE action_id = ?",
            action.action_id
        )
        return affected > 0
    
    async def delete_all(self) -> bool:
        affected = await super().delete("DELETE FROM actions")
        return affected > 0