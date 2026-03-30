from attr import dataclass

from domain import User, GuildConfig
from domain import UserNotFoundException, OnCooldownException
from infrastructure import UserRepository
from application.helpers.ensure_user import ensure_guild_and_user
import random
import datetime

@dataclass
class WorkCommandRequest:
    guild_id: int
    user: User

@dataclass
class WorkCommandResponse:
    success: bool
    guild_config: GuildConfig
    user: User
    amount: int

class WorkCommand:

    def __init__(self, request: WorkCommandRequest):
        self.request = request
        return
    
    def _timestamp_to_string(self, timestamp: int) -> str:
        dt = datetime.datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def execute(self) -> WorkCommandResponse:

        guild_config, user = ensure_guild_and_user(self.request.guild_id, self.request.user)

        if user.last_work:
            time_since_last_work = int(datetime.datetime.now().timestamp())- int(user.last_work)
            if time_since_last_work < guild_config.work_cooldown:
                remaining_cooldown = guild_config.work_cooldown - time_since_last_work
                raise OnCooldownException(f"You are on cooldown. Please wait {self._timestamp_to_string(remaining_cooldown)} before working again.")

        # Calculate random pay amount
        amount = random.randint(guild_config.work_min_pay, guild_config.work_max_pay)

        # Validate sufficient funds
        user.cash_balance = int(user.cash_balance) + amount
        user.last_work = datetime.datetime.now().timestamp()

        success = UserRepository().update(user)

        updated_user = UserRepository().get_by_id(user.guild_id, user.user_id)
        if updated_user is None:
            raise UserNotFoundException(f"User with ID {user.user_id} not found in guild {user.guild_id}.")

        return WorkCommandResponse(success=success, guild_config=guild_config, user=updated_user, amount=amount)
