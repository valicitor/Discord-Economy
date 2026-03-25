from infrastructure.interfaces.i_server_config_repository import IServerConfigRepository
from typing import List
import sqlite3
from threading import Lock

class ServerConfigRepository(IServerConfigRepository):
    _instance = None  # Class-level instance token
    _lock = Lock()  # Lock for thread-safe singleton

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(ServerConfigRepository, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_path=None):
        if not hasattr(self, '_initialized'):
            self.db_path = db_path or 'server_config.db'
            self.init_database()
            self._initialized = True  # Mark as initialized
    
    def _get_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def init_database(self):
        conn = self._get_connection()
        try:
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
        finally:
            conn.close()

    async def get_by_id(self, guild_id: str):
        conn = self._get_connection()
        try:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute('SELECT * FROM server_config WHERE guild_id = ?', (str(guild_id),))
            row = c.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    async def get_all(self) -> List[dict]:
        conn = self._get_connection()
        try:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute('SELECT * FROM server_config')
            rows = c.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    async def add(self, entity: dict) -> bool:
        conn = self._get_connection()
        try:
            c = conn.cursor()
            c.execute('''
                INSERT INTO server_config (guild_id, starting_balance, currency_symbol, currency_emoji)
                VALUES (?, ?, ?, ?)
            ''', (entity['guild_id'], entity['starting_balance'], entity['currency_symbol'], entity['currency_emoji']))
            add_count = c.rowcount
            conn.commit()
            return add_count > 0
        finally:
            conn.close()

    async def update(self, entity: dict) -> bool:
        conn = self._get_connection()
        try:
            c = conn.cursor()
            c.execute('''
                UPDATE server_config
                SET starting_balance = ?, currency_symbol = ?, currency_emoji = ?
                WHERE guild_id = ?  
            ''', (entity['starting_balance'], entity['currency_symbol'], entity['currency_emoji'], entity['guild_id']))
            updated_count = c.rowcount
            conn.commit()
            return updated_count > 0
        finally:
            conn.close()

    async def delete(self, entity: dict) -> bool:
        conn = self._get_connection()
        try:
            c = conn.cursor()
            c.execute('DELETE FROM server_config WHERE guild_id = ?', (entity['guild_id'],))
            deleted_count = c.rowcount
            conn.commit()
            return deleted_count > 0
        finally:
            conn.close()

    async def delete_all(self, guild_id: str) -> int:
        raise NotImplementedError("This method is not applicable for ServerConfigRepository since each guild has only one config entry.")

    async def exists(self, guild_id: str) -> bool:
        conn = self._get_connection()
        try:
            c = conn.cursor()
            c.execute('SELECT 1 FROM server_config WHERE guild_id = ?', (str(guild_id),))
            return c.fetchone() is not None
        finally:
            conn.close()