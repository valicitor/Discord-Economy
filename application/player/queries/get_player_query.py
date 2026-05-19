import asyncio

from attr import dataclass

from domain import RecordNotFoundException
from infrastructure import (
    PlayerRepository, 
    PlayerBalanceRepository, 
    PlayerActionRepository, 
    PlayerInventoryRepository,
    PlayerUnitRepository,
    BankAccountRepository, 
    FactionRepository, 
    FactionMemberRepository
)
from application import (
    PlayerProfile, 
    PlayerFaction,
    PlayerBalancesCollection, 
    PlayerBankAccountsCollection, 
    PlayerInventoryCollection, 
    PlayerUnitCollection, 
    PlayerActionsCollection
)

@dataclass
class GetPlayerQueryRequest:
    discord_guild_id: int
    discord_user_id: int

@dataclass
class GetPlayerQueryResponse:
    success: bool
    player: PlayerProfile

class GetPlayerQuery:

    def __init__(self, request: GetPlayerQueryRequest):
        self.request = request
        return

    async def execute(self) -> GetPlayerQueryResponse:
        (
            player_repo,
            player_balance_repo,
            bank_account_repo,
            faction_member_repo,
            faction_repo,
            player_action_repo,
            player_inventory_repo,
            player_units_repo,
        ) = await asyncio.gather(
            PlayerRepository().get_instance(),
            PlayerBalanceRepository().get_instance(),
            BankAccountRepository().get_instance(),
            FactionMemberRepository().get_instance(),
            FactionRepository().get_instance(),
            PlayerActionRepository().get_instance(),
            PlayerInventoryRepository().get_instance(),
            PlayerUnitRepository().get_instance(),
        )

        player_exists = await player_repo.exists_by_discord_id(self.request.discord_user_id, self.request.discord_guild_id)
        if not player_exists:
            raise RecordNotFoundException(f"User with ID {self.request.discord_user_id} not found in guild {self.request.discord_guild_id}.")
        
        player = await player_repo.get_by_discord_id(self.request.discord_user_id)
        if player is None:
            raise RecordNotFoundException(f"User with ID {self.request.discord_user_id} not found in guild {self.request.discord_guild_id}.")

        faction_member = await faction_member_repo.get_by_player_id(player.player_id)
        faction = await faction_repo.get_by_id(faction_member.faction_id) if faction_member else None
        balances = await player_balance_repo.get_all(player_id=player.player_id)
        bank_accounts = await bank_account_repo.get_all(player_id=player.player_id)
        actions = await player_action_repo.get_all_by_player_id(player_id=player.player_id)
        inventory = await player_inventory_repo.get_all_by_player_id(player_id=player.player_id)
        units = await player_units_repo.get_all_by_player_id(player_id=player.player_id)

        return GetPlayerQueryResponse(
            success=True, 
            player=PlayerProfile(
                player=player, 
                faction=PlayerFaction(
                    faction.faction_id, 
                    faction.name, 
                    faction.description, 
                    faction.color
                ) if faction else None, 
                balances=PlayerBalancesCollection(balances), 
                bank_accounts=PlayerBankAccountsCollection(bank_accounts),
                inventory=PlayerInventoryCollection(inventory),
                units=PlayerUnitCollection(units),
                actions=PlayerActionsCollection(actions)
            )
        )
