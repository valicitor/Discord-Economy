from domain import Player
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class PlayerRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    def init_database(self):
        with self._lock:
            c = self.cursor()
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
            self.execute("PRAGMA journal_mode=WAL;")
            self.commit()

    # ---------- Queries ----------

    def get_by_id(self, player_id: int) -> Optional[Player]:
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
    
        with self._lock:
            c = self.cursor()
            c.execute(
                query, (player_id,)
            )
            row = c.fetchone()
            return Player(data=dict(row)) if row else None
        
    def get_by_discord_id(self, discord_id: int) -> Optional[Player]:
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
    
        with self._lock:
            c = self.cursor()
            c.execute(query, (discord_id,))
            row = c.fetchone()
            return Player(data=dict(row)) if row else None

    def get_all(self, server_id: int = None) -> List[Player]:
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

        with self._lock:
            c = self.cursor()
            if params:
                c.execute(query, params)
            else:
                c.execute(query)
            return [Player(data=dict(row)) for row in c.fetchall()]

    def get_all_by_discord_guild(self, discord_guild_id: int) -> List[Player]:
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
        with self._lock:
            c = self.cursor()
            c.execute(query, (discord_guild_id,))
            return [Player(data=dict(row)) for row in c.fetchall()]

    # ---------- Mutations ----------

    def add(self, player: Player) -> tuple[bool, int]:
        with self._lock:
            c = self.cursor()
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

            self.commit()
            return (c.rowcount > 0, c.lastrowid)

    def update(self, player: Player) -> bool:
        with self._lock:
            c = self.cursor()
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

            self.commit()
            return c.rowcount > 0

    def delete(self, player: Player) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute(
                "DELETE FROM players WHERE (discord_id = ? AND discord_guild_id = ?) OR player_id = ?",
                (player.discord_id, player.discord_guild_id, player.player_id)
            )

            self.commit()
            return c.rowcount > 0
    
    def delete_all(self, server_id: int) -> int:
        with self._lock:
            c = self.cursor()
            c.execute(
                "DELETE FROM players WHERE server_id = ?",
                (server_id,)
            )

            self.commit()
            return c.rowcount

    def exists(self, player_id: int) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute(
                "SELECT 1 FROM players WHERE player_id = ?", (player_id,)
            )
            return c.fetchone() is not None

    def exists_by_discord_id(self, discord_id: int, discord_guild_id: int) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute(
                "SELECT 1 FROM players WHERE discord_id = ? AND discord_guild_id = ?",
                (discord_id, discord_guild_id)
            )
            return c.fetchone() is not None
    
    # ---------- Custom Methods ----------

    def get_count(self, server_id: int) -> int:
        with self._lock:
            c = self.cursor()
            c.execute(
                "SELECT COUNT(*) as count FROM players WHERE server_id = ?", (server_id,)
            )
            row = c.fetchone()
            return row["count"] if row else 0

    def _get_sort_column(self, sort_by: str) -> str:
        mapping = {
            "Cash": "RANK() OVER (ORDER BY SUM(pb.balance) DESC) AS rank",
            "Bank": "RANK() OVER (ORDER BY SUM(ba.balance) DESC) AS rank",
            "Total": "RANK() OVER (ORDER BY (SUM(pb.balance) + SUM(ba.balance)) DESC) AS rank"
        }

        if sort_by not in mapping:
            raise ValueError(f"Invalid sort_by value: {sort_by}")

        return mapping[sort_by]

    def get_leaderboard(self, server_id: int, page: int, sort_by: str = "Total") -> List[Player]:
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

        with self._lock:
            c = self.cursor()
            
            c.execute(query, params)

            return [Player(data=dict(row)) for row in c.fetchall()]