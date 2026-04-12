from domain import ServerSetting, IRepository
from infrastructure import BaseRepository
from typing import List, Optional

class ServerSettingRepository(BaseRepository, IRepository):
    
    # ---------- Schema Setup ----------

    async def init_database(self):
        """
        initalizes the database schema for the server_settings table. Called automatically on first use. Override in child classes to create tables.
        connection is managed by BaseRepository, so we can use super() to execute our schema setup queries.
        """
        conn = await super().acquire_connection()

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS server_settings (
                setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (server_id) REFERENCES servers (server_id) ON DELETE CASCADE
            )
        """)

        await conn.commit()
    
    # ---------- Teardown ----------

    async def drop_table(self):
        """
        Drops the server_settings table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        await super().execute(f"DROP TABLE IF EXISTS server_settings")

    async def clear_all(self) -> bool:
        """
        Clears all data from the server_settings table. Use with caution! This will delete all data in the table and cannot be undone.
        """
        affected = await super().delete(
            "DELETE FROM server_settings"
        )
        await super().execute("DELETE FROM sqlite_sequence WHERE name = ?", "server_settings")
        return affected > 0

    # ---------- Queries ----------

    async def get_by_id(self, setting_id: int) -> Optional[ServerSetting]:
        row = await super().fetchrow(
            "SELECT * FROM server_settings WHERE setting_id = ?",
            setting_id
        )
        return ServerSetting(data=dict(row)) if row else None

    async def get_all(self) -> List[ServerSetting]:
        rows = await super().fetch("SELECT * FROM server_settings")
        return [ServerSetting(data=dict(row)) for row in rows]
    
    # ---------- Additional Queries ----------
  
    async def get_by_key(self, key: str, server_id: int) -> Optional[ServerSetting]:
        row = await super().fetchrow(
            "SELECT * FROM server_settings WHERE key = ? AND server_id = ?", 
            key, 
            server_id
        )
        return ServerSetting(data=dict(row)) if row else None

    async def get_all_by_server_id(self, server_id: int) -> List[ServerSetting]:
        rows = await super().fetch(
            "SELECT * FROM server_settings WHERE server_id = ?",
            server_id
        )
        return [ServerSetting(data=dict(row)) for row in rows]
    
    # ---------- Existence Checks ----------

    async def exists(self, setting_id: int) -> bool:
        row = await super().fetchrow(
            "SELECT 1 FROM server_settings WHERE setting_id = ?",
            setting_id
        )
        return row is not None
    
    # ---------- Additional Existence Checks ----------

    # ---------- Mutations ----------

    async def insert(self, server_setting: ServerSetting) -> int:
        return await super().insert(
            "INSERT INTO server_settings (server_id, key, value) VALUES (?, ?, ?)",
            server_setting.server_id,
            server_setting.key,
            server_setting.value
        )

    async def update(self, server_setting: ServerSetting) -> bool:
        affected = await super().update(
            "UPDATE server_settings SET key = ?, value = ? WHERE setting_id = ?",
            server_setting.key,
            server_setting.value,
            server_setting.setting_id
        )
        return affected > 0

    async def delete(self, server_setting: ServerSetting) -> bool:
        affected = await super().delete(
            "DELETE FROM server_settings WHERE setting_id = ?",
            server_setting.setting_id
        )
        return affected > 0
    
    async def delete_all(self, server_id: int) -> bool:
        # Delete_all and clear_all do the same in this repository since there are no environment variables to restrict by.
        affected = await super().delete(
            "DELETE FROM server_settings WHERE server_id = ?",
            server_id
        )
        return affected > 0