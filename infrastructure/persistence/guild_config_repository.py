from domain import GuildConfig
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class GuildConfigRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "dynamic_resources.db")

    def init_database(self):
        with self._lock:
            c = self.conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS guild_config (
                    guild_id INTEGER PRIMARY KEY,
                    starting_balance INTEGER NOT NULL,
                    currency_symbol TEXT NOT NULL,
                    currency_emoji TEXT,
                    work_cooldown INTEGER NOT NULL,
                    work_min_pay INTEGER NOT NULL,
                    work_max_pay INTEGER NOT NULL
                )
            """)
            c.execute("PRAGMA table_info(guild_config)")
            existing_columns = {row[1] for row in c.fetchall()}
            if "work_cooldown" not in existing_columns:
                c.execute("ALTER TABLE guild_config ADD COLUMN work_cooldown INTEGER NOT NULL")
            if "work_min_pay" not in existing_columns:
                c.execute("ALTER TABLE guild_config ADD COLUMN work_min_pay INTEGER NOT NULL")
            if "work_max_pay" not in existing_columns:
                c.execute("ALTER TABLE guild_config ADD COLUMN work_max_pay INTEGER NOT NULL")
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.commit()

    # ---------- Queries ----------

    def get_by_id(self, guild_id: int) -> Optional[GuildConfig]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT * FROM guild_config WHERE guild_id = ?",
                (guild_id,)
            )
            row = c.fetchone()
            return GuildConfig(data=dict(row)) if row else None

    def get_all(self) -> List[GuildConfig]:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("SELECT * FROM guild_config")
            return [GuildConfig(data=dict(row)) for row in c.fetchall()]

    # ---------- Mutations ----------

    def add(self, guild_config: GuildConfig) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                INSERT INTO guild_config (
                    guild_id, starting_balance, currency_symbol, currency_emoji, work_cooldown, work_min_pay, work_max_pay
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(guild_id) DO NOTHING
            """, (
                guild_config.guild_id,
                guild_config.starting_balance,
                guild_config.currency_symbol,
                guild_config.currency_emoji,
                guild_config.work_cooldown,
                guild_config.work_min_pay,
                guild_config.work_max_pay
            ))

            self.conn.commit()
            return c.rowcount > 0

    def update(self, guild_config: GuildConfig) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute("""
                UPDATE guild_config
                SET starting_balance = ?, currency_symbol = ?, currency_emoji = ?, work_cooldown = ?, work_min_pay = ?, work_max_pay = ?
                WHERE guild_id = ?
            """, (
                guild_config.starting_balance,
                guild_config.currency_symbol,
                guild_config.currency_emoji,
                guild_config.work_cooldown,
                guild_config.work_min_pay,
                guild_config.work_max_pay,
                guild_config.guild_id
            ))

            self.conn.commit()
            return c.rowcount > 0

    def delete(self, guild_config: GuildConfig) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "DELETE FROM guild_config WHERE guild_id = ?",
                (guild_config.guild_id,)
            )

            self.conn.commit()
            return c.rowcount > 0

    def exists(self, guild_id: int) -> bool:
        with self._lock:
            self._ensure_connection()
            c = self.conn.cursor()
            c.execute(
                "SELECT 1 FROM guild_config WHERE guild_id = ?",
                (guild_id,)
            )
            return c.fetchone() is not None