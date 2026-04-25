from attr import dataclass

from domain import Player, PlayerBalance, BankAccount, FactionMember
from domain import CreateFailedException, RecordNotFoundException
from infrastructure import PlayerRepository, PlayerBalanceRepository, PlayerActionRepository, BankAccountRepository, FactionRepository, FactionMemberRepository
from application import DiscordUser, ServerConfig, PlayerProfile, PlayerBalancesCollection, PlayerBankAccountsCollection, PlayerInventoryCollection, PlayerActionsCollection, PlayerFaction

@dataclass
class SetupPlayerCommandRequest:
    server_config: ServerConfig
    discord_user: DiscordUser

@dataclass
class SetupPlayerCommandResponse:
    success: bool

class SetupPlayerCommand:

    def __init__(self, request: SetupPlayerCommandRequest):
        self.request = request
        return

    async def execute(self) -> SetupPlayerCommandResponse:
        player_repo = await PlayerRepository().get_instance()
        player_balance_repo = await PlayerBalanceRepository().get_instance()
        bank_account_repo = await BankAccountRepository().get_instance()
        faction_member_repo = await FactionMemberRepository().get_instance()

        create_new_player = False

        async with player_repo.transaction():
            create_new_player = not await player_repo.exists_by_discord_id(self.request.discord_user.user_id, self.request.server_config.server.guild_id)
            if create_new_player:
                try:
                    new_player = Player(discord_id=self.request.discord_user.user_id, discord_guild_id=self.request.server_config.server.guild_id, server_id=self.request.server_config.server.server_id, username=self.request.discord_user.name, avatar=self.request.discord_user.display_avatar)
                    player_id = await player_repo.insert(new_player)
                    if not player_id:
                        raise CreateFailedException(f"Failed to create player for user ID {self.request.discord_user.user_id} in guild ID {self.request.server_config.server.guild_id}.")

                    _, default_currency_id = self.request.server_config.server_settings.get_by_key("default_currency_id")
                    new_balance = PlayerBalance(player_id=player_id, currency_id=default_currency_id.value, amount=0)
                    business_id = await player_balance_repo.insert(new_balance)
                    if not business_id:
                        raise CreateFailedException(f"Failed to create balance for player ID {player_id}.")
                    
                    _, default_bank_id = self.request.server_config.server_settings.get_by_key("default_bank_id")
                    new_bank_account = BankAccount(bank_id=default_bank_id.value, player_id=player_id, balance=0)
                    bank_account_id = await bank_account_repo.insert(new_bank_account)
                    if not bank_account_id:
                        raise CreateFailedException(f"Failed to create bank account for player ID {player_id}.")
                
                    _, default_faction_id = self.request.server_config.server_settings.get_by_key("default_faction_id")
                    new_faction_member = FactionMember(faction_id=default_faction_id.value, player_id=player_id)
                    faction_member_id = await faction_member_repo.insert(new_faction_member)
                    if not faction_member_id:
                        raise CreateFailedException(f"Failed to create faction membership for player ID {player_id}.")
                    
                except Exception as e:
                    raise CreateFailedException(f"Failed to ensure user with ID {self.request.discord_user.user_id} in guild ID {self.request.server_config.server.guild_id}: {str(e)}")

        return SetupPlayerCommandResponse(success=create_new_player)
