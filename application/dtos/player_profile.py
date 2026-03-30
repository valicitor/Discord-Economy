from domain import (
    Player, 
    PlayerBalance,
    BankAccount
)
from dataclasses import dataclass

@dataclass
class PlayerProfile:
    player: Player
    balances: list[PlayerBalance]
    bank_accounts: list[BankAccount]