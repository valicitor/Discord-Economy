from domain import Server
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class ServerRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "dynamic_resources.db")

    def init_database(self):
        with self._lock:
            c = self.conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS servers (
                    server_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.commit()

    # ---------- Queries ----------

    def get_by_id(self, server_id: int) -> Optional[Server]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT * FROM servers WHERE server_id = ?", (server_id,)
            )
            row = c.fetchone()
            return Server(data=dict(row)) if row else None
    
    def get_by_guild_id(self, guild_id: int) -> Optional[Server]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT * FROM servers WHERE guild_id = ?", (guild_id,)
            )
            row = c.fetchone()
            return Server(data=dict(row)) if row else None

    def get_all(self) -> List[Server]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("SELECT * FROM servers")
            return [Server(data=dict(row)) for row in c.fetchall()]

    # ---------- Mutations ----------

    def add(self, server: Server) -> tuple[bool, int]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                INSERT INTO servers (
                    guild_id, name
                )
                VALUES (?, ?)
            """, (
                server.guild_id,
                server.name
            ))

            self.conn.commit()
            return (c.rowcount > 0, c.lastrowid)

    def update(self, server: Server) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                UPDATE servers
                SET name = ?
                WHERE server_id = ?
            """, (
                server.name,
                server.server_id
            ))

            self.conn.commit()
            return c.rowcount > 0

    def delete(self, server: Server) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "DELETE FROM servers WHERE server_id = ?",
                (server.server_id,)
            )

            self.conn.commit()
            return c.rowcount > 0

    def exists(self, server_id: int) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT 1 FROM servers WHERE server_id = ?",
                (server_id,)
            )
            return c.fetchone() is not None
    
    def exists_by_guild_id(self, guild_id: int) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT 1 FROM servers WHERE guild_id = ?",
                (guild_id,)
            )
            return c.fetchone() is not None