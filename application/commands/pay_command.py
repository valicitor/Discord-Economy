from attr import dataclass

from infrastructure import  PlayerBalanceRepository
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

    def execute(self) -> PayCommandResponse:
        server_config, [player_profile, target_player_profile] = ensure_guild_and_users(self.request.guild, [self.request.user, self.request.target])

        default_currency_id = next((obj.value for obj in server_config.server_settings if obj.key == "default_currency_id"), None)

        i, balance = next(((idx, obj) for idx, obj in enumerate(player_profile.balances) if obj.currency_id == int(default_currency_id)), (None, None))
        j, target_balance = next(((idx, obj) for idx, obj in enumerate(target_player_profile.balances) if obj.currency_id == int(default_currency_id)), (None, None))

        balance.balance = int(balance.balance) - self.request.amount
        if balance.balance < 0:
            raise InsufficientFundsException("You do not have enough funds to complete this withdrawal.")
        
        balance_success = PlayerBalanceRepository().update(balance)
        if not balance_success:
            raise UpdateFailedException("Failed to update player balance. Please try again.")
        balance = PlayerBalanceRepository().get_by_id(balance.balance_id)

        target_balance.balance = int(target_balance.balance) + self.request.amount
        target_balance_success = PlayerBalanceRepository().update(target_balance)
        if not target_balance_success:
            raise UpdateFailedException("Failed to update target player balance. Please try again.")
        target_balance = PlayerBalanceRepository().get_by_id(target_balance.balance_id)

        player_profile.balances[i] = balance
        target_player_profile.balances[j] = target_balance

        return PayCommandResponse(
            success=balance_success and target_balance_success, 
            server_config=server_config, 
            player=player_profile, 
            target_player=target_player_profile, 
            amount=self.request.amount
        )
