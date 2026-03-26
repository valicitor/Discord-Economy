from domain import User
from infrastructure.interfaces.i_user_repository import IUserRepository
from typing import List
import sqlite3
from threading import Lock

class UserRepository(IUserRepository):
    _instance = None  # Class-level instance token
    _lock = Lock()  # Lock for thread-safe singleton

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(UserRepository, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_path=None):
        if not hasattr(self, '_initialized'):
            self.db_path = db_path or 'users.db'
            self.init_database()
            self._initialized = True  # Mark as initialized

    def _get_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def init_database(self):
        conn = self._get_connection()
        try:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    guild_id INTEGER NOT NULL,
                    username TEXT NOT NULL,
                    cash_balance INTEGER NOT NULL DEFAULT 0,
                    bank_balance INTEGER NOT NULL DEFAULT 0
                )
            ''')
            conn.commit()
        finally:
            conn.close()

    async def get_by_id(self, user_id: str) -> User | None:
        conn = self._get_connection()
        try:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute('SELECT *, RANK() OVER (ORDER BY (cash_balance + bank_balance) DESC) as rank FROM users WHERE user_id = ?', (str(user_id),))
            row = c.fetchone()
            return User(data=dict(row)) if row else None
        finally:
            conn.close()
    
    async def get_all(self, guild_id: str) -> List[User]:
        conn = self._get_connection()
        try:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute('SELECT *, RANK() OVER (ORDER BY (cash_balance + bank_balance) DESC) as rank FROM users WHERE guild_id = ?', (str(guild_id),))
            rows = c.fetchall()
            return [User(data=dict(row)) for row in rows]
        finally:
            conn.close()

    # Options for sort_by: ['Cash', 'Bank', 'Total']
    async def get_leaderboard(self, guild_id: str, page: int = None, sort_by: str = 'Cash') -> List[User]:
        sort_by_column = {
            'Cash': 'cash_balance',
            'Bank': 'bank_balance',
            'Total': '(cash_balance + bank_balance)'
        }[sort_by]

        conn = self._get_connection()
        try:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            if page is not None:
                offset = (page - 1) * 10
                c.execute(f'SELECT *, RANK() OVER (ORDER BY (cash_balance + bank_balance) DESC) as rank FROM users WHERE guild_id = ? ORDER BY {sort_by_column} DESC LIMIT 10 OFFSET ?', (str(guild_id), offset))
            else:
                c.execute(f'SELECT *, RANK() OVER (ORDER BY (cash_balance + bank_balance) DESC) as rank FROM users WHERE guild_id = ? ORDER BY {sort_by_column} DESC', (str(guild_id),))
            rows = c.fetchall()
            return [User(data=dict(row)) for row in rows]
        finally:
            conn.close()

    async def add(self, user: User) -> bool:
        conn = self._get_connection()
        try:
            c = conn.cursor()
            c.execute('''
                INSERT INTO users (user_id, guild_id, username, cash_balance, bank_balance)
                VALUES (?, ?, ?, ?, ?)
            ''', (user.user_id, user.guild_id, user.username, user.cash_balance, user.bank_balance))
            add_count = c.rowcount
            conn.commit()
            return add_count > 0
        finally:
            conn.close()

    async def update(self, user: User) -> bool:
        conn = self._get_connection()
        try:
            c = conn.cursor()
            c.execute('''
                UPDATE users
                SET cash_balance = ?, bank_balance = ?, username = ?
                WHERE user_id = ? AND guild_id = ?  
            ''', (user.cash_balance, user.bank_balance, user.username, user.user_id, user.guild_id))
            updated_count = c.rowcount
            conn.commit()
            return updated_count > 0
        finally:
            conn.close()

    async def delete(self, user: User) -> bool:
        conn = self._get_connection()
        try:
            c = conn.cursor()
            c.execute('DELETE FROM users WHERE user_id = ? AND guild_id = ?', (user.user_id, user.guild_id))
            deleted_count = c.rowcount
            conn.commit()
            return deleted_count > 0
        finally:
            conn.close()

    async def delete_all(self, guild_id: str) -> int:
        """Delete all users for a guild and return the number of deleted records"""
        conn = self._get_connection()
        try:
            c = conn.cursor()
            c.execute('DELETE FROM users WHERE guild_id = ?', (str(guild_id),))
            deleted_count = c.rowcount
            conn.commit()
            return deleted_count
        finally:
            conn.close()

    async def exists(self, user_id: str, guild_id: str) -> bool:
        conn = self._get_connection()
        try:
            c = conn.cursor()
            c.execute('SELECT 1 FROM users WHERE user_id = ? AND guild_id = ?', (str(user_id), str(guild_id),))
            return c.fetchone() is not None
        finally:
            conn.close()