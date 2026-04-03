from domain import FactionMember
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class FactionMemberRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    def init_database(self):
        with self._lock:
            c = self.conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS faction_members (
                    member_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    faction_id INTEGER NOT NULL,
                    player_id INTEGER NOT NULL,
                    role TEXT,
                    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(faction_id) REFERENCES factions(faction_id),
                    FOREIGN KEY(player_id) REFERENCES players(player_id)
                )
            """)
            c.execute("CREATE INDEX IF NOT EXISTS idx_faction_members_faction_id ON faction_members(faction_id)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_faction_members_player_id ON faction_members(player_id)")
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.commit()
    
    # ---------- Queries ----------

    def get_by_id(self, member_id: int) -> Optional[FactionMember]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT * FROM faction_members WHERE member_id = ?", (member_id,)
            )
            row = c.fetchone()
            return FactionMember(data=dict(row)) if row else None
        
    def get_by_player_id(self, player_id: int) -> Optional[FactionMember]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("SELECT * FROM faction_members WHERE player_id = ?", (player_id,))
            row = c.fetchone()
            return FactionMember(data=dict(row)) if row else None

    def get_all(self, faction_id: int = None) -> List[FactionMember]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            if faction_id is not None:
                c.execute("SELECT * FROM faction_members WHERE faction_id = ?", (faction_id,))
            else:
                c.execute("SELECT * FROM faction_members")
            return [FactionMember(data=dict(row)) for row in c.fetchall()]

    # ---------- Mutations ----------

    def add(self, faction_member: FactionMember) -> tuple[bool, int]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                INSERT INTO faction_members (
                    faction_id, player_id, role
                )
                VALUES (?, ?, ?)
                ON CONFLICT(member_id) DO NOTHING
            """, (
                faction_member.faction_id,
                faction_member.player_id,
                faction_member.role
            ))

            self.conn.commit()
            return (c.rowcount > 0, c.lastrowid)

    def update(self, faction_member: FactionMember) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                UPDATE faction_members
                SET faction_id = ?, player_id = ?, role = ?
                WHERE member_id = ?
            """, (
                faction_member.faction_id,
                faction_member.player_id,
                faction_member.role,
                faction_member.member_id
            ))

            self.conn.commit()
            return c.rowcount > 0

    def delete(self, faction_member: FactionMember) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "DELETE FROM faction_members WHERE member_id = ?",
                (faction_member.member_id,)
            )

            self.conn.commit()
            return c.rowcount > 0
    
    def delete_by_player_id(self, player_id: int) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "DELETE FROM faction_members WHERE player_id = ?",
                (player_id,)
            )

            self.conn.commit()
            return c.rowcount > 0
    
    def delete_all(self, faction_id: int) -> int:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "DELETE FROM faction_members WHERE faction_id = ?",
                (faction_id,)
            )

            self.conn.commit()
            return c.rowcount

    def exists(self, member_id: int) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT 1 FROM faction_members WHERE member_id = ?", (member_id,)
            )
            return c.fetchone() is not None

    def exists_by_player_id(self, player_id: int) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT 1 FROM faction_members WHERE player_id = ?", (player_id,)
            )
            return c.fetchone() is not None