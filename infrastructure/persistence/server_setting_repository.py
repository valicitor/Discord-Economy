from domain import ServerSetting
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class ServerSettingRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "dynamic_resources.db")

    def init_database(self):
        with self._lock:
            c = self.conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS server_settings (
                    setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_id INTEGER NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    FOREIGN KEY(server_id) REFERENCES servers(server_id)
                )
            """)
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.commit()

    # ---------- Queries ----------

    def get_by_id(self, setting_id: int) -> Optional[ServerSetting]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT * FROM server_settings WHERE setting_id = ?", (setting_id,)
            )
            row = c.fetchone()
            return ServerSetting(data=dict(row)) if row else None

    def get_all(self) -> List[ServerSetting]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("SELECT * FROM server_settings")
            return [ServerSetting(data=dict(row)) for row in c.fetchall()]
        
    def get_all_by_server_id(self, server_id: int) -> List[ServerSetting]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("SELECT * FROM server_settings WHERE server_id = ?", (server_id,))
            return [ServerSetting(data=dict(row)) for row in c.fetchall()]

    # ---------- Mutations ----------

    def add(self, server_setting: ServerSetting) -> tuple[bool, int]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                INSERT INTO server_settings (
                    server_id, key, value
                )
                VALUES (?, ?, ?)
            """, (
                server_setting.server_id,
                server_setting.key,
                server_setting.value
            ))

            self.conn.commit()
            return (c.rowcount > 0, c.lastrowid)

    def update(self, server_setting: ServerSetting) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                UPDATE server_settings
                SET server_id = ?, key = ?, value = ?
                WHERE setting_id = ?
            """, (
                server_setting.server_id,
                server_setting.key,
                server_setting.value,
                server_setting.setting_id
            ))

            self.conn.commit()
            return c.rowcount > 0

    def delete(self, server_setting: ServerSetting) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "DELETE FROM server_settings WHERE setting_id = ?",
                (server_setting.setting_id,)
            )

            self.conn.commit()
            return c.rowcount > 0
    
    def delete_all(self) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("DELETE FROM server_settings")
            self.conn.commit()
            return c.rowcount > 0

    def exists(self, setting_id: int) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT 1 FROM server_settings WHERE setting_id = ?", (setting_id,)
            )
            return c.fetchone() is not None