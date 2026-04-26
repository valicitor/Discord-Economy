from domain import (
    Player, 
    PlayerBalance,
    PlayerInventory,
    PlayerAction,
    PlayerUnit,
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
    
class PlayerInventoryCollection(BaseCollection):
    def __init__(self, items: list[PlayerInventory]):
        super().__init__(items)

    def get_by_item_id(self, item_id: int) -> tuple[int, PlayerInventory|None]:
        return next(((idx, obj) for idx, obj in enumerate(self._items) if obj.item_id == item_id), (None, None))

class PlayerUnitCollection(BaseCollection):
    def __init__(self, items: list[PlayerUnit]):
        super().__init__(items)

    def get_by_item_id(self, unit_id: int) -> tuple[int, PlayerUnit|None]:
        return next(((idx, obj) for idx, obj in enumerate(self._items) if obj.unit_id == unit_id), (None, None))

class PlayerBankAccountsCollection(BaseCollection):
    def __init__(self, items: list[BankAccount]):
        super().__init__(items)

    def get_by_bank_id(self, bank_id: str) -> tuple[int, BankAccount|None]:
        return next(((idx, obj) for idx, obj in enumerate(self._items) if obj.bank_id == bank_id), (None, None))
    
    def total_bank_balance(self) -> int:
        return sum(bank_account.balance for bank_account in self._items)

class PlayerActionsCollection(BaseCollection):
    def __init__(self, items: list[PlayerAction]):
        super().__init__(items)

    def get_by_action_type(self, action_type: str) -> tuple[int, PlayerAction|None]:
        return next(((idx, obj) for idx, obj in enumerate(self._items) if obj.type == action_type), (None, None))
    
    def total_actions(self) -> int:
        return len(self._items)

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
    inventory: PlayerInventoryCollection
    units: PlayerUnitCollection
    actions: PlayerActionsCollection