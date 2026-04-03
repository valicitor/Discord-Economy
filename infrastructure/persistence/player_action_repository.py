from domain import PlayerAction
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class PlayerActionRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    def init_database(self):
        with self._lock:
            c = self.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS player_actions (
                    player_action_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    last_used_at DATETIME,
                    FOREIGN KEY(player_id) REFERENCES players(player_id),
                    UNIQUE(player_id, type)
                )
            """)
            self.execute("PRAGMA journal_mode=WAL;")
            self.commit()

    # ---------- Queries ----------

    def get_by_id(self, player_action_id: int) -> Optional[PlayerAction]:
        with self._lock:
            c = self.cursor()
            c.execute(
                "SELECT * FROM player_actions WHERE player_action_id = ?", (player_action_id,)
            )
            row = c.fetchone()
            return PlayerAction(data=dict(row)) if row else None

    def get_by_type(self, action_type: str, player_id: int) -> Optional[PlayerAction]:
        with self._lock:
            c = self.cursor()
            c.execute(
                "SELECT * FROM player_actions WHERE player_id = ? AND type = ?", (player_id, action_type)
            )
            row = c.fetchone()
            return PlayerAction(data=dict(row)) if row else None

    def get_all(self) -> List[PlayerAction]:
        with self._lock:
            c = self.cursor()
            c.execute("SELECT * FROM player_actions")
            return [PlayerAction(data=dict(row)) for row in c.fetchall()]
    
    def get_all_by_player_id(self, player_id: int) -> List[PlayerAction]:
        with self._lock:
            c = self.cursor()
            c.execute("SELECT * FROM player_actions WHERE player_id = ?", (player_id,))
            return [PlayerAction(data=dict(row)) for row in c.fetchall()]

    # ---------- Mutations ----------

    def add(self, player_action: PlayerAction) -> tuple[bool, int]:
        with self._lock:
            c = self.cursor()
            c.execute("""
                INSERT INTO player_actions (
                    player_id, type, last_used_at
                )
                VALUES (?, ?, ?)
            """, (
                player_action.player_id,
                player_action.type,
                player_action.last_used_at
            ))

            self.commit()
            return (c.rowcount > 0, c.lastrowid)

    def update(self, player_action: PlayerAction) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute("""
                UPDATE player_actions
                SET player_id = ?, type = ?, last_used_at = ?
                WHERE player_action_id = ?
            """, (
                player_action.player_id,
                player_action.type,
                player_action.last_used_at,
                player_action.player_action_id
            ))

            self.commit()
            return c.rowcount > 0

    def delete(self, player_action: PlayerAction) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute(
                "DELETE FROM player_actions WHERE player_action_id = ?",
                (player_action.player_action_id,)
            )

            self.commit()
            return c.rowcount > 0
    
    def delete_all(self, player_id: int) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute("DELETE FROM player_actions WHERE player_id = ?", (player_id,))
            self.commit()
            return c.rowcount > 0

    def exists(self, player_action_id: int) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute(
                "SELECT 1 FROM player_actions WHERE player_action_id = ?",
                (player_action_id,)
            )
            return c.fetchone() is not None