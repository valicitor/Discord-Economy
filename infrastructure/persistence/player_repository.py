from domain import Player
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class PlayerRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(db_path=db_path or "dynamic_resources.db")
        if seeder: 
            seeder(self)

    def init_database(self):
        with self._lock:
            c = self.conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_id INTEGER NOT NULL,
                    discord_id INTEGER UNIQUE NOT NULL,
                    discord_guild_id INTEGER NOT NULL,
                    username TEXT NOT NULL,
                    avatar TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(server_id) REFERENCES servers(server_id)
                )
            """)
            c.execute("CREATE INDEX IF NOT EXISTS idx_players_discord ON players(discord_id, discord_guild_id)")
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
        
    def get_by_discord_id(self, discord_id: int) -> Optional[Player]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("SELECT * FROM players WHERE discord_id = ?", (discord_id,))
            row = c.fetchone()
            return Player(data=dict(row)) if row else None

    def get_all(self, server_id: int = None) -> List[Player]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            if server_id is not None:
                c.execute("SELECT * FROM players WHERE server_id = ?", (server_id,))
            else:
                c.execute("SELECT * FROM players")
            return [Player(data=dict(row)) for row in c.fetchall()]

    def get_all_by_discord_guild(self, discord_guild_id: int) -> List[Player]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("SELECT * FROM players WHERE discord_guild_id = ?", (discord_guild_id,))
            return [Player(data=dict(row)) for row in c.fetchall()]

    # ---------- Mutations ----------

    def add(self, player: Player) -> tuple[bool, int]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                INSERT INTO players (
                    discord_id, discord_guild_id, server_id, username, avatar
                )
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(discord_id) DO NOTHING
            """, (
                player.discord_id,
                player.discord_guild_id,
                player.server_id,
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
                SET username = ?, avatar = ?, discord_guild_id = ?, server_id = ?
                WHERE discord_id = ?
            """, (
                player.username,
                player.avatar,
                player.discord_guild_id,
                player.server_id,
                player.discord_id
            ))

            self.conn.commit()
            return c.rowcount > 0

    def delete(self, player: Player) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "DELETE FROM players WHERE (discord_id = ? AND discord_guild_id = ?) OR player_id = ?",
                (player.discord_id, player.discord_guild_id, player.player_id)
            )

            self.conn.commit()
            return c.rowcount > 0
    
    def delete_all(self, server_id: int) -> int:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "DELETE FROM players WHERE server_id = ?",
                (server_id,)
            )

            self.conn.commit()
            return c.rowcount

    def exists(self, player_id: int) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT 1 FROM players WHERE player_id = ?", (player_id,)
            )
            return c.fetchone() is not None

    def exists_by_discord_id(self, discord_id: int, discord_guild_id: int) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT 1 FROM players WHERE discord_id = ? AND discord_guild_id = ?",
                (discord_id, discord_guild_id)
            )
            return c.fetchone() is not None