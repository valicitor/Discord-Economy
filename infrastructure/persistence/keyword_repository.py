from domain import Keyword
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class KeywordRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    def init_database(self):
        with self._lock:
            c = self.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS keywords (
                    keyword_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    metadata TEXT,
                    FOREIGN KEY(server_id) REFERENCES servers(server_id),
                    UNIQUE(name, server_id)
                )
            """)
            self.execute("PRAGMA journal_mode=WAL;")
            self.commit()

    # ---------- Queries ----------

    def get_by_id(self, keyword_id: int) -> Optional[Keyword]:
        with self._lock:
            c = self.cursor()
            c.execute(
                "SELECT * FROM keywords WHERE keyword_id = ?", (keyword_id,)
            )
            row = c.fetchone()
            return Keyword(data=dict(row)) if row else None
    
    def get_by_name(self, name: str, server_id: int) -> Optional[Keyword]:
        with self._lock:
            c = self.cursor()
            c.execute(
                "SELECT * FROM keywords WHERE name = ? AND server_id = ?", (name, server_id)
            )
            row = c.fetchone()
            return Keyword(data=dict(row)) if row else None

    def get_all(self, server_id: int) -> List[Keyword]:
        with self._lock:
            c = self.cursor()
            c.execute("SELECT * FROM keywords WHERE server_id = ?", (server_id,))
            return [Keyword(data=dict(row)) for row in c.fetchall()]

    # ---------- Mutations ----------

    def add(self, keyword: Keyword) -> tuple[bool, int]:
        with self._lock:
            c = self.cursor()
            c.execute("""
                INSERT INTO keywords (
                    server_id, name, description, metadata
                )
                VALUES (?, ?, ?, ?)
            """, (
                keyword.server_id,
                keyword.name,
                keyword.description,
                str(keyword.metadata)
            ))

            self.commit()
            return (c.rowcount > 0, c.lastrowid)

    def update(self, keyword: Keyword) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute("""
                UPDATE keywords
                SET server_id = ?, name = ?, description = ?, metadata = ?
                WHERE keyword_id = ?
            """, (
                keyword.server_id,
                keyword.name,
                keyword.description,
                str(keyword.metadata),
                keyword.keyword_id
            ))

            self.commit()
            return c.rowcount > 0

    def delete(self, keyword: Keyword) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute(
                "DELETE FROM keywords WHERE keyword_id = ?",
                (keyword.keyword_id,)
            )

            self.commit()
            return c.rowcount > 0
    
    def delete_all(self, server_id: int) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute("DELETE FROM keywords WHERE server_id = ?", (server_id,))
            self.commit()
            return c.rowcount > 0

    def exists(self, keyword_id: int) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute(
                "SELECT 1 FROM keywords WHERE keyword_id = ?",
                (keyword_id,)
            )
            return c.fetchone() is not None