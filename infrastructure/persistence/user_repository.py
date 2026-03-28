from domain import User
from infrastructure import IUserRepository
from typing import List, Optional
import sqlite3
from threading import Lock
import atexit

class UserRepository(IUserRepository):
    _instance = None
    _instance_lock = Lock()

    def __new__(cls, *args, **kwargs):
        with cls._instance_lock:
            if not cls._instance:
                cls._instance = super(UserRepository, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_path: str = None):
        if not hasattr(self, "_initialized"):
            self.db_path = db_path or "users.db"
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self._lock = Lock()

            self.init_database()

            atexit.register(self.close)
            self._initialized = True

    # ---------- Database Setup ----------

    def init_database(self):
        with self._lock:
            c = self.conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    username TEXT NOT NULL,
                    avatar TEXT NOT NULL,
                    cash_balance INTEGER NOT NULL DEFAULT 0,
                    bank_balance INTEGER NOT NULL DEFAULT 0,
                    last_work REAL,
                    PRIMARY KEY (user_id, guild_id)
                )
            """)
            c.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_guild_id 
                ON users(guild_id)
            """)
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.commit()

    # ---------- Helpers ----------

    def _ensure_connection(self):
        if self.conn is None:
            raise RuntimeError("Database connection is closed")

    def _get_sort_column(self, sort_by: str) -> str:
        mapping = {
            "Cash": "cash_balance",
            "Bank": "bank_balance",
            "Total": "(cash_balance + bank_balance)"
        }

        if sort_by not in mapping:
            raise ValueError(f"Invalid sort_by value: {sort_by}")

        return mapping[sort_by]

    # ---------- Queries ----------

    def get_by_id(self, guild_id: int, user_id: int) -> Optional[User]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                WITH RankedUsers AS (
                    SELECT *,
                        RANK() OVER (
                            PARTITION BY guild_id
                            ORDER BY (cash_balance + bank_balance) DESC
                        ) as rank
                    FROM users
                    WHERE guild_id = ?
                )
                      
                SELECT *
                FROM RankedUsers
                WHERE user_id = ?
            """, (guild_id, user_id))

            row = c.fetchone()
            return User(data=dict(row)) if row else None

    def get_all(self, guild_id: int) -> List[User]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                WITH RankedUsers AS (
                    SELECT *,
                        RANK() OVER (
                            PARTITION BY guild_id
                            ORDER BY (cash_balance + bank_balance) DESC
                        ) as rank
                    FROM users
                    WHERE guild_id = ?
                )
                      
                SELECT *
                FROM RankedUsers
            """, (guild_id,))

            return [User(data=dict(row)) for row in c.fetchall()]

    def get_leaderboard(
        self,
        guild_id: int,
        page: int = None,
        sort_by: str = "Total"
    ) -> List[User]:

        sort_column = self._get_sort_column(sort_by)

        query = f"""
            WITH RankedUsers AS (
                SELECT *,
                    RANK() OVER (
                        PARTITION BY guild_id
                        ORDER BY {sort_column} DESC
                    ) as rank
                FROM users
                WHERE guild_id = ?
            )

            SELECT *
            FROM RankedUsers
            ORDER BY {sort_column} DESC
        """

        params = [guild_id]

        if page is not None:
            offset = (page - 1) * 10
            query += " LIMIT 10 OFFSET ?"
            params.append(offset)

        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(query, tuple(params))
            return [User(data=dict(row)) for row in c.fetchall()]

    def get_count(self, guild_id: int) -> int:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT COUNT(*) FROM users WHERE guild_id = ?",
                (guild_id,)
            )
            return c.fetchone()[0]

    # ---------- Mutations ----------

    def add(self, user: User) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                INSERT INTO users (user_id, guild_id, username, avatar, cash_balance, bank_balance, last_work)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id, guild_id) DO NOTHING
            """, (
                user.user_id,
                user.guild_id,
                user.username,
                user.avatar,
                user.cash_balance,
                user.bank_balance,
                user.last_work
            ))

            self.conn.commit()
            return c.rowcount > 0

    def update(self, user: User) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                UPDATE users
                SET username = ?, avatar = ?, cash_balance = ?, bank_balance = ?, last_work = ?
                WHERE user_id = ? AND guild_id = ?
            """, (
                user.username,
                user.avatar,
                user.cash_balance,
                user.bank_balance,
                user.last_work,
                
                user.user_id,
                user.guild_id
            ))

            self.conn.commit()
            return c.rowcount > 0

    def delete(self, user: User) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "DELETE FROM users WHERE user_id = ? AND guild_id = ?",
                (user.user_id, user.guild_id)
            )

            self.conn.commit()
            return c.rowcount > 0

    def delete_all(self, guild_id: int) -> int:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "DELETE FROM users WHERE guild_id = ?",
                (guild_id,)
            )

            self.conn.commit()
            return c.rowcount

    def exists(self, user_id: int, guild_id: int) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT 1 FROM users WHERE user_id = ? AND guild_id = ?",
                (user_id, guild_id)
            )
            return c.fetchone() is not None

    # ---------- Cleanup ----------

    def close(self):
        with self._lock:
            if self.conn:
                self.conn.close()
                self.conn = None