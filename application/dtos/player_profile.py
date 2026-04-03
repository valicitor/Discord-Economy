from domain import (
    Player, 
    PlayerBalance,
    BankAccount
)
from application import BaseCollection
from dataclasses import dataclass

class PlayerBalancesCollection(BaseCollection):
    def __init__(self, items: list[PlayerBalance]):
        super().__init__(items)

    def get_by_currency_id(self, currency_id: str) -> tuple[int, PlayerBalance|None]:
        return next(((idx, obj) for idx, obj in enumerate(self._items) if obj.currency_id == currency_id), (None, None))

    def total_balance(self) -> int:
        return sum(balance.balance for balance in self._items)

class PlayerBankAccountsCollection(BaseCollection):
    def __init__(self, items: list[BankAccount]):
        super().__init__(items)

    def get_by_bank_id(self, bank_id: str) -> tuple[int, BankAccount|None]:
        return next(((idx, obj) for idx, obj in enumerate(self._items) if obj.bank_id == bank_id), (None, None))
    
    def total_bank_balance(self) -> int:
        return sum(bank_account.balance for bank_account in self._items)

@dataclass
class PlayerFaction:
    faction_id: int|None
    name: str|None
    description: str|None
    color: str|None

@dataclass
class PlayerProfile:
    player: Player
    faction: PlayerFaction|None
    balances: PlayerBalancesCollection
    bank_accounts: PlayerBankAccountsCollection