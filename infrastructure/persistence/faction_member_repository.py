from domain import FactionMember
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class FactionMemberRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    async def init_database(self):
        await self.execute("""
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
        await self.execute("CREATE INDEX IF NOT EXISTS idx_faction_members_faction_player_id ON faction_members(faction_id, player_id)")
        await self.execute("PRAGMA journal_mode=WAL;")
    
    # ---------- Queries ----------

    async def get_by_id(self, member_id: int) -> Optional[FactionMember]:
        row = await self.fetchrow(
            "SELECT * FROM faction_members WHERE member_id = ?", (member_id,)
        )
        return FactionMember(data=dict(row)) if row else None
        
    async def get_by_player_id(self, player_id: int) -> Optional[FactionMember]:
        row = await self.fetchrow(
            "SELECT * FROM faction_members WHERE player_id = ?", (player_id,)
        )
        return FactionMember(data=dict(row)) if row else None

    async def get_all(self, faction_id: int = None) -> List[FactionMember]:
        if faction_id is not None:
            rows = await self.fetch("SELECT * FROM faction_members WHERE faction_id = ?", (faction_id,))
        else:
            rows = await self.fetch("SELECT * FROM faction_members")
        return [FactionMember(data=dict(row)) for row in rows]

    # ---------- Mutations ----------

    async def add(self, faction_member: FactionMember) -> tuple[bool, int]:
        last_id = await self.insert("""
            INSERT INTO faction_members (
                faction_id, player_id, role
            )
            VALUES (?, ?, ?)
        """, (
            faction_member.faction_id,
            faction_member.player_id,
            faction_member.role
        ))
        return (last_id > 0, last_id)

    async def update(self, faction_member: FactionMember) -> bool:
        rowcount = await self.update("""
            UPDATE faction_members
            SET faction_id = ?, player_id = ?, role = ?
            WHERE member_id = ?
        """, (
            faction_member.faction_id,
                faction_member.player_id,
                faction_member.role,
                faction_member.member_id
            ))

        return rowcount > 0

    async def delete(self, faction_member: FactionMember) -> bool:
        rowcount = await self.delete(
            "DELETE FROM faction_members WHERE member_id = ?",
            (faction_member.member_id,)
        )
        return rowcount > 0

    async def delete_by_player_id(self, player_id: int) -> bool:
        rowcount = await self.delete(
            "DELETE FROM faction_members WHERE player_id = ?",
            (player_id,)
        )
        return rowcount > 0

    async def delete_all(self, faction_id: int) -> int:
        rowcount = await self.delete(
            "DELETE FROM faction_members WHERE faction_id = ?",
            (faction_id,)
        )
        return rowcount

    async def exists(self, member_id: int) -> bool:
        row = await self.fetchrow(
            "SELECT 1 FROM faction_members WHERE member_id = ?", (member_id,)
        )
        return row is not None

    async def exists_by_player_id(self, player_id: int) -> bool:
        row = await self.fetchrow(
            "SELECT 1 FROM faction_members WHERE player_id = ?", (player_id,)
        )
        return row is not None