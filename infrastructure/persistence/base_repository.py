import aiosqlite
import asyncio
import atexit

class BaseRepository:
    _pool = None

    async def __init__(self, seeder=None, db_path: str = None):
        self.db_path = db_path or "repository.db"
        self._transaction_active = False
        self._connection = None

        if not BaseRepository._pool:
            await self._initialize_pool()
        
        await self.init_database()

        if seeder:
            await seeder.seed()

    async def _initialize_pool(self):
        if not BaseRepository._pool:
            BaseRepository._pool = await aiosqlite.connect(self.db_path)
            BaseRepository._pool.row_factory = aiosqlite.Row

    async def acquire_connection(self):
        if not self._connection:
            self._connection = BaseRepository._pool

    async def close(self):
        if BaseRepository._pool:
            await BaseRepository._pool.close()
            BaseRepository._pool = None

    async def execute(self, query: str, *args):
        await self.acquire_connection()
        await self._connection.execute(query, *args)
        if not self._transaction_active:
            await self._connection.commit()

    async def fetch(self, query: str, *args):
        await self.acquire_connection()
        cursor = await self._connection.execute(query, *args)
        rows = await cursor.fetchall()
        await cursor.close()
        return rows

    async def fetchrow(self, query: str, *args):
        await self.acquire_connection()
        cursor = await self._connection.execute(query, *args)
        row = await cursor.fetchone()
        await cursor.close()
        return row

    async def insert(self, query: str, *args) -> int:
        await self.acquire_connection()
        cursor = await self._connection.execute(query, *args)
        if not self._transaction_active:
            await self._connection.commit()
        last_id = cursor.lastrowid
        await cursor.close()
        return last_id

    async def update(self, query: str, *args) -> int:
        await self.acquire_connection()
        cursor = await self._connection.execute(query, *args)
        if not self._transaction_active:
            await self._connection.commit()
        rowcount = cursor.rowcount
        await cursor.close()
        return rowcount

    async def delete(self, query: str, *args) -> int:
        await self.acquire_connection()
        cursor = await self._connection.execute(query, *args)
        if not self._transaction_active:
            await self._connection.commit()
        rowcount = cursor.rowcount
        await cursor.close()
        return rowcount

    async def begin_transaction(self):
        await self.acquire_connection()
        if not self._transaction_active:
            await self._connection.execute("BEGIN")
            self._transaction_active = True

    async def commit_transaction(self):
        if self._transaction_active:
            await self._connection.commit()
            self._transaction_active = False

    async def rollback_transaction(self):
        if self._transaction_active:
            await self._connection.execute("ROLLBACK")
            self._transaction_active = False

    async def init_database(self):
        """Placeholder for child classes to override."""
        pass