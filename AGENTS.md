# Discord Economy Bot — Agent Guide

A Python 3.13+ Discord bot implementing a persistent, multi-server economy and logistics game. Discord.py 2.x slash commands. SQLite via `aiosqlite`.

## Directory Map

```
application/   Business logic — commands (mutate) and queries (read), DTOs, helpers
domain/        Plain-class models, domain exceptions, IRepository interface
host/          Discord.py layer — cogs (slash command handlers) and embeds (response formatters)
infrastructure/ Repositories (aiosqlite) and seeders (JSON → DB)
shared/        Seed data JSON files for Halo and Star Wars themes
tests/         unittest test suite with in-memory SQLite
config.py      Runtime config (token, sync flags)
main.py        Bot entry point
```

## Layer Interaction

```
host/cogs        → instantiate Command/Query with Request DTO → await .execute()
application/     → load repositories via singleton factory → run business logic
infrastructure/  → BaseRepository.fetch/insert/update/delete → aiosqlite
domain/models    → consumed and returned throughout; never import host or infrastructure
```

**Cog methods are thin.** They extract DTOs, delegate to one Command or Query, and pass the response to an Embed builder. No logic lives in cogs.

## Domain-Driven Design

This project follows DDD. Key rules:

- **Ubiquitous language.** Every domain concept (Business, PlayerStock, Loan, Transport, Recipe, LocationPolicy) maps 1-to-1 to a `domain/models/` class. Use the same names everywhere.
- **Domain isolation.** `domain/` imports nothing from `application/`, `host/`, or `infrastructure/`. Models and exceptions are pure Python.
- **Repositories are domain-defined.** `domain/interfaces/i_repository.py` specifies the contract; `infrastructure/persistence/` implements it.
- **Bounded contexts.** Each sub-directory under `application/` is a bounded context. Contexts share data only through `Helpers.get_player_profile` / `Helpers.get_server_config`, not by importing each other's commands.
- **Application services orchestrate; domain models encapsulate.** Business rules belong in domain models, not in cog handlers or repositories. Commands and queries load entities, invoke domain logic, persist results.
- **Domain exceptions signal rule violations.** Raise `InsufficientFundsException`, `OnCooldownException`, `PermissionDeniedException`, etc. Never let raw DB errors reach the cog layer.

## Timestamp Pattern — No Background Processes

The bot has no scheduler, no background tasks, and no supporting services. There is no periodic tick. **All time-based effects are resolved lazily at the start of the relevant command:**

1. Read `last_updated_at` from the entity.
2. Compute `elapsed = now - last_updated_at`.
3. Apply effects proportional to `elapsed` (interest, maintenance, dividends, resource production).
4. Persist with `last_updated_at = now`.
5. Then execute the command's own action.

**Models that accrue effects over time must carry a `last_updated_at` column:** `Loan`, `PlayerStock`, `BusinessInventory`, `ResourceNode`, `PlayerUnit`. Add this column to `init_database()` for any new time-sensitive model.

The tick logic lives in `application/services/EconomyTickService`. It must be **idempotent** — guard with `if elapsed <= 0: return`.

Admin commands that previously triggered effects manually (e.g. `PayDividendsCommand`) become wrappers around the tick service; they are no longer the sole trigger.

**Tests:** Control time explicitly. Store a known `last_updated_at` in setup, assert effects against a known `elapsed`. Never rely on wall-clock proximity.

## Data Model Philosophy

Tables and domain models serve two goals: **modularity** and **complete user-facing reads**.

**Modular and extensible:**
- One entity, one table. Related but distinct data (balances, inventory, units) lives in separate FK-linked tables, not as columns on a wide parent row.
- Extend entities with new linked tables rather than adding nullable columns to existing ones (e.g. `LocationPolicy` is a linked table, not columns on `Location`).
- All physical goods live in one `catalogue` table — raw materials and finished goods both — referenced by FK + quantity in recipes and inventory.
- Every multi-server table carries `server_id` as a column and as the first filter in `get_all` queries.
- After seeding, all cross-entity references are FK integers. Seeders resolve names → IDs at insert time; name strings are not stored as references.

**Designed for complete reads:**
- The `PlayerProfile` aggregate DTO is the primary read surface. It co-loads a `Player` with all related collections (balances, bank accounts, inventory, units, actions) in one call. Commands read from this aggregate; they don't re-query sub-tables individually.
- Collections expose typed `get_by_*` helpers returning `(index, item)` tuples for in-place updates without a second DB round-trip.
- Related display data (currency symbol, item name, business name) is resolved from the already-loaded `ServerConfig` or `PlayerProfile` — not cached as denormalised strings on child rows.
- Load full sets with `get_all(filter_id)` before iterating. Never issue `get_by_id` inside a loop.

## Domain Models

Plain Python classes. Init accepts `data: dict = None` plus `**kwargs`; fields assigned via `kwargs.get(...)`. Always includes `to_dict()`. **Not** dataclasses.

Application DTOs (`application/dtos/`) use `@dataclass`. Collection DTOs (e.g. `PlayerBalancesCollection`) subclass `BaseCollection[T]` and add typed `get_by_*` helpers returning `(index, item)` tuples.

