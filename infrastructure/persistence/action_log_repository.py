from domain import ActionLog
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class ActionLogRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")        

    async def init_database(self):
        await self.execute("""
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
        await self.execute("PRAGMA journal_mode=WAL;")

    # ---------- Queries ----------

    async def get_by_id(self, log_id: int) -> Optional[ActionLog]:
        row = await self.fetchrow(
            "SELECT * FROM action_logs WHERE log_id = ?", log_id
        )
        return ActionLog(data=dict(row)) if row else None

    async def get_all(self) -> List[ActionLog]:
        rows = await self.fetch("SELECT * FROM action_logs")
        return [ActionLog(data=dict(row)) for row in rows]

    # ---------- Mutations ----------

    async def add(self, action_log: ActionLog) -> tuple[bool, int]:
        last_id = await self.insert("""
            INSERT INTO action_logs (
                player_id, action_id, target_player_id, success, reward_amount, penalty_amount, result_data
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            action_log.player_id,
            action_log.action_id,
            action_log.target_player_id,
            action_log.success,
            action_log.reward_amount,
            action_log.penalty_amount,
            action_log.result_data
        ))

        return (last_id > 0, last_id)

    async def update(self, action_log: ActionLog) -> bool:
        rowcount = await self.update("""
            UPDATE action_logs
            SET player_id = ?, action_id = ?, target_player_id = ?, success = ?, reward_amount = ?, penalty_amount = ?, result_data = ?
            WHERE log_id = ?
        """, (
            action_log.player_id,
            action_log.action_id,
            action_log.target_player_id,
            action_log.success,
            action_log.reward_amount,
            action_log.penalty_amount,
            action_log.result_data,
            action_log.log_id
        ))

        return rowcount > 0

    async def delete(self, action_log: ActionLog) -> bool:
        rowcount = await self.delete(
            "DELETE FROM action_logs WHERE log_id = ?",
            (action_log.log_id,)
        )

        return rowcount > 0

    async def exists(self, log_id: int) -> bool:
        row = await self.fetchrow(
            "SELECT 1 FROM action_logs WHERE log_id = ?", log_id
        )
        return row is not None