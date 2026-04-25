from attr import dataclass

from domain import RecordNotFoundException
from infrastructure import PlayerRepository, PlayerBalanceRepository, PlayerActionRepository, BankAccountRepository, FactionRepository, FactionMemberRepository
from application import PlayerProfile, PlayerBalancesCollection, PlayerBankAccountsCollection, PlayerInventoryCollection, PlayerActionsCollection, PlayerFaction

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
        player_repo = await PlayerRepository().get_instance()
        player_balance_repo = await PlayerBalanceRepository().get_instance()
        bank_account_repo = await BankAccountRepository().get_instance()
        faction_member_repo = await FactionMemberRepository().get_instance()
        faction_repo = await FactionRepository().get_instance()
        player_action_repo = await PlayerActionRepository().get_instance()

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
        inventory = []

        return GetPlayerQueryResponse(
            success=True, 
            player=PlayerProfile(
                player, 
                PlayerFaction(
                    faction.faction_id, 
                    faction.name, 
                    faction.description, 
                    faction.color
                ) if faction else None, 
                PlayerBalancesCollection(balances), 
                PlayerBankAccountsCollection(bank_accounts),
                PlayerInventoryCollection(inventory),
                PlayerActionsCollection(actions)
            )
        )
