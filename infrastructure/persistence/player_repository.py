from domain import Player
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class PlayerRepository(IRepository, BaseRepository):
    def __init__(self, db_path: str = None):
        super().__init__(db_path or "player.db")

    def init_database(self):
        with self._lock:
            c = self.conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    discord_id INTEGER UNIQUE NOT NULL,
                    username TEXT NOT NULL,
                    avatar TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            c.execute("CREATE INDEX IF NOT EXISTS idx_players_discord_id ON players(discord_id)")
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.commit()

    # ---------- Queries ----------

    def get_by_id(self, player_id: int) -> Optional[Player]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT * FROM players WHERE player_id = ?", (player_id,)
            )
            row = c.fetchone()
            return Player(data=dict(row)) if row else None
        
    def get_by_discord(self, discord_id: int) -> Optional[Player]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("SELECT * FROM players WHERE discord_id = ?", (discord_id,))
            row = c.fetchone()
            return Player(data=dict(row)) if row else None

    def get_all(self) -> List[Player]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("SELECT * FROM players")
            return [Player(data=dict(row)) for row in c.fetchall()]

    # ---------- Mutations ----------

    def add(self, player: Player) -> tuple[bool, int]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                INSERT INTO players (
                    discord_id, username, avatar
                )
                VALUES (?, ?, ?)
                ON CONFLICT(discord_id) DO NOTHING
            """, (
                player.discord_id,
                player.username,
                player.avatar
            ))

            self.conn.commit()
            return (c.rowcount > 0, c.lastrowid)

    def update(self, player: Player) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                UPDATE players
                SET username = ?, avatar = ?
                WHERE discord_id = ?
            """, (
                player.username,
                player.avatar,
                player.discord_id
            ))

            self.conn.commit()
            return c.rowcount > 0

    def delete(self, player: Player) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "DELETE FROM players WHERE discord_id = ?",
                (player.discord_id,)
            )

            self.conn.commit()
            return c.rowcount > 0

    def exists(self, discord_id: int) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT 1 FROM players WHERE discord_id = ?",
                (discord_id,)
            )
            return c.fetchone() is not None