`PlayerProfile` is the main aggregate DTO: holds a `Player`, optional faction, plus typed collections for balances, bank accounts, inventory, units, and actions.

## Repository Pattern

All repositories extend `BaseRepository` + `IRepository`:
- `await FooRepository().get_instance(db_path)` — singleton per class, shared connection.
- Standard methods: `init_database`, `drop_table`, `clear_all`, `get_by_id`, `get_all`, `insert` (returns `lastrowid`), `update` (returns `bool`), `delete` (returns `bool`).
- Rows map to models via `Model(data=dict(row))`.
- Transactions: `async with self.repo.transaction(): ...` — auto COMMIT/ROLLBACK.

## Application Helpers

`application/services/helpers.py` — static methods used across commands:
- `get_server_config(guild_id)` → `ServerConfig`
- `get_player_profile(guild_id, user_id)` → `PlayerProfile`
- `ensure_guild_and_user(guild, user)` → `(ServerConfig, PlayerProfile)`
- `format_cash_amount(n)` — "1.5M" / "500K" / "1,234"
- `format_countdown(seconds)` — "2h 30m 45s"
- `is_in_range(ex, ey, range, px, py)` — Euclidean distance

## BaseCog

`host/cogs/base_cog.py`:
- `cog_app_command_error` — catches all exceptions, sends ephemeral Discord error message. No try/except needed in individual commands.
- `_guild(interaction)` → `DiscordGuild`
- `_user(u)` → `DiscordUser`

## Naming Conventions

| Artefact | Pattern | Example |
|---|---|---|
| Command file | `{action}_{entity}_command.py` | `add_balance_command.py` |
| Query file | `get_{entity}_query.py` | `get_balance_query.py` |
| Repository | `{entity}_repository.py` | `player_balance_repository.py` |
| Command class | `{Action}{Entity}Command` | `AddBalanceCommand` |
| Request DTO | `{Action}{Entity}CommandRequest` | `AddBalanceCommandRequest` |
| Response DTO | `{Action}{Entity}CommandResponse` | `AddBalanceCommandResponse` |
| Query class | `Get{Entity}Query` | `GetBalanceQuery` |
| Cog file/class | `{feature}.py` / `{Feature}Cog` | `work.py` / `WorkCog` |
| Embed file | `discord_{feature}_embed.py` | `discord_work_embed.py` |

## Adding a New Feature — Checklist

1. `domain/models/{entity}.py` — plain class, `data=None` init, `to_dict()`
2. `domain/exceptions/` — new exception types if needed
3. `infrastructure/persistence/{entity}_repository.py` — `BaseRepository + IRepository`, `init_database()`, CRUD
4. Wire into `tests/helper/default_setup.py` — `get_instance`, `init_database`, `clear_all`, `drop_table`, `close_all`
5. `application/{domain}/commands/{action}_{entity}_command.py` — Request, Response, `execute()`
6. Export from `application/__init__.py`, `domain/__init__.py`, `infrastructure/__init__.py`
7. `host/cogs/{feature}.py` — thin cog method, `@app_commands.guild_only()`
8. `host/embeds/discord_{feature}_embed.py` — embed builder if new UI needed
9. `tests/commands/test_{action}_{entity}.py` — unittest, asyncio.run(), DefaultSetup

## Test Pattern

```python
class TestMyCommand(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ds = DefaultSetup()
        asyncio.run(cls.ds.setUpClass())    # init all repos with :memory: DB

    def setUp(self):
        asyncio.run(self.ds.setUp())        # clear tables
        asyncio.run(self.ds.setupData())    # seed test guild + 2 players

    def test_something(self):
        response = asyncio.run(MyCommand(MyCommandRequest(...)).execute())
        self.assertTrue(response.success)
```

Run tests: `python -m unittest discover tests`

## Critical: asyncio and Tests

**Never use `asyncio.gather` in code exercised by the test harness** (e.g. `Helpers.ensure_user`, `DefaultSetup.setupData`).

The test harness calls `asyncio.run()` separately for `setUp` and `setupData`, creating a new event loop each call. An `asyncio.Lock` bound to one loop raises `RuntimeError: bound to a different event loop` on the next. Sequential calls are safe because the lock stays loop-agnostic until first contention. `asyncio.gather` is fine in production command code since the bot runs one persistent event loop.

## Seed Data

`shared/assets/seed_data/{halo,star_wars}/` — JSON files. Seeders in `infrastructure/seeders/` extend `BaseSeeder`, load JSON, resolve cross-entity relations by name, insert within a transaction. Idempotent — skip if data already exists. `/admin setup` triggers all seeders for the calling guild.

## Domain Exceptions

`domain/exceptions/` — caught automatically by `BaseCog.cog_app_command_error`:

- `RecordNotFoundException` — entity not found
- `DuplicateRecordException` — unique constraint violation
- `InsufficientFundsException` — balance too low
- `OnCooldownException` — within cooldown window
- `PermissionDeniedException` — missing role or ownership
- `InvalidDataException` — bad input
- `CreateFailedException`, `UpdateFailedException`, `DeleteFailedException` — DB mutation returned 0 rows
- `SeederErrorException` — unrecoverable seeder state
