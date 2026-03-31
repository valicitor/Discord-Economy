from domain import PlayerAction
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class PlayerActionRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(db_path=db_path or "dynamic_resources.db")
        if seeder: 
            seeder(self)

    def init_database(self):
        with self._lock:
            c = self.conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS player_actions (
                    player_action_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER NOT NULL,
                    action_id INTEGER NOT NULL,
                    last_used_at DATETIME,
                    FOREIGN KEY(player_id) REFERENCES players(player_id),
                    FOREIGN KEY(action_id) REFERENCES actions(action_id)
                )
            """)
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.commit()

    # ---------- Queries ----------

    def get_by_id(self, player_action_id: int) -> Optional[PlayerAction]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT * FROM player_actions WHERE player_action_id = ?", (player_action_id,)
            )
            row = c.fetchone()
            return PlayerAction(data=dict(row)) if row else None

    def get_all(self) -> List[PlayerAction]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("SELECT * FROM player_actions")
            return [PlayerAction(data=dict(row)) for row in c.fetchall()]

    # ---------- Mutations ----------

    def add(self, player_action: PlayerAction) -> tuple[bool, int]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                INSERT INTO player_actions (
                    player_id, action_id, last_used_at
                )
                VALUES (?, ?, ?)
            """, (
                player_action.player_id,
                player_action.action_id,
                player_action.last_used_at
            ))

            self.conn.commit()
            return (c.rowcount > 0, c.lastrowid)

    def update(self, player_action: PlayerAction) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                UPDATE player_actions
                SET player_id = ?, action_id = ?, last_used_at = ?
                WHERE player_action_id = ?
            """, (
                player_action.player_id,
                player_action.action_id,
                player_action.last_used_at,
                player_action.player_action_id
            ))

            self.conn.commit()
            return c.rowcount > 0

    def delete(self, player_action: PlayerAction) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "DELETE FROM player_actions WHERE player_action_id = ?",
                (player_action.player_action_id,)
            )

            self.conn.commit()
            return c.rowcount > 0

    def exists(self, player_action_id: int) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT 1 FROM player_actions WHERE player_action_id = ?",
                (player_action_id,)
            )
            return c.fetchone() is not None