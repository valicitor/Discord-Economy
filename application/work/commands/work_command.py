from datetime import datetime, timezone
import random

from attr import dataclass

from infrastructure import PlayerBalanceRepository, PlayerActionRepository, BusinessRepository, ActionRepository
from application.helpers.helpers import Helpers

from application import DiscordGuild, DiscordUser, ServerConfig, PlayerProfile

from domain import PlayerAction, Business, Action, CreateFailedException, UpdateFailedException, OnCooldownException

@dataclass
class WorkCommandRequest:
    guild: DiscordGuild
    user: DiscordUser
    work_type: str

@dataclass
class WorkCommandResponse:
    success: bool
    server_config: ServerConfig
    player: PlayerProfile
    action_success: bool
    business: Business
    action: Action
    wage: int
    fine: int

class WorkCommand:

    def __init__(self, request: WorkCommandRequest):
        self.request = request

        return

    async def execute(self) -> WorkCommandResponse:
        self.player_balance_repository = await PlayerBalanceRepository().get_instance()
        self.player_action_repository = await PlayerActionRepository().get_instance()
        self.business_repository = await BusinessRepository().get_instance()
        self.action_repository = await ActionRepository().get_instance()

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)
        player_profile = await Helpers.get_player_profile(self.request.guild.guild_id, self.request.user.user_id)

        async with self.player_action_repository.transaction():
            last_action = await self.player_action_repository.get_last_action_by_type(self.request.work_type, player_profile.player.player_id)
            if last_action:
                last_used_at = datetime.fromisoformat(last_action.last_used_at)
                if last_used_at.tzinfo is None:  # Assume naive datetime is in UTC
                    last_used_at = last_used_at.replace(tzinfo=timezone.utc)
                cooldown_seconds = last_action.cooldown_seconds
                now_utc = datetime.now(timezone.utc).replace(microsecond=0)
                if (last_used_at is not None) and ((last_used_at.timestamp() + cooldown_seconds) > now_utc.timestamp()):
                    time_remaining_seconds = int((last_used_at.timestamp() + cooldown_seconds) - now_utc.timestamp())
                    raise OnCooldownException(f"You are on cooldown. Please wait {Helpers.format_countdown(time_remaining_seconds)} before working again.")

            businesses = await self.business_repository.get_all_within_range(x=player_profile.player.x, y=player_profile.player.y, server_id=server_config.server.server_id)
            if not businesses:
                return WorkCommandResponse(success=False, server_config=server_config, player=player_profile, action_success=False, business=None, action=None, wage=0, fine=0)
            
            rng_business = businesses[random.randint(0, len(businesses) - 1)]

            actions = await self.action_repository.get_all_by_business_id(action_type=self.request.work_type,business_id=rng_business.business_id)
            if not actions:
                raise UpdateFailedException("No actions found for this business. Please try again later.")
            
            rng_action = actions[random.randint(0, len(actions) - 1)]

            player_action = PlayerAction(
                player_id=player_profile.player.player_id,
                action_id=rng_action.action_id,
                type=rng_action.type,
                cooldown_seconds=rng_action.cooldown_seconds
            )
            success = await self.player_action_repository.insert(player_action)
            if not success:
                raise CreateFailedException("Player action already exists. Please wait before trying again.")

            action_success = random.uniform(0, 1) < rng_action.success_rate
            risk = random.uniform(0, rng_action.risk_rate)
            wage = int(rng_action.base_reward * (1 + risk)) if action_success else 0
            fine = int(rng_action.fine_amount * (1 + risk)) if not action_success else 0

            i, default_currency_id = server_config.server_settings.get_by_key("default_currency_id")
            j, player_balance = player_profile.balances.get_by_currency_id(int(default_currency_id.value))

            player_balance.balance = int(player_balance.balance) + wage - fine

            success = await self.player_balance_repository.update(player_balance=player_balance)
            if not success:
                raise UpdateFailedException("Failed to update player balance. Please try again.")
            
            player_profile.balances[j] = player_balance

        return WorkCommandResponse(success=success, server_config=server_config, player=player_profile, action_success=action_success, business=rng_business, action=rng_action, wage=wage, fine=fine)
