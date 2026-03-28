# Economy Bot

This project is a Discord bot built using Python, designed to support a persistent, multiplayer strategy roleplay within a Discord server. It leverages the Discord API to manage player interactions, automate game systems, and maintain states across sessions. The bot is structured to be modular and extensible, allowing for incremental expansion of gameplay systems and mechanics.

## Design Goals

To create a bot that can allows a rich economy to exist within roleplay, with players able to track their money, grow, invest, take loans, etc. This money can then be used to buy solider and gear, pay maintenance costs of standing armies, and use that military power to wage war.

As Players expand, maintenence costs will become too high, business intrests will affect war efforts, and a natural balance should be achieved, and the need for money and growth should drive player actions. 

Also by allowing trading, investing, and other deep economic actions players that horde money have war potential without needing a standing army, and therefore we allow weighted political RP

### Custom Economy Bot TODO:
#### Core Features:
- [x] Basic currency tracking: Implement a system to track player balances.
- [ ] Basic gambling games: Add simple games like dice rolls or card games for players to gamble currency.
- [x] Basic collect income/bank: Allow players to collect periodic income and deposit/withdraw from a bank.
- [ ] Basic inventory: Track player-owned items.
- [ ] Basic shop store/trading: Enable players to buy/sell items and trade with each other.

#### Advanced Features:
- [ ] Businesses to replace Basic collect: Introduce player-owned businesses that generate income.
- [ ] Player-owned business store fronts: Allow players to set up shops to sell items to others.
- [ ] Inventory categories: Separate inventory into categories like Soldiers, Gear, Vehicles, etc.
- [ ] Maintenance costs: Add upkeep costs for inventory items to limit hoarding.
- [ ] Business locations and planet locations: Tie businesses to specific locations, affecting their performance.
- [ ] Bank interest rates: Introduce interest rates for deposited currency.
- [ ] Business stock market/investing: Allow players to invest in businesses and trade stocks.
- [ ] Loans: Enable players to take loans with interest.

### Core Features Breakdown:

#### Basic Currency Tracking:
- **Commands**:
  - `AddBalanceCommand`: Add currency to a player's balance.
  - `SetBalanceCommand`: Set a player's balance to a specific amount.
  - `PayCommand`: Send money to another player
- **Queries**:
  - `GetUserQuery`: Retrieve a player
  - `GetTopBalancesQuery`: Retrieve a leaderboard of players with the highest balances.

#### Basic Gambling Games:
- **Commands**:
  - `PlaceBetCommand`: Place a bet for a gambling game.
  - `ResolveBetCommand`: Resolve the outcome of a bet and update balances.
- **Queries**:
  - `GetBetHistoryQuery`: Retrieve a player's gambling history.

#### Basic Collect Income/Bank:
- **Commands**:
  - `CollectIncomeCommand`: Allow players to collect periodic income.
  - `DepositBankCommand`: Deposit currency into a player's bank account.
  - `WithdrawBankCommand`: Withdraw currency from a player's bank account.
- **Queries**:
  - `GetBankBalanceQuery`: Retrieve a player's current bank balance.
  - `GetIncomeCooldownQuery`: Check if a player is eligible to collect income.

#### Basic Inventory:
- **Commands**:
  - `AddItemCommand`: Add an item to a player's inventory.
  - `RemoveItemCommand`: Remove an item from a player's inventory.
- **Queries**:
  - `GetInventoryQuery`: Retrieve a player's inventory.
  - `GetItemDetailsQuery`: Retrieve details about a specific item.

#### Basic Shop Store/Trading:
- **Commands**:
  - `BuyItemCommand`: Allow players to purchase items from a shop.
  - `SellItemCommand`: Allow players to sell items to a shop.
  - `TradeItemCommand`: Facilitate item trading between players.
- **Queries**:
  - `GetShopItemsQuery`: Retrieve a list of items available in the shop.
  - `GetTradeHistoryQuery`: Retrieve a player's trading history.

# Git Commands:

Check status of git:
- `git status`

Move to the main branch:
- `git checkout main`

Create and switch to a new branch:
- `git checkout -b <branch-name>` (e.g., `git checkout -b feature/add-tests`)

Merge a branch into main:
- `git merge <branch-name>`

Pull changes from the remote repository:
- `git pull`

Commit changes with a message:
- `git commit -m "<Message>"`

Push changes from local machine to the remote repo:
- `git push`

# Running Bot:

Run the unit tests:
`python -m unittest discover -s tests -p "*.py"`

Run the main application to launch the bot:
`python main.py`

# Setting Up the Environment:
1. Create a virtual environment:
   `python -m venv venv`
2. Activate the virtual environment:
   - Windows: `venv\\Scripts\\Activate.ps1`
   - Mac/Linux: `source venv/bin/activate`
3. Install dependencies:
   `pip install -r requirements.txt`
