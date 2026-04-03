from domain import Business
from domain import IRepository
from infrastructure import BaseRepository
from typing import List, Optional


class BusinessRepository(IRepository, BaseRepository):
    def __init__(self, seeder=None, db_path: str = None):
        super().__init__(seeder=seeder, db_path=db_path or "repository.db")

    def init_database(self):
        with self._lock:
            c = self.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS businesses (
                    business_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_id INTEGER NOT NULL,
                    owner_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    type TEXT NOT NULL,
                    location TEXT,
                    range INTEGER,
                    metadata TEXT,
                    FOREIGN KEY(server_id) REFERENCES servers(server_id),
                    UNIQUE(name, server_id)
                )
            """)
            self.execute("PRAGMA journal_mode=WAL;")
            self.commit()

    # ---------- Queries ----------

    def get_by_id(self, business_id: int) -> Optional[Business]:
        with self._lock:
            c = self.cursor()
            c.execute(
                "SELECT * FROM businesses WHERE business_id = ?", (business_id,)
            )
            row = c.fetchone()
            return Business(data=dict(row)) if row else None
    
    def get_by_name(self, name: str, server_id: int) -> Optional[Business]:
        with self._lock:
            c = self.cursor()
            c.execute(
                "SELECT * FROM businesses WHERE name = ? AND server_id = ?", (name, server_id)
            )
            row = c.fetchone()
            return Business(data=dict(row)) if row else None

    def get_all(self, server_id: int) -> List[Business]:
        with self._lock:
            c = self.cursor()
            c.execute("SELECT * FROM businesses WHERE server_id = ?", (server_id,))
            return [Business(data=dict(row)) for row in c.fetchall()]

    # ---------- Mutations ----------

    def add(self, business: Business) -> tuple[bool, int]:
        with self._lock:
            c = self.cursor()
            c.execute("""
                INSERT INTO businesses (
                    server_id, owner_id, name, description, type, location, range, metadata
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                business.server_id,
                business.owner_id,
                business.name,
                business.description,
                business.type,
                business.location,
                business.range,
                str(business.metadata)
            ))

            self.commit()
            return (c.rowcount > 0, c.lastrowid)

    def update(self, business: Business) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute("""
                UPDATE businesses
                SET server_id = ?, owner_id = ?, name = ?, description = ?, type = ?, location = ?, range = ?, metadata = ?
                WHERE business_id = ?
            """, (
                business.server_id,
                business.owner_id,
                business.name,
                business.description,
                business.type,
                business.location,
                business.range,
                str(business.metadata),
                business.business_id
            ))

            self.commit()
            return c.rowcount > 0

    def delete(self, business: Business) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute(
                "DELETE FROM businesses WHERE business_id = ?",
                (business.business_id,)
            )

            self.commit()
            return c.rowcount > 0
    
    def delete_all(self, server_id: int) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute("DELETE FROM businesses WHERE server_id = ?", (server_id,))
            self.commit()
            return c.rowcount > 0

    def exists(self, business_id: int) -> bool:
        with self._lock:
            c = self.cursor()
            c.execute(
                "SELECT 1 FROM businesses WHERE business_id = ?",
                (business_id,)
            )
            return c.fetchone() is not None