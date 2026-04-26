## Economy Bot
A modular Discord bot built in Python for running a persistent, strategy-driven economy and warfare system inside a Discord server.

Players earn money, invest, build armies, and influence large-scale conflicts through economic and military decisions.

## Core Features
* Persistent player economy (balance, bank, inventory)
* Business system for earning income
* Unit creation using races and equipment
* Shop system for purchasing units and gear
* Player profiles and progression tracking

## Gameplay Overview
* Players earn money through `/work` and business interactions
* Currency can be saved, invested, or spent on military units
* Units require upkeep, forcing economic decisions
* Wealth can be converted into political or military power

The system is designed so:

* expansion increases maintenance pressure
* economic strength can rival military strength
* player interaction drives the balance

## Example Commands
```
/balance        # View your current money
/work           # Earn money from a business
/shop           # View available units and equipment
/profile        # View your character
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

## Project Structure (recommended section once stable)
```
/commands
/events
/models
/services
```

## Roadmap

### Completed
* Currency system
* Banking
* Businesses
* Work system
* Units, races, equipment
* Inventory and shop
* Player profiles

### In Progress
* Selling system
* Custom units

### Planned
* Locations and travel
* Factions
* Stock market and economy simulation
* Loans and interest
* Resource production and logistics
* Multiple currencies and exchange rates

## Notes
This project is actively evolving. Systems are being built incrementally with a focus on modularity and long-term extensibility.