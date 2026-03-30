from domain import Action
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class ActionRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "dynamic_resources.db")

    def init_database(self):
        with self._lock:
            c = self.conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS actions (
                    action_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    cooldown_seconds INTEGER DEFAULT 86400,
                    base_reward INTEGER DEFAULT 0,
                    reward_currency_id INTEGER,
                    success_rate REAL DEFAULT 1.0,
                    FOREIGN KEY(reward_currency_id) REFERENCES currencies(currency_id)
                )
            """)
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.commit()

    # ---------- Queries ----------

    def get_by_id(self, action_id: int) -> Optional[Action]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT * FROM actions WHERE action_id = ?", (action_id,)
            )
            row = c.fetchone()
            return Action(data=dict(row)) if row else None

    def get_all(self) -> List[Action]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("SELECT * FROM actions")
            return [Action(data=dict(row)) for row in c.fetchall()]

    # ---------- Mutations ----------

    def add(self, action: Action) -> tuple[bool, int]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                INSERT INTO actions (
                    name, cooldown_seconds, base_reward, reward_currency_id, success_rate
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                action.name,
                action.cooldown_seconds,
                action.base_reward,
                action.reward_currency_id,
                action.success_rate
            ))

            self.conn.commit()
            return (c.rowcount > 0, c.lastrowid)

    def update(self, action: Action) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                UPDATE actions
                SET name = ?, cooldown_seconds = ?, base_reward = ?, reward_currency_id = ?, success_rate = ?
                WHERE action_id = ?
            """, (
                action.name,
                action.cooldown_seconds,
                action.base_reward,
                action.reward_currency_id,
                action.success_rate,
                action.action_id
            ))

            self.conn.commit()
            return c.rowcount > 0

    def delete(self, action: Action) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "DELETE FROM actions WHERE action_id = ?",
                (action.action_id,)
            )

            self.conn.commit()
            return c.rowcount > 0

    def exists(self, action_id: int) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT 1 FROM actions WHERE action_id = ?",
                (action_id,)
            )
            return c.fetchone() is not None