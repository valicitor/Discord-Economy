# Economy Bot

This project is a Discord bot built using Python, designed to support a persistent, multiplayer strategy roleplay within a Discord server. It leverages the Discord API to manage player interactions, automate game systems, and maintain states across sessions. The bot is structured to be modular and extensible, allowing for incremental expansion of gameplay systems and mechanics.

## Design Goals

To create a bot that allows for a rich economy to exist within roleplay, with players able to track their money, grow, invest, take loans, etc. This money can then be used to buy soldiers and gear, pay maintenance costs of standing armies, and use that military power to wage war.

As players expand, maintenance costs will become too high, business interests will affect war efforts, and a natural balance should be achieved. The need for money and growth should drive player actions.

By allowing trading, investing, and other deep economic actions, players who hoard money can have war potential without needing a standing army. This enables weighted political roleplay.

### Custom Economy Bot TODO:

#### Phase 1 Completed Features:
- Balance: Basic currency tracking
- Bank: Bank player balance
- Businesses: Defined businesses with actions to perform for that business
- Work: Player action that is performed against a defined business for pay/currency

#### Phase 2 Completed Features:
- Races: Defined races with stats
- Equipment: Defined equipment with stats
- Units: Defined units that combine race and equipment
- Inventory: Track player inventory and items

#### Phase 2 Features:
- [ ] Shop: Buy/Sell units and equipment

### Phase 3 Features:
- [ ] Player: Players should need to create an account/character before interacting with the economy
- [ ] Admin: Seeding data should be optional, create a /admin seed_data or /setup command
- [ ] Custom Units: Units should have equipment unassignable/assignable to them
- [ ] Player: Players should be able to see thier own profile, create a /profile command

#### Phase 4 Features:
- [ ] Locations: Players, Banks, Businesses, and Shops should have locations and prevent interaction with each other if not within range
- [ ] Businesses: Stocks that go up/down in price based on market points
- [ ] Shop: Players can buy stocks
- [ ] Bank: Players that own stocks are paid dividends
- [ ] Work: Player actions cause business market points to go up/down based on success/fail of actions
- [ ] Bank: Interest rates, loans
- [ ] Units: Maintenance costs taken out of player bank
- [ ] Unit Garrison: Units should be able to be assigned to a location

#### Phase 5 Features:
- [ ] Factions: Players can create/join factions
- [ ] Vehicles: Defined vehicles that require crew and override unit stats
- [ ] Locations: Locations should have exhaustible/discoverable resource nodes
- [ ] Currency: Factions and Locations can use different currencies
- [ ] Exchange: Players can exchange one currency for another based on exchange rate
- [ ] Business: Collective market points at locations/factions affect exchange rates of currencies
- [ ] Resources: Businesses produce resources when player actions are completed
- [ ] Business: Businesses require resources in stock for business actions to be available
- [ ] Transport: Resources produced at businesses at different locations should need transporting

## Getting Started

To set up the bot, follow these steps:
1. Clone the repository.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Configure the bot by editing the `config.py` file.
4. Run the bot using `python main.py`.

# Git Commands:

Check the status of the repository:
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
