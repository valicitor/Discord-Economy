from infrastructure.interfaces.i_server_config_repository import IServerConfigRepository
from typing import List
import sqlite3

class ServerConfigRepository(IServerConfigRepository):
    _instance = None  # Class-level instance token

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ServerConfigRepository, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_path='server_config.db'):
        if not hasattr(self, '_initialized'):
            self.db_path = db_path
            self.init_database()
            self._initialized = True  # Mark as initialized

    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS server_config (
                guild_id TEXT PRIMARY KEY,
                starting_balance INTEGER NOT NULL,
                currency_symbol TEXT NOT NULL,
                currency_emoji TEXT
            )
        ''')
        conn.commit()
        conn.close()

    async def get_by_id(self, id: str):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM server_config WHERE guild_id = ?', (str(id),))
            return c.fetchone()

    async def get_all(self, guild_id: str) -> List[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute('SELECT * FROM server_config')
            rows = c.fetchall()
            return [dict(row) for row in rows]

    async def list(self, guild_id: str) -> List[dict]:
        return await self.get_all(guild_id)

    async def add(self, entity: dict) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO server_config (guild_id, starting_balance, currency_symbol, currency_emoji)
                VALUES (?, ?, ?, ?)
            ''', (entity['id'], entity['starting_balance'], entity['currency_symbol'], entity['currency_emoji']))
            add_count = c.rowcount
            conn.commit()
            return add_count > 0

    async def update(self, entity: dict) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''
                UPDATE server_config
                SET starting_balance = ?, currency_symbol = ?, currency_emoji = ?
                WHERE guild_id = ?  
            ''', (entity['starting_balance'], entity['currency_symbol'], entity['currency_emoji'], entity['id']))
            updated_count = c.rowcount
            conn.commit()
            return updated_count > 0

    async def delete(self, entity: dict) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('DELETE FROM server_config WHERE guild_id = ?', (entity['id'],))
            deleted_count = c.rowcount
            conn.commit()
            return deleted_count > 0

    async def delete_all(self, guild_id: str) -> int:
        raise NotImplementedError("This method is not applicable for ServerConfigRepository since each guild has only one config entry.")

    async def exists(self, id: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('SELECT 1 FROM server_config WHERE guild_id = ?', (str(id),))
            return c.fetchone() is not None