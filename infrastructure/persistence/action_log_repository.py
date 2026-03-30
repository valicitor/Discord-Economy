from domain import ActionLog
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class ActionLogRepository(IRepository, BaseRepository):
    def __init__(self, db_path: str = None):
        super().__init__(db_path or "action_log.db")

    def init_database(self):
        with self._lock:
            c = self.conn.cursor()
            c.execute("""
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
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.commit()

    # ---------- Queries ----------

    def get_by_id(self, log_id: int) -> Optional[ActionLog]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT * FROM action_logs WHERE log_id = ?", (log_id,)
            )
            row = c.fetchone()
            return ActionLog(data=dict(row)) if row else None

    def get_all(self) -> List[ActionLog]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("SELECT * FROM action_logs")
            return [ActionLog(data=dict(row)) for row in c.fetchall()]

    # ---------- Mutations ----------

    def add(self, action_log: ActionLog) -> tuple[bool, int]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
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

            self.conn.commit()
            return (c.rowcount > 0, c.lastrowid)

    def update(self, action_log: ActionLog) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
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

            self.conn.commit()
            return c.rowcount > 0

    def delete(self, action_log: ActionLog) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "DELETE FROM action_logs WHERE log_id = ?",
                (action_log.log_id,)
            )

            self.conn.commit()
            return c.rowcount > 0

    def exists(self, log_id: int) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT 1 FROM action_logs WHERE log_id = ?",
                (log_id,)
            )
            return c.fetchone() is not None