from domain import Player, IRepository
from infrastructure import BaseRepository
from typing import List, Optional

class PlayerRepository(BaseRepository, IRepository):
    
    # ---------- Schema Setup ----------

    async def init_database(self):
        """
        initalizes the database schema for the server_settings table. Called automatically on first use. Override in child classes to create tables.
        connection is managed by BaseRepository, so we can use super() to execute our schema setup queries.
        """
        conn = await super().acquire_connection()

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS players (
                player_id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER NOT NULL,
                discord_id INTEGER UNIQUE NOT NULL,
                discord_guild_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                avatar TEXT NOT NULL,
                name TEXT NOT NULL,
                race TEXT NOT NULL,
                backstory TEXT NOT NULL,
                x REAL NOT NULL,
                y REAL NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(server_id) REFERENCES servers(server_id)
            )
        """)
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_players_discord ON players(discord_id, discord_guild_id)")

        await conn.commit()
    
    # ---------- Teardown ----------

    async def drop_table(self):
        """
        Drops the players table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        await super().execute(f"DROP TABLE IF EXISTS players")

    async def clear_all(self) -> bool:
        """
        Clears all data from the players table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        affected = await super().delete(
            "DELETE FROM players"
        )
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "players")
        return affected > 0

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

        row = await super().fetchrow(
            query, 
            player_id
        )
        return Player(data=dict(row)) if row else None

    async def get_all(self) -> List[Player]:
        rows = await super().fetch("SELECT * FROM players")
        return [Player(data=dict(row)) for row in rows]
    
    # ---------- Additional Queries ----------
  
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
        
        row = await super().fetchrow(
            query, 
            discord_id
        )
        return Player(data=dict(row)) if row else None
    
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
        rows = await super().fetch(
            query, 
            discord_guild_id
        )
        return [Player(data=dict(row)) for row in rows]
    
    # ---------- Existence Checks ----------

    async def exists(self, player_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM players WHERE player_id = ?",
            player_id
        )
        return row is not None

    # ---------- Additional Existence Checks ----------

    async def exists_by_discord_id(self, discord_id: int, discord_guild_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM players WHERE discord_id = ? AND discord_guild_id = ?",
            discord_id,
            discord_guild_id
        )
        return row is not None

    # ---------- Mutations ----------

    async def insert(self, player: Player) -> int:
        return await super().insert(
            """
                INSERT INTO players (
                    discord_id, discord_guild_id, server_id, username, avatar, name, race, backstory, x, y
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(discord_id) DO NOTHING
            """,
            player.discord_id,
            player.discord_guild_id,
            player.server_id,
            player.username,
            player.avatar,
            player.name,
            player.race,
            player.x,
            player.y,
            player.backstory
        )

    async def update(self, player: Player) -> bool:
        affected = await super().update(
            """
                UPDATE players
                SET username = ?, avatar = ?, discord_guild_id = ?, server_id = ?, name = ?, race = ?, backstory = ?, x =?, y = ?
                WHERE discord_id = ?
            """, 
            player.username,
            player.avatar,
            player.discord_guild_id,
            player.server_id,
            player.name,
            player.race,
            player.backstory,
            player.x,
            player.y,
            player.discord_id
        )
        return affected > 0

    async def delete(self, player: Player) -> bool:
        affected = await super().delete(
            """
                DELETE FROM players WHERE (discord_id = ? AND discord_guild_id = ?) OR player_id = ?
            """, 
            player.discord_id,
            player.discord_guild_id,
            player.player_id
        )
        return affected > 0
    
    async def delete_all(self, server_id: int) -> bool:
        # Delete_all and clear_all do the same in this repository since there are no environment variables to restrict by.
        affected = await super().delete(
            "DELETE FROM players WHERE server_id = ?",
            server_id
        )
        return affected > 0

    # ---------- Custom Methods ----------

    async def get_count(self, server_id: int) -> int:
        rows = await super().fetch(
            "SELECT COUNT(*) as count FROM players WHERE server_id = ?", 
            server_id
        )
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

    async def get_leaderboard(self, server_id: int, page: int, sort_by: str = "Total", limit: int = 10) -> List[Player]:
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
            offset = (page - 1) * limit
            query += f" LIMIT {limit} OFFSET ?"
            params.append(offset)

        rows = await super().fetch(
            query, 
            *params
        )
        return [Player(data=dict(row)) for row in rows]