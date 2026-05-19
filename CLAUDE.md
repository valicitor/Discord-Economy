# Discord Economy Bot — Claude Code Guide

## Project Overview

Python 3.13+ Discord bot (discord.py 2.x) implementing a persistent, multi-server economy and logistics system. SQLite via `aiosqlite`. Bot token is loaded from `.env`.

## Running & Testing

```bash
# Run the bot
python main.py

# Run all tests
python -m unittest discover tests

# Run a specific test file
python -m unittest tests.commands.test_work
```

**No build step.** Dependencies: `pip install -r requirements.txt` (discord.py, aiosqlite, python-dotenv).

---

## Architecture: Four Layers

```
host/          → Discord layer (cogs receive slash commands, embeds format responses)
application/   → Business logic (commands mutate state, queries read state)
domain/        → Domain models and exceptions
infrastructure/ → Repositories (aiosqlite SQLite) and seeders (JSON → DB)
```

Data flows **down** (host → application → infrastructure) and back up as response objects. Layers never import across the boundary in the other direction.

---

## Domain-Driven Design

The project follows DDD. Keep these principles when adding or changing code:

**Ubiquitous language.** Every domain concept (Business, PlayerStock, Loan, Transport, Recipe, LocationPolicy) maps directly to a class in `domain/models/`. Use the same names in code, tests, seed data, and conversation.

**Domain isolation.** `domain/` has zero dependencies on `application/`, `host/`, or `infrastructure/`. Models and exceptions are pure Python — no aiosqlite, no discord.py. The domain defines *what* a repository must do via `domain/interfaces/i_repository.py`; infrastructure wires up *how*.

**Bounded contexts.** Each sub-directory under `application/` is a bounded context (balance, economy, shop, logistics, work, faction, player, admin). Commands and queries in one context do not directly import from another — they go through shared helpers (`Helpers.get_player_profile`, `Helpers.get_server_config`) or load their own repositories.

**Application services orchestrate; domain models encapsulate.** Business rules belong in domain models or domain services, not in cog methods or repositories. Commands and queries orchestrate: load entities, call domain logic, persist results.

**Repositories are domain-defined.** `IRepository` lives in `domain/interfaces/` — it specifies the contract. `infrastructure/persistence/` implements it. The application layer programs against the interface, not the concrete class.

**Domain exceptions signal business rule violations.** Raise `InsufficientFundsException`, `OnCooldownException`, `PermissionDeniedException`, etc. from domain/application code. Never let raw SQLite errors or generic `ValueError`s surface to the cog layer.

---

## Timestamp Pattern — No Background Processes

**The bot has no scheduler, no background tasks, and no supporting services.** There is no process that fires periodically to accrue interest, pay dividends, drain maintenance, or tick resource nodes. Discord only invokes the bot in response to a slash command.

All time-based effects are therefore **resolved lazily** at the start of the relevant command, immediately before the command processes its own action:

1. Read the entity's `last_updated_at` timestamp from the DB.
2. Compute `elapsed = now - last_updated_at`.
3. Apply all effects proportional to `elapsed` (e.g. interest = principal × rate × elapsed_days).
4. Persist the updated entity with a new `last_updated_at = now`.
5. Then execute the actual command logic.

**Models that accrue effects over time must carry a `last_updated_at` column:** `Loan`, `PlayerStock`, `BusinessInventory`, `ResourceNode`, `PlayerUnit` (maintenance). When adding a new time-sensitive model, include this column in `init_database()` and update it on every write.

The service responsible for lazy tick resolution lives (or will live) in `application/services/` as `EconomyTickService`. It must be **idempotent** — if interrupted and re-called within the same second it must not double-apply. Guard with `if elapsed <= 0: return`.

Admin commands that previously triggered these effects manually (e.g. `PayDividendsCommand`) become thin wrappers that call the tick service explicitly for testing or catch-up; they are no longer the sole trigger.

**Consequence for tests:** When testing time-sensitive logic, control time explicitly. Store a known `last_updated_at` in the test setup, then assert the computed effect against a known `elapsed` value. Never rely on `datetime.now()` being "close enough".

---

## Data Model Philosophy

Tables and domain models are designed around two goals: **modularity** and **complete user-facing reads**.

### Modular and extensible tables

Each table represents exactly one domain concept. Responsibilities are never shared between tables, and unrelated attributes are never co-located on the same row.

- **One entity, one table.** `PlayerBalance`, `BankAccount`, `Inventory`, `PlayerUnit` are separate tables with FK relationships to `Player` — not columns on a monolithic player row.
- **FK-linked extensions over wide tables.** When a concept gains optional behaviour (e.g. a `Location` gains governance rules), attach a new linked table (`LocationPolicy`) rather than adding nullable columns to the existing one.
- **Nullable columns for truly optional scalar fields only.** If the optional data has its own identity or can repeat, it belongs in a separate table.
- **All physical goods in one catalogue.** Raw materials and finished goods both live in `catalogue`. Recipes reference catalogue items by FK + quantity. This avoids parallel type systems and makes every good uniformly addressable.
- **Every multi-server table carries `server_id`.** All game data is scoped to a guild. `server_id` is always a column and the first filter in every `get_all` query.
- **Relations are ID-based after seeding.** Seeders resolve cross-entity names → IDs at insert time. Once data is in the DB, all references are FK integers — never name strings.

