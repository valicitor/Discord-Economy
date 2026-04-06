from attr import dataclass

from infrastructure import  PlayerBalanceRepository, ServerSettingRepository
from application.helpers.ensure_user import ensure_guild_and_users

from application import DiscordGuild, DiscordUser, ServerConfig, PlayerProfile

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
        server_config, [player_profile, target_player_profile] = await ensure_guild_and_users(self.request.guild, [self.request.user, self.request.target])

        _, default_currency = server_config.server_settings.get_by_key("default_currency_id")

        i, balance = player_profile.balances.get_by_currency_id(int(default_currency.value))
        j, target_balance = target_player_profile.balances.get_by_currency_id(int(default_currency.value))

        balance.balance = int(balance.balance) - self.request.amount
        if balance.balance < 0:
            raise InsufficientFundsException("You do not have enough funds to complete this withdrawal.")
        
        balance_success = await PlayerBalanceRepository().update(balance)
        if not balance_success:
            raise UpdateFailedException("Failed to update player balance. Please try again.")
        balance = await PlayerBalanceRepository().get_by_id(balance.balance_id)

        target_balance.balance = int(target_balance.balance) + self.request.amount
        target_balance_success = await PlayerBalanceRepository().update(target_balance)
        if not target_balance_success:
            raise UpdateFailedException("Failed to update target player balance. Please try again.")
        target_balance = await PlayerBalanceRepository().get_by_id(target_balance.balance_id)

        player_profile.balances[i] = balance
        target_player_profile.balances[j] = target_balance

        return PayCommandResponse(
            success=balance_success and target_balance_success, 
            server_config=server_config, 
            player=player_profile, 
            target_player=target_player_profile, 
            amount=self.request.amount
        )
