from domain import ActionLog, IRepository
from infrastructure import BaseRepository
from typing import List, Optional

class ActionLogRepository(BaseRepository, IRepository):
    
    # ---------- Schema Setup ----------

    async def init_database(self):
        """
        initalizes the database schema for the action_logs table. Called automatically on first use. Override in child classes to create tables.
        connection is managed by BaseRepository, so we can use super() to execute our schema setup queries.
        """
        conn = await super().acquire_connection()

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS action_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                action_id INTEGER NOT NULL,
                target_player_id INTEGER,
                success BOOLEAN,
                reward_amount INTEGER,
                penalty_amount INTEGER,
                result_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(player_id) REFERENCES players(player_id),
                FOREIGN KEY(action_id) REFERENCES actions(action_id)
            )
        """)

        await conn.commit()
    
    # ---------- Teardown ----------

    async def drop_table(self):
        """
        Drops the action_logs table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        await super().execute(f"DROP TABLE IF EXISTS action_logs")

    async def clear_all(self) -> bool:
        """
        Clears all data from the action_logs table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        affected = await super().delete(
            "DELETE FROM action_logs"
        )
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "action_logs")
        return affected > 0

    # ---------- Queries ----------

    async def get_by_id(self, log_id: int) -> Optional[ActionLog]:
        row = await super().fetchrow(
            "SELECT * FROM action_logs WHERE log_id = ?",
            log_id
        )
        return ActionLog(data=dict(row)) if row else None

    async def get_all(self) -> List[ActionLog]:
        rows = await super().fetch("SELECT * FROM action_logs")
        return [ActionLog(data=dict(row)) for row in rows]
    
    # ---------- Additional Queries ----------
    
    # ---------- Existence Checks ----------

    async def exists(self, log_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM action_logs WHERE log_id = ?",
            log_id
        )
        return row is not None
    
    # ---------- Additional Existence Checks ----------

    # ---------- Mutations ----------

    async def insert(self, action_log: ActionLog) -> int:
        return await super().insert(
            "INSERT INTO action_logs (player_id, action_id, target_player_id, success, reward_amount, penalty_amount, result_data) VALUES (?, ?, ?, ?, ?, ?, ?)",
            action_log.player_id,
            action_log.action_id,
            action_log.target_player_id,
            action_log.success,
            action_log.reward_amount,
            action_log.penalty_amount,
            action_log.result_data
        )

    async def update(self, action_log: ActionLog) -> bool:
        affected = await super().update(
            "UPDATE action_logs SET player_id = ?, action_id = ?, target_player_id = ?, success = ?, reward_amount = ?, penalty_amount = ?, result_data = ? WHERE log_id = ?",
            action_log.player_id,
            action_log.action_id,
            action_log.target_player_id,
            action_log.success,
            action_log.reward_amount,
            action_log.penalty_amount,
            action_log.result_data,
            action_log.log_id
        )
        return affected > 0

    async def delete(self, action_log: ActionLog) -> bool:
        affected = await super().delete(
            "DELETE FROM action_logs WHERE log_id = ?",
            action_log.log_id
        )
        return affected > 0
    
    async def delete_all(self, player_id: int) -> bool:
        # Delete_all and clear_all do the same in this repository since there are no environment variables to restrict by.
        affected = await super().delete(
            "DELETE FROM action_logs WHERE player_id = ?",
            player_id
        )
        return affected > 0