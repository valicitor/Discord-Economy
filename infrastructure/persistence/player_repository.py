from domain import Player
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class PlayerRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    async def init_database(self):
        await self.execute("""
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
        await self.execute("CREATE INDEX IF NOT EXISTS idx_players_discord ON players(discord_id, discord_guild_id)")
        await self.execute("PRAGMA journal_mode=WAL;")

    # ---------- Queries ----------

    async def get_by_id(self, player_id: int) -> Optional[Player]:
        query = f"""
            SELECT 
                p.*,
        """
        query += self._get_sort_column("Total")
        query += f"""
            FROM players p
            LEFT JOIN player_balances pb 
                ON pb.player_id = p.player_id
            LEFT JOIN bank_accounts ba
                ON ba.player_id = p.player_id
            WHERE p.player_id = ?
            GROUP BY p.player_id
        """

        row = await self.fetchrow(query, (player_id,))
        return Player(data=dict(row)) if row else None
    
        
    async def get_by_discord_id(self, discord_id: int) -> Optional[Player]:
        query = f"""
            SELECT 
                p.*,
        """
        query += self._get_sort_column("Total")
        query += f"""
            FROM players p
            LEFT JOIN player_balances pb 
                ON pb.player_id = p.player_id
            LEFT JOIN bank_accounts ba
                ON ba.player_id = p.player_id
            WHERE p.discord_id = ?
            GROUP BY p.player_id
        """
        
        row = await self.fetchrow(query, (discord_id,))
        return Player(data=dict(row)) if row else None

    async def get_all(self, server_id: int = None) -> List[Player]:
        query = f"""
            SELECT 
                p.*,
        """
        query += self._get_sort_column("Total")
        query += f"""
            FROM players p
            LEFT JOIN player_balances pb 
                ON pb.player_id = p.player_id
            LEFT JOIN bank_accounts ba
                ON ba.player_id = p.player_id
        """
        params = []
        if server_id is not None:
            query += f" WHERE p.server_id = ?"
            params.append(server_id)
        query += " GROUP BY p.player_id"

        params = tuple(params)
        rows = await self.fetch(query, params)
        return [Player(data=dict(row)) for row in rows]
    

    async def get_all_by_discord_guild(self, discord_guild_id: int) -> List[Player]:
        query = f"""
            SELECT 
                p.*,
        """
        query += self._get_sort_column("Total")
        query += f"""
            FROM players p
            LEFT JOIN player_balances pb 
                ON pb.player_id = p.player_id
            LEFT JOIN bank_accounts ba
                ON ba.player_id = p.player_id
            WHERE p.discord_guild_id = ?
            GROUP BY p.player_id
        """
        rows = await self.fetch(query, (discord_guild_id,))
        return [Player(data=dict(row)) for row in rows]

    # ---------- Mutations ----------

    async def add(self, player: Player) -> tuple[bool, int]:
        last_id = await self.insert("""
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
        
        return (last_id > 0, last_id)

    async def update(self, player: Player) -> bool:
        last_id = await self.update("""
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
        return last_id > 0

    async def delete(self, player: Player) -> bool:
        last_id = await self.delete("""
                DELETE FROM players WHERE (discord_id = ? AND discord_guild_id = ?) OR player_id = ?
            """, (
                player.discord_id,
                player.discord_guild_id,
                player.player_id
            ))
        return last_id > 0
    
    async def delete_all(self, server_id: int) -> int:
        last_id = await self.delete(
            "DELETE FROM players WHERE server_id = ?",
            (server_id,)
        )
        return last_id

    async def exists(self, player_id: int) -> bool:
        query = "SELECT 1 FROM players WHERE player_id = ?"
        params = (player_id,)
        rows = await self.fetch(query, params)
        return len(rows) > 0

    async def exists_by_discord_id(self, discord_id: int, discord_guild_id: int) -> bool:
        query = "SELECT 1 FROM players WHERE discord_id = ? AND discord_guild_id = ?"
        params = (discord_id, discord_guild_id)
        rows = await self.fetch(query, params)
        return len(rows) > 0
    
    # ---------- Custom Methods ----------

    async def get_count(self, server_id: int) -> int:
        query = "SELECT COUNT(*) as count FROM players WHERE server_id = ?"
        params = (server_id,)
        rows = await self.fetch(query, params)
        return rows[0]["count"] if rows else 0

    def _get_sort_column(self, sort_by: str) -> str:
        mapping = {
            "Cash": "RANK() OVER (ORDER BY SUM(pb.balance) DESC) AS rank",
            "Bank": "RANK() OVER (ORDER BY SUM(ba.balance) DESC) AS rank",
            "Total": "RANK() OVER (ORDER BY (SUM(pb.balance) + SUM(ba.balance)) DESC) AS rank"
        }

        if sort_by not in mapping:
            raise ValueError(f"Invalid sort_by value: {sort_by}")

        return mapping[sort_by]

    async def get_leaderboard(self, server_id: int, page: int, sort_by: str = "Total") -> List[Player]:
        query = f"""
            SELECT 
                p.*,
        """
        query += self._get_sort_column(sort_by)
        query += f"""
            FROM players p
            LEFT JOIN player_balances pb 
                ON pb.player_id = p.player_id
            LEFT JOIN bank_accounts ba
                ON ba.player_id = p.player_id
            WHERE p.server_id = ?
            GROUP BY p.player_id
            ORDER BY rank ASC
        """

        params = [server_id]

        if page is not None:
            offset = (page - 1) * 10
            query += " LIMIT 10 OFFSET ?"
            params.append(offset)

        rows = await self.fetch(query, params)
        return [Player(data=dict(row)) for row in rows]