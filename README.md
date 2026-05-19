## Economy Bot
A modular Discord bot built in Python for running a persistent, strategy-driven economy and warfare system inside a Discord server.

Players earn money, invest, build armies, transport resources, trade stocks, take loans, and influence large-scale conflicts through economic and military decisions.

## Core Features
* Persistent player economy (balance, bank, inventory)
* Business system with stock ownership and dividend payouts
* Multi-currency support with configurable exchange rates
* Loans and interest system
* Unit creation using races and equipment
* Shop and catalogue system for purchasing units and gear
* Resource nodes, crafting recipes with structured inputs/outputs, and business inventory
* Logistics: unit garrisons, maintenance costs, and resource transport between locations
* Faction system with membership management
* Player profiles and progression tracking
* Admin tooling: server setup, business/bank/item/recipe/exchange-rate/policy management
* Per-server configuration and multi-server support
* Dual theme support (Halo and Star Wars seed data)

## Gameplay Overview
* Players earn money through `/work` and business interactions
* Currency can be saved, invested in business stocks, or spent on military units
* Stock ownership earns dividends; loans accrue interest
* Units require upkeep, forcing economic decisions
* Resources can be extracted from nodes, crafted at manufacturing businesses, and transported between locations
* All physical goods (raw materials and finished goods) live in a unified catalogue — recipes define inputs and outputs as catalogue references with quantities
* Factions give players collective identity and future governance hooks
* Wealth can be converted into political or military power

The system is designed so:

* expansion increases maintenance pressure
* economic strength can rival military strength
* player interaction drives the balance

## Example Commands
```
/balance                                           # View your current money
/leaderboard                                       # View the richest players
/pay @User 500                                     # Pay another player
/bank deposit 1000                                 # Deposit into your bank account
/bank withdraw 500                                 # Withdraw from your bank account
/work                                              # Earn money from a business
/shop browse                                       # Browse available items (click to buy)
/shop info Clone Trooper                           # View a catalogue item's full stats
/shop sell DC-15A Blaster Rifle                    # Sell an item from your inventory
/unit create unit_name:Alpha-1 race_name:Human     # Create a custom unit
/unit equip Phase I Clone Armor                    # Equip an item to your character
/unit unequip Phase I Clone Armor                  # Return an item to your inventory
/unit unassign unit_name:Alpha-1 slot_name:Armor   # Remove equipment from a unit slot
/market stocks                                     # View your stock portfolio
/market buy business_id:1                          # Buy shares in a business
/market exchange                                   # Convert between currencies
/loan take amount:1000                             # Take out a loan
/loan repay                                        # Repay your outstanding loan
/logistics garrison assign                         # Assign a unit to garrison a location
/logistics garrison view                           # View your garrisoned units
/logistics maintenance pay                         # Pay upkeep for all your units
/logistics transport start                         # Start transporting a resource between businesses
/logistics transport complete                      # Collect all arrived transports
/faction create                                    # Create a faction
/faction join name:Rebels                          # Join an existing faction
/faction leave                                     # Leave your current faction
/faction info name:Rebels                          # View faction details
/register                                          # Register as a new player
/profile                                           # View your character profile
/help                                              # Show all commands
```

## Setup

### Requirements
* Python 3.13+
* Discord bot token

### Installation
```bash
git clone https://github.com/valicitor/Discord-Economy
cd Discord-Economy
pip install -r requirements.txt
```

### Configuration
Edit `config.py` and add your bot token and settings.

### Run
```bash
python main.py
```

## Project Structure
```
/application
    /admin        # Server and game object management commands
    /balance      # Currency, banking, leaderboard
    /economy      # Stocks, loans, dividends, exchange
    /faction      # Faction creation and membership
    /logistics    # Garrisons, transport, maintenance
    /player       # Player registration and profiles
    /shop         # Buy/sell items and equipment
    /work         # Work commands and cooldowns
    /services     # Shared helpers and economy tick service
    /dtos         # Data transfer objects
/domain
    /exceptions   # Domain exception types
    /models       # All domain models
/host
    /cogs         # Discord slash command groups
    /embeds       # Rich Discord embed formatters
/infrastructure
    /persistence  # Repository pattern data access
    /seeders      # Game data initialisation from JSON
/shared
    /assets/seed_data
        /halo       # Halo-themed seed data
        /star_wars  # Star Wars-themed seed data
/tests
```

## Roadmap

### Completed
* Currency system and banking
* Work system with cooldowns
* Business system
* Business stock ownership and dividend payouts
* Loans and interest
* Multi-currency exchange rates
* Shop, catalogue, and inventory
* Custom units using races and equipment
* Player profiles and registration
* Per-server configuration
* Dual-theme seed data (Halo, Star Wars)
* Command structure refactor: unified `/admin`, `/market`, `/shop`, `/unit`, `/logistics` groups
* Resource nodes: discoverable and activatable via admin commands
* Server-level recipes with structured input/output lists: each recipe defines catalogue items + quantities consumed and produced
* Business inventory: manufacturing businesses track stock as `(business_id, catalogue_id, quantity)`; businesses reference exactly one recipe via `businesses.recipe_id`
* Admin recipe commands: create/edit/delete recipes; add and remove catalogue-linked inputs and outputs at runtime
* Admin tooling expansion: resource nodes, recipes, inputs/outputs, and location policies manageable at runtime
* `LocationPolicy` domain model and repository for per-location governance rules; default open policies seeded for every location on `/admin setup`
* Catalogue-unified goods model: all physical goods (raw materials and finished goods) live in the catalogue
* Work command: Extract (resource node → inventory), Process (recipe inputs → outputs), Haul (move excess inventory to demand locations), Restock (replenish business inventory from player stock)
* Logistics: unit garrison assignment, garrison viewing, maintenance payment, and business-to-business resource transport (start/complete)
* Faction system: create, join, leave, and inspect factions; faction membership integrated into player profiles
* Full economy commands: buy business stocks, pay dividends, take/repay loans, exchange currencies
* Seed data completeness: both Halo and Star Wars themes produce a fully playable environment on `/admin setup`
* Event-driven economy infrastructure: `last_updated_at` and `server_id` columns added to all time-sensitive models (`Loan`, `PlayerStock`, `BusinessResource`, `ResourceNode`, `PlayerUnit`, `Transport`); `EconomyTickService` scaffold in place

### Planned

#### Event-Driven Tick Integration
* Wire `EconomyTickService` into relevant commands so effects (loan interest, dividend accrual, unit maintenance, resource node production) are resolved lazily on each player interaction without requiring admin triggers
* `EconomyTickService` must be idempotent — if called twice within the same second it must not double-apply

#### Supply Chain Gameplay
* Players buy and sell raw materials and finished goods at businesses
* Smuggling routes as an illegal/high-risk variant of transport with risk calculated from origin and destination location policies
* Production capacity limits and throughput bottlenecks at manufacturing businesses

#### Location Ownership and Governance
* Locations owned by a faction leader or a player owner
* Owners create and update `LocationPolicy` records for their location: tax rates, trade tariffs, import/export restrictions, local interest rate modifier
* Policies affect businesses operating at the location (income modifiers, available resources)
* Ownership transferable through purchase, conquest, or faction takeover

#### Expanded Faction System
* Faction-owned locations and resources
* Faction treasury and shared economy
* Faction wars and territory control

#### Stock Market Simulation
* Dynamic stock prices driven by business performance and player trading volume
* Market events and volatility

## Notes
This project is actively evolving. Systems are built incrementally with a focus on modularity and long-term extensibility.
