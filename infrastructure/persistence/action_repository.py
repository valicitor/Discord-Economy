from domain import Action
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class ActionRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    def init_database(self):
        with self._lock:
            c = self.cursor()
            c.execute("""
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
            self.execute("PRAGMA journal_mode=WAL;")
            self.commit()

    # ---------- Queries ----------

    def get_by_id(self, action_id: int) -> Optional[Action]:
        with self._lock:
            c = self.cursor()
            c.execute(
                "SELECT * FROM actions WHERE action_id = ?", (action_id,)
            )
            row = c.fetchone()
            return Action(data=dict(row)) if row else None

    def get_all(self) -> List[Action]:
        with self._lock:
            c = self.cursor()
            c.execute("SELECT * FROM actions")
            return [Action(data=dict(row)) for row in c.fetchall()]

    # ---------- Mutations ----------

    def add(self, action: Action) -> tuple[bool, int]:
        with self._lock:
            c = self.cursor()
            c.execute("""
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

            self.commit()
            return (c.rowcount > 0, c.lastrowid)

    def update(self, action: Action) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute("""
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

            self.commit()
            return c.rowcount > 0

    def delete(self, action: Action) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute(
                "DELETE FROM actions WHERE action_id = ?",
                (action.action_id,)
            )

            self.commit()
            return c.rowcount > 0

    def exists(self, action_id: int) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute(
                "SELECT 1 FROM actions WHERE action_id = ?",
                (action_id,)
            )
            return c.fetchone() is not None