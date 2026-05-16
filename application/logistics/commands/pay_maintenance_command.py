import json

from attr import dataclass

from infrastructure import PlayerUnitRepository, PlayerBalanceRepository, CatalogueRepository
from application import DiscordGuild, DiscordUser, ServerConfig, PlayerProfile
from application.services.helpers import Helpers
from domain import InsufficientFundsException, UpdateFailedException

@dataclass
class PayMaintenanceCommandRequest:
    guild: DiscordGuild
    user: DiscordUser

@dataclass
class PayMaintenanceCommandResponse:
    success: bool
    server_config: ServerConfig
    player: PlayerProfile
    total_cost: int

class PayMaintenanceCommand:

    def __init__(self, request: PayMaintenanceCommandRequest):
        self.request = request

    async def execute(self) -> PayMaintenanceCommandResponse:
        self.player_unit_repository = await PlayerUnitRepository().get_instance()
        self.player_balance_repository = await PlayerBalanceRepository().get_instance()
        self.catalogue_repository = await CatalogueRepository().get_instance()

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)
        player_profile = await Helpers.get_player_profile(self.request.guild.guild_id, self.request.user.user_id)

        units = await self.player_unit_repository.get_all_by_player_id(player_profile.player.player_id)

        total_cost = 0
        for unit in units:
            catalogue_item = await self.catalogue_repository.get_by_name(unit.name, server_config.server.server_id)
            if not catalogue_item:
                continue
            metadata = catalogue_item.metadata
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except (json.JSONDecodeError, TypeError):
                    metadata = {}
            maintenance_cost = (metadata or {}).get("maintenance_cost", 0)
            total_cost += int(maintenance_cost) * unit.quantity

        if total_cost == 0:
            return PayMaintenanceCommandResponse(success=True, server_config=server_config, player=player_profile, total_cost=0)

        async with self.player_balance_repository.transaction():
            _, default_currency = server_config.server_settings.get_by_key("default_currency_id")
            i, balance = player_profile.balances.get_by_currency_id(int(default_currency.value))

            balance.balance = int(balance.balance) - total_cost
            if balance.balance < 0:
                raise InsufficientFundsException("You do not have enough funds to pay unit maintenance.")

            success = await self.player_balance_repository.update(balance)
            if not success:
                raise UpdateFailedException("Failed to deduct maintenance cost. Please try again.")

            balance = await self.player_balance_repository.get_by_id(balance.balance_id)
            player_profile.balances[i] = balance

        return PayMaintenanceCommandResponse(success=True, server_config=server_config, player=player_profile, total_cost=total_cost)
