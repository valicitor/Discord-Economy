from attr import dataclass

from infrastructure import  PlayerBalanceRepository
from application import DiscordGuild, DiscordUser, ServerConfig, PlayerProfile
from application.helpers.helpers import Helpers
from domain import UpdateFailedException, InsufficientFundsException

@dataclass
class PayCommandRequest:
    guild: DiscordGuild
    user: DiscordUser
    target: DiscordUser
    amount: int

@dataclass
class PayCommandResponse:
    success: bool
    server_config: ServerConfig
    player: PlayerProfile
    target_player: PlayerProfile
    amount: int

class PayCommand:

    def __init__(self, request: PayCommandRequest):
        self.request = request

        return

    async def execute(self) -> PayCommandResponse:
        self.player_balance_repository = await PlayerBalanceRepository().get_instance()
    
        server_config = await Helpers.get_server_config(self.request.guild.guild_id)
        player_profile = await Helpers.get_player_profile(self.request.guild.guild_id, self.request.user.user_id)
        target_player_profile = await Helpers.get_player_profile(self.request.guild.guild_id, self.request.target.user_id)

        async with self.player_balance_repository.transaction():
            _, default_currency = server_config.server_settings.get_by_key("default_currency_id")

            i, balance = player_profile.balances.get_by_currency_id(int(default_currency.value))
            j, target_balance = target_player_profile.balances.get_by_currency_id(int(default_currency.value))

            balance.balance = int(balance.balance) - self.request.amount
            if balance.balance < 0:
                raise InsufficientFundsException("You do not have enough funds to complete this withdrawal.")
            
            balance_success = await self.player_balance_repository.update(balance)
            if not balance_success:
                raise UpdateFailedException("Failed to update player balance. Please try again.")
            balance = await self.player_balance_repository.get_by_id(balance.balance_id)

            target_balance.balance = int(target_balance.balance) + self.request.amount
            target_balance_success = await self.player_balance_repository.update(target_balance)
            if not target_balance_success:
                raise UpdateFailedException("Failed to update target player balance. Please try again.")
            target_balance = await self.player_balance_repository.get_by_id(target_balance.balance_id)

            player_profile.balances[i] = balance
            target_player_profile.balances[j] = target_balance

        return PayCommandResponse(
            success=balance_success and target_balance_success, 
            server_config=server_config, 
            player=player_profile, 
            target_player=target_player_profile, 
            amount=self.request.amount
        )
