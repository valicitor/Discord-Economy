from domain import Faction
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class FactionRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    def init_database(self):
        with self._lock:
            c = self.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS factions (
                    faction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_id INTEGER NOT NULL,
                    owner_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    color TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(server_id) REFERENCES servers(server_id),
                    FOREIGN KEY(owner_id) REFERENCES players(player_id),
                    UNIQUE(name, server_id)
                )
            """)
            c.execute("CREATE INDEX IF NOT EXISTS idx_factions_name ON factions(name)")
            self.execute("PRAGMA journal_mode=WAL;")
            self.commit()
    
    # ---------- Queries ----------

    def get_by_id(self, faction_id: int) -> Optional[Faction]:
        with self._lock:
            c = self.cursor()
            c.execute(
                "SELECT * FROM factions WHERE faction_id = ?", (faction_id,)
            )
            row = c.fetchone()
            return Faction(data=dict(row)) if row else None
        
    def get_by_owner_id(self, owner_id: int, server_id: int) -> Optional[Faction]:
        with self._lock:
            c = self.cursor()
            c.execute("SELECT * FROM factions WHERE owner_id = ? AND server_id = ?", (owner_id, server_id))
            row = c.fetchone()
            return Faction(data=dict(row)) if row else None

    def get_all(self, server_id: int = None) -> List[Faction]:
        with self._lock:
            c = self.cursor()
            if server_id is not None:
                c.execute("SELECT * FROM factions WHERE server_id = ?", (server_id,))
            else:
                c.execute("SELECT * FROM factions")
            return [Faction(data=dict(row)) for row in c.fetchall()]

    # ---------- Mutations ----------

    def add(self, faction: Faction) -> tuple[bool, int]:
        with self._lock:
            c = self.cursor()
            c.execute("""
                INSERT INTO factions (
                    server_id, owner_id, name, description, color
                )
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(faction_id) DO NOTHING
            """, (
                faction.server_id,
                faction.owner_id,
                faction.name,
                faction.description,
                faction.color
            ))

            self.commit()
            return (c.rowcount > 0, c.lastrowid)

    def update(self, faction: Faction) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute("""
                UPDATE factions
                SET server_id = ?, owner_id = ?, name = ?, description = ?, color = ?
                WHERE faction_id = ?
            """, (
                faction.server_id,
                faction.owner_id,
                faction.name,
                faction.description,
                faction.color,
                faction.faction_id
            ))

            self.commit()
            return c.rowcount > 0

    def delete(self, faction: Faction) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute(
                "DELETE FROM factions WHERE faction_id = ?",
                (faction.faction_id,)
            )

            self.commit()
            return c.rowcount > 0
    
    def delete_all(self, server_id: int) -> int:
        with self._lock:
            c = self.cursor()
            c.execute(
                "DELETE FROM factions WHERE server_id = ?",
                (server_id,)
            )

            self.commit()
            return c.rowcount

    def exists(self, faction_id: int) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute(
                "SELECT 1 FROM factions WHERE faction_id = ?", (faction_id,)
            )
            return c.fetchone() is not None

    def exists_by_owner_id(self, owner_id: int, server_id: int) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute(
                "SELECT 1 FROM factions WHERE owner_id = ? AND server_id = ?",
                (owner_id, server_id)
            )
            return c.fetchone() is not None