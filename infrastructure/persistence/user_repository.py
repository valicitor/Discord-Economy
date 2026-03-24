from infrastructure.interfaces.i_user_repository import IUserRepository
from typing import List
import sqlite3

class UserRepository(IUserRepository):
    _instance = None  # Class-level instance token

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(UserRepository, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_path='users.db'):
        if not hasattr(self, '_initialized'):
            self.db_path = db_path
            self.init_database()
            self._initialized = True  # Mark as initialized

    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        try:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    guild_id INTEGER NOT NULL,
                    balance INTEGER NOT NULL DEFAULT 0
                )
            ''')
            conn.commit()
        finally:
            conn.close()

    async def get_by_id(self, id: str) -> dict | None:
        conn = sqlite3.connect(self.db_path)
        try:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute('SELECT * FROM users WHERE user_id = ?', (str(id),))
            row = c.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    async def get_all(self, guild_id: str) -> List[dict]:
        conn = sqlite3.connect(self.db_path)
        try:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute('SELECT * FROM users WHERE guild_id = ?', (str(guild_id),))
            rows = c.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    async def list(self, guild_id: str) -> List[dict]:
        return await self.get_all(guild_id)

    async def add(self, entity: dict) -> bool:
        conn = sqlite3.connect(self.db_path)
        try:
            c = conn.cursor()
            c.execute('''
                INSERT INTO users (user_id, guild_id, balance)
                VALUES (?, ?, ?)
            ''', (entity['id'], entity['guild_id'], entity['balance'],))
            add_count = c.rowcount
            conn.commit()
            return add_count > 0
        finally:
            conn.close()

    async def update(self, entity: dict) -> bool:
        conn = sqlite3.connect(self.db_path)
        try:
            c = conn.cursor()
            c.execute('''
                UPDATE users
                SET balance = ?
                WHERE user_id = ? AND guild_id = ?  
            ''', (entity['balance'], entity['id'], entity['guild_id'],))
            updated_count = c.rowcount
            conn.commit()
            return updated_count > 0
        finally:
            conn.close()

    async def delete(self, entity: dict) -> bool:
        conn = sqlite3.connect(self.db_path)
        try:
            c = conn.cursor()
            c.execute('DELETE FROM users WHERE user_id = ? AND guild_id = ?', (entity['id'], entity['guild_id'],))
            deleted_count = c.rowcount
            conn.commit()
            return deleted_count > 0
        finally:
            conn.close()

    async def delete_all(self, guild_id: str) -> int:
        """Delete all users for a guild and return the number of deleted records"""
        conn = sqlite3.connect(self.db_path)
        try:
            c = conn.cursor()
            c.execute('DELETE FROM users WHERE guild_id = ?', (str(guild_id),))
            deleted_count = c.rowcount
            conn.commit()
            return deleted_count
        finally:
            conn.close()

    async def exists(self, id: str, guild_id: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        try:
            c = conn.cursor()
            c.execute('SELECT 1 FROM users WHERE user_id = ? AND guild_id = ?', (str(id), str(guild_id),))
            return c.fetchone() is not None
        finally:
            conn.close()