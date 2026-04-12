from domain import FactionMember, IRepository
from infrastructure import BaseRepository
from typing import List, Optional

class FactionMemberRepository(BaseRepository, IRepository):
    
    # ---------- Schema Setup ----------

    async def init_database(self):
        """
        initalizes the database schema for the faction_members table. Called automatically on first use. Override in child classes to create tables.
        connection is managed by BaseRepository, so we can use super() to execute our schema setup queries.
        """
        conn = await super().acquire_connection()

        await conn.execute("""
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
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_faction_members_faction_player_id ON faction_members(faction_id, player_id)")

        await conn.commit()
    
    # ---------- Teardown ----------

    async def drop_table(self):
        """
        Drops the faction_members table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        await super().execute(f"DROP TABLE IF EXISTS faction_members")

    async def clear_all(self) -> bool:
        """
        Clears all data from the faction_members table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        affected = await super().delete(
            "DELETE FROM faction_members"
        )
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "faction_members")
        return affected > 0

    # ---------- Queries ----------

    async def get_by_id(self, member_id: int) -> Optional[FactionMember]:
        row = await super().fetchrow(
            "SELECT * FROM faction_members WHERE member_id = ?",
            member_id
        )
        return FactionMember(data=dict(row)) if row else None

    async def get_all(self, faction_id: int|None = None) -> List[FactionMember]:
        if faction_id is not None:
            rows = await super().fetch("SELECT * FROM faction_members WHERE faction_id = ?", faction_id)
        else:
            rows = await super().fetch("SELECT * FROM faction_members")
        return [FactionMember(data=dict(row)) for row in rows]
    
    # ---------- Additional Queries ----------

    async def get_by_player_id(self, player_id: int) -> Optional[FactionMember]:
        row = await super().fetchrow(
            "SELECT * FROM faction_members WHERE player_id = ?", 
            player_id
        )
        return FactionMember(data=dict(row)) if row else None
    
    # ---------- Existence Checks ----------

    async def exists(self, member_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM faction_members WHERE member_id = ?",
            member_id
        )
        return row is not None
    
    # ---------- Additional Existence Checks ----------

    async def exists_by_player_id(self, player_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM faction_members WHERE player_id = ?", 
            player_id
        )
        return row is not None

    # ---------- Mutations ----------

    async def insert(self, faction_member: FactionMember) -> int:
        return await super().insert(
            "INSERT INTO faction_members (faction_id, player_id, role) VALUES (?, ?, ?)",
            faction_member.faction_id,
            faction_member.player_id,
            faction_member.role
        )
    
    async def update(self, faction_member: FactionMember) -> bool:
        affected = await super().update(
            "UPDATE faction_members SET faction_id = ?, player_id = ?, role = ? WHERE member_id = ?",
            faction_member.faction_id,
            faction_member.player_id,
            faction_member.role,
            faction_member.member_id
        )
        return affected > 0

    async def delete(self, faction_member: FactionMember) -> bool:
        affected = await super().delete(
            "DELETE FROM faction_members WHERE member_id = ?",
            faction_member.member_id
        )
        return affected > 0
    
    async def delete_all(self, faction_id: int) -> bool:
        affected = await super().delete(
            "DELETE FROM faction_members WHERE faction_id = ?",
            faction_id
        )
        return affected > 0
    
    # --------- Additional Mutations ----------

    async def delete_by_player_id(self, player_id: int) -> bool:
        rowcount = await super().delete(
            "DELETE FROM faction_members WHERE player_id = ?",
            player_id
        )
        return rowcount > 0