import aiosqlite
import asyncio
import os
import contextvars


# Per-coroutine transaction context
_active_tx = contextvars.ContextVar("active_tx", default=None)


class BaseRepository:
    _connections = {}
    _instances = {}
    _init_locks = {}
    _locks = {}
    _class_db_paths = {}

    def __init__(self, db_path: str = None):
        if db_path and db_path != ":memory:":
            db_path = os.path.abspath(db_path)
        self.db_path = db_path or os.path.abspath("repository.db")

    # ---------- Factory / Singleton ----------

    @classmethod
    async def get_instance(cls, db_path: str = None):
        if db_path and db_path != ":memory:":
            db_path = os.path.abspath(db_path)

        default_path = os.path.abspath("repository.db")

        if cls not in cls._class_db_paths:
            cls._class_db_paths[cls] = db_path or default_path

        chosen_path = cls._class_db_paths[cls]

        if db_path is not None and db_path != chosen_path:
            raise RuntimeError(
                f"{cls.__name__} already initialized with db_path='{chosen_path}', "
                f"cannot reinitialize with '{db_path}'"
            )

        key = (cls, chosen_path)

        if key in cls._instances:
            return cls._instances[key]

        if key not in cls._init_locks:
            cls._init_locks[key] = asyncio.Lock()

        async with cls._init_locks[key]:
            if key in cls._instances:
                return cls._instances[key]

            repo = cls(db_path=chosen_path)
            await repo.initialize()

            cls._instances[key] = repo
            return repo

    # ---------- Initialization ----------

    async def initialize(self):
        if self.db_path not in BaseRepository._connections:
            if self.db_path == ":memory:":
                db_uri = "file::memory:?cache=shared"
                uri = True
            else:
                db_uri = self.db_path
                uri = False

            # IMPORTANT: isolation_level=None for manual transaction control
            conn = await aiosqlite.connect(db_uri, uri=uri, isolation_level=None)
            conn.row_factory = aiosqlite.Row

            await conn.execute("PRAGMA journal_mode=WAL;")
            await conn.commit()

            BaseRepository._connections[self.db_path] = conn
            BaseRepository._locks[self.db_path] = asyncio.Lock()

        await self.init_database()

    async def init_database(self):
        pass

    # ---------- Connection ----------

    async def acquire_connection(self):
        if self.db_path not in BaseRepository._connections:
            raise RuntimeError(
                f"No connection for db_path='{self.db_path}'. "
                "Was initialize() called?"
            )
        return BaseRepository._connections[self.db_path]

    # ---------- Internal Helper ----------

    async def _get_connection_and_lock(self):
        tx_conn = _active_tx.get()

        if tx_conn:
            return tx_conn, None  # no lock, already held by transaction

        conn = await self.acquire_connection()
        lock = BaseRepository._locks[self.db_path]
        return conn, lock

    # ---------- Core Query Methods ----------

    async def execute(self, query: str, *args):
        conn, lock = await self._get_connection_and_lock()

        if lock:
            async with lock:
                await conn.execute(query, args)
                await conn.commit()
        else:
            await conn.execute(query, args)

    async def fetch(self, query: str, *args):
        conn, lock = await self._get_connection_and_lock()

        if lock:
            async with lock:
                cursor = await conn.execute(query, args)
                rows = await cursor.fetchall()
                await cursor.close()
                return rows
        else:
            cursor = await conn.execute(query, args)
            rows = await cursor.fetchall()
            await cursor.close()
            return rows

    async def fetchrow(self, query: str, *args):
        conn, lock = await self._get_connection_and_lock()

        if lock:
            async with lock:
                cursor = await conn.execute(query, args)
                row = await cursor.fetchone()
                await cursor.close()
                return row
        else:
            cursor = await conn.execute(query, args)
            row = await cursor.fetchone()
            await cursor.close()
            return row

    async def insert(self, query: str, *args) -> int:
        conn, lock = await self._get_connection_and_lock()

        if lock:
            async with lock:
                cursor = await conn.execute(query, args)
                await conn.commit()
                last_id = cursor.lastrowid
                await cursor.close()
                return last_id
        else:
            cursor = await conn.execute(query, args)
            last_id = cursor.lastrowid
            await cursor.close()
            return last_id

    async def update(self, query: str, *args) -> int:
        conn, lock = await self._get_connection_and_lock()

        if lock:
            async with lock:
                cursor = await conn.execute(query, args)
                await conn.commit()
                count = cursor.rowcount
                await cursor.close()
                return count
        else:
            cursor = await conn.execute(query, args)
            count = cursor.rowcount
            await cursor.close()
            return count

    async def delete(self, query: str, *args) -> int:
        conn, lock = await self._get_connection_and_lock()

        if lock:
            async with lock:
                cursor = await conn.execute(query, args)
                await conn.commit()
                count = cursor.rowcount
                await cursor.close()
                return count
        else:
            cursor = await conn.execute(query, args)
            count = cursor.rowcount
            await cursor.close()
            return count

    # ---------- Transactions ----------

    def transaction(self):
        return _TransactionContext(self)

    # ---------- Shutdown ----------

    @classmethod
    async def close_all(cls):
        for conn in cls._connections.values():
            await conn.close()

        cls._connections.clear()
        cls._locks.clear()
        cls._instances.clear()
        cls._init_locks.clear()
        cls._class_db_paths.clear()


class _TransactionContext:
    def __init__(self, repo: BaseRepository):
        self.repo = repo
        self.conn = None
        self.lock = None
        self.token = None

    async def __aenter__(self):
        self.conn = await self.repo.acquire_connection()
        self.lock = BaseRepository._locks[self.repo.db_path]

        await self.lock.acquire()
        await self.conn.execute("BEGIN")

        # Set transaction context (per coroutine)
        self.token = _active_tx.set(self.conn)

        return self.conn

    async def __aexit__(self, exc_type, exc, tb):
        try:
            if exc_type:
                await self.conn.execute("ROLLBACK")
            else:
                await self.conn.commit()
        finally:
            _active_tx.reset(self.token)
            self.lock.release()