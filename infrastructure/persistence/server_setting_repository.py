from domain import ServerSetting
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class ServerSettingRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    async def init_database(self):
        await self.execute("""
                CREATE TABLE IF NOT EXISTS server_settings (
                    setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_id INTEGER NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    FOREIGN KEY(server_id) REFERENCES servers(server_id)
                )
            """)
        await self.execute("PRAGMA journal_mode=WAL;")

    # ---------- Queries ----------

    async def get_by_id(self, setting_id: int) -> Optional[ServerSetting]:
        query = "SELECT * FROM server_settings WHERE setting_id = ?"
        params = (setting_id,)
        row = await self.fetchrow(query, params)
        return ServerSetting(data=dict(row)) if row else None

    async def get_all(self) -> List[ServerSetting]:
        query = "SELECT * FROM server_settings"
        rows = await self.fetch(query)
        return [ServerSetting(data=dict(row)) for row in rows]
        
    async def get_all_by_server_id(self, server_id: int) -> List[ServerSetting]:
        query = "SELECT * FROM server_settings WHERE server_id = ?"
        params = (server_id,)
        rows = await self.fetch(query, params)
        return [ServerSetting(data=dict(row)) for row in rows]
    
    async def get_by_key(self, key: str, server_id: int) -> Optional[ServerSetting]:
        query = "SELECT * FROM server_settings WHERE key = ? AND server_id = ?"
        params = (key, server_id)
        row = await self.fetchrow(query, params)
        return ServerSetting(data=dict(row)) if row else None

    # ---------- Mutations ----------

    async def add(self, server_setting: ServerSetting) -> tuple[bool, int]:
        query = """
            INSERT INTO server_settings (
                server_id, key, value
            )
            VALUES (?, ?, ?)
        """
        params = (
            server_setting.server_id,
            server_setting.key,
            server_setting.value
        )
        last_id = await self.insert(query, params)
        return (last_id > 0, last_id)
    
    async def update(self, server_setting: ServerSetting) -> bool:
        query = """
            UPDATE server_settings
            SET server_id = ?, key = ?, value = ?
            WHERE setting_id = ?
        """
        params = (
            server_setting.server_id,
            server_setting.key,
            server_setting.value,
            server_setting.setting_id
        )
        last_id = await self.update(query, params)
        return last_id > 0

    async def delete(self, server_setting: ServerSetting) -> bool:
        query = "DELETE FROM server_settings WHERE setting_id = ?"
        params = (server_setting.setting_id,)
        last_id = await self.delete(query, params)
        return last_id > 0
    
    async def delete_all(self, server_id: int) -> bool:
        query = "DELETE FROM server_settings WHERE server_id = ?"
        params = (server_id,)
        last_id = await self.delete(query, params)
        return last_id > 0

    async def exists(self, setting_id: int) -> bool:
        query = "SELECT 1 FROM server_settings WHERE setting_id = ?"
        params = (setting_id,)
        rows = await self.fetch(query, params)
        return len(rows) > 0