### Tables designed for complete reads

The data model must make it possible to assemble a complete, meaningful response to a player command with a small, predictable number of queries. Design each table so that all data a player would naturally want in a given context can be co-loaded from closely related tables.

- **The `PlayerProfile` aggregate is the primary read surface.** `Helpers.get_player_profile()` loads a `Player` plus all related collections (balances, bank accounts, inventory, units, actions) in one place. Commands read from this aggregate; they do not re-query individual sub-tables.
- **Collections carry typed `get_by_*` helpers.** `PlayerBalancesCollection.get_by_currency_id()`, `PlayerInventoryCollection.get_by_item_id()`, etc. return `(index, item)` tuples so commands can update in-place without a second DB round-trip.
- **Related display data is FK-resolvable, not string-cached.** Embeds that need a currency symbol, item name, or business name resolve it from the already-loaded `ServerConfig` or `PlayerProfile` — they do not store denormalised display strings on the child row.
- **Avoid queries inside loops.** If a command needs a set of related entities, load the full set once with `get_all(filter_id)` before iterating. Never issue a `get_by_id` inside a for-loop over rows.

---

### host/cogs/ — Slash Command Handlers

Each cog inherits `BaseCog` ([host/cogs/base_cog.py](host/cogs/base_cog.py)):
- `cog_app_command_error` catches all exceptions and sends ephemeral error messages — no need for try/except in individual commands.
- `_guild(interaction)` → `DiscordGuild` DTO.
- `_user(u)` → `DiscordUser` DTO.

Cog methods are thin: extract DTOs, call a Command or Query, pass the response to an Embed builder.

```python
@app_commands.command(name="work")
@app_commands.guild_only()
async def user_work(self, interaction: discord.Interaction):
    guild = self._guild(interaction)
    user  = self._user(interaction.user)
    response = await WorkCommand(WorkCommandRequest(guild=guild, user=user, work_type="Work")).execute()
    view = await DiscordWorkEmbed.get_work_view(interaction, response)
    await interaction.response.send_message(view=view)
```

### application/ — Commands and Queries

Every operation is a class with a typed `Request` dataclass, a typed `Response` dataclass, and an `async execute()` method.

- **Commands** (`application/{domain}/commands/`) — mutate state, use transactions.
- **Queries** (`application/{domain}/queries/`) — read-only, no transactions needed.

Repositories are instantiated via singleton factory: `await FooRepository().get_instance()`. Parallel init is fine in production commands via `asyncio.gather()`. **Exception: `Helpers.ensure_user` / any code exercised by the test harness must remain sequential** — see the [Critical Asyncio Constraint](#critical-asyncio-constraint) section.

Common helpers live in [application/services/helpers.py](application/services/helpers.py):
- `Helpers.get_server_config(guild_id)` — loads `ServerConfig` DTO.
- `Helpers.get_player_profile(guild_id, user_id)` — loads aggregated `PlayerProfile`.
- `Helpers.ensure_guild_and_user(guild, user)` → `(ServerConfig, PlayerProfile)`.
- `Helpers.format_cash_amount(n)` — "1.5M", "500K", "1,234".
- `Helpers.format_countdown(seconds)` — "2h 30m 45s".
- `Helpers.is_in_range(ex, ey, range, px, py)` — Euclidean distance check.

### domain/models/ — Plain Python Classes

Models use a dict-based init pattern — **not** dataclasses or attrs:

```python
class Player:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}
        self.player_id: int | None = kwargs.get('player_id')
        self.discord_id: int | None = kwargs.get('discord_id')
        ...
    def to_dict(self): ...
```

DTOs in `application/dtos/` use `@dataclass`. Collections (e.g. `PlayerBalancesCollection`) subclass `BaseCollection[T]` and expose `get_by_*` helpers that return `(index, item)` tuples for in-place updates.

### infrastructure/persistence/ — Repositories

All repos inherit `BaseRepository` ([infrastructure/persistence/base_repository.py](infrastructure/persistence/base_repository.py)) and implement `IRepository`:

- Singleton factory: `await FooRepository().get_instance(db_path="...")` — one connection per class.
- WAL mode enabled; `isolation_level=None` for manual transaction control.
- `contextvars.ContextVar` tracks the active transaction per coroutine.
- Core base methods: `fetch`, `fetchrow`, `insert`, `update`, `delete`, `execute`.

Rows are converted to models with `Model(data=dict(row))`.

**Transactions:**
```python
async with self.some_repository.transaction():
    # all operations here share a connection and are committed atomically
    # exception → ROLLBACK; success → COMMIT
```

**Standard repository interface:**
```python
async def init_database(self)           # CREATE TABLE
async def drop_table(self)              # DROP TABLE
async def clear_all(self) -> bool       # DELETE all + reset sequence
async def get_by_id(self, id) -> Model | None
async def get_all(self, filter_id=None) -> list[Model]
async def insert(self, model) -> int    # returns lastrowid
async def update(self, model) -> bool
async def delete(self, model) -> bool
```

---

## Critical Asyncio Constraint

**Do not parallelize with `asyncio.gather` inside code paths exercised by the test harness.**

The test helper calls `asyncio.run()` separately for `setUp` and `setupData`, producing different event loops per call. An `asyncio.Lock` bound to one loop rejects another loop with `RuntimeError: bound to a different event loop`. Sequential calls never contend, so the lock stays loop-agnostic.

`asyncio.gather` is safe inside production commands (single persistent event loop), but `Helpers.ensure_user` and anything called from `DefaultSetup.setupData` must stay sequential.

---

## Naming Conventions

| Thing | Convention | Example |
|---|---|---|
| Command file | `{action}_{entity}_command.py` | `add_balance_command.py` |
| Query file | `get_{entity}_query.py` | `get_balance_query.py` |
| Repository file | `{entity}_repository.py` | `player_balance_repository.py` |
| Seeder file | `{entities}_seeder.py` | `shop_items_seeder.py` |
| Cog file | `{feature}.py` | `work.py` |
| Embed file | `discord_{feature}_embed.py` | `discord_work_embed.py` |
| Command class | `{Action}{Entity}Command` | `AddBalanceCommand` |
| Request/Response | `{Action}{Entity}CommandRequest/Response` | `AddBalanceCommandRequest` |
| Query class | `Get{Entity}Query` | `GetBalanceQuery` |
| Repository class | `{Entity}Repository` | `PlayerBalanceRepository` |
| Cog class | `{Feature}Cog` | `WorkCog` |

---

## Adding a New Feature

New features follow this checklist top-down:

1. **Domain model** in `domain/models/{entity}.py` — plain class with `data=None` dict init and `to_dict()`.
2. **Domain exception(s)** in `domain/exceptions/` if new failure modes are needed.
3. **Repository** in `infrastructure/persistence/{entity}_repository.py` — extends `BaseRepository, IRepository`, implements `init_database()` and CRUD methods.
4. **Wire repository into `DefaultSetup`** (`tests/helper/default_setup.py`) — `get_instance`, `init_database`, `clear_all`, `drop_table`, and `close_all` must all be present.
5. **Application command or query** in `application/{domain}/commands/` or `.../queries/` — `Request` dataclass, `Response` dataclass, `execute()` method.
6. **Export** from `application/__init__.py` and `domain/__init__.py` and `infrastructure/__init__.py`.
7. **Cog method** in the appropriate `host/cogs/{feature}.py` — thin, delegates entirely to the command/query.
8. **Embed** in `host/embeds/discord_{feature}_embed.py` if new UI is needed.
9. **Tests** in `tests/commands/` or `tests/queries/` — inherit from `unittest.TestCase`, use `asyncio.run()`, call `DefaultSetup` helpers.

---

## Test Pattern

Tests use `unittest.TestCase` + `asyncio.run()`. In-memory SQLite (`:memory:`) via `DefaultSetup`:

```python
class TestMyCommand(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ds = DefaultSetup()
        asyncio.run(cls.ds.setUpClass())   # init 40+ repos

    def setUp(self):
        asyncio.run(self.ds.setUp())       # clear all tables
        asyncio.run(self.ds.setupData())   # seed test guild + players

    def test_something(self):
        response = asyncio.run(MyCommand(MyCommandRequest(...)).execute())
        self.assertTrue(response.success)
```

`DefaultSetup` exposes: `discord_guild`, `discord_user1`, `discord_user2`, `server_config`, `player_profile1`, `player_profile2`, and all 40+ initialized repository instances.

---

## Seed Data

JSON files live in `shared/assets/seed_data/{halo,star_wars}/`. Seeders in `infrastructure/seeders/` extend `BaseSeeder`, load JSON with `_load_json()`, resolve cross-entity relations by name lookup, and insert within a transaction. Seeders skip gracefully if data already exists (idempotent). `/admin setup` triggers all seeders for the calling guild.

---

## Key Config (config.py)

- `BOT_VERSION`, `BOT_NAME`
- `DISCORD_BOT_TOKEN` — from `.env`
- `TEST_SERVER_ID` — dev guild for fast slash-command syncing
- `DO_GLOBAL_SYNC` — enable only for production releases
- `FORCE_SYNC` — force re-sync on every startup (dev only)

---

## Domain Exceptions

All in `domain/exceptions/`:

| Exception | When |
|---|---|
| `RecordNotFoundException` | Entity not found in DB |
| `DuplicateRecordException` | Unique constraint violation |
| `InsufficientFundsException` | Balance too low |
| `OnCooldownException` | Action within cooldown window |
| `PermissionDeniedException` | Missing role or ownership |
| `InvalidDataException` | Bad input values |
| `CreateFailedException` / `UpdateFailedException` / `DeleteFailedException` | DB mutation returned 0 rows |
| `SeederErrorException` | Seeder encountered an unrecoverable state |

`BaseCog.cog_app_command_error` converts all of these to ephemeral Discord messages automatically.
