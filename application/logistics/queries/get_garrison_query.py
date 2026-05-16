from attr import dataclass

from infrastructure import PlayerUnitRepository, UnitGarrisonRepository, PointOfInterestRepository
from application import DiscordGuild, DiscordUser, ServerConfig, PlayerProfile
from application.services.helpers import Helpers
from domain import PlayerUnit, UnitGarrison, PointOfInterest

@dataclass
class GetGarrisonQueryRequest:
    guild: DiscordGuild
    user: DiscordUser

@dataclass
class GetGarrisonQueryResponse:
    success: bool
    server_config: ServerConfig
    player: PlayerProfile
    garrisons: list[tuple[PlayerUnit, UnitGarrison, PointOfInterest]]

class GetGarrisonQuery:

    def __init__(self, request: GetGarrisonQueryRequest):
        self.request = request

    async def execute(self) -> GetGarrisonQueryResponse:
        self.player_unit_repository = await PlayerUnitRepository().get_instance()
        self.unit_garrison_repository = await UnitGarrisonRepository().get_instance()
        self.poi_repository = await PointOfInterestRepository().get_instance()

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)
        player_profile = await Helpers.get_player_profile(self.request.guild.guild_id, self.request.user.user_id)

        units = await self.player_unit_repository.get_all_by_player_id(player_profile.player.player_id)
        garrisons = []
        for unit in units:
            garrison = await self.unit_garrison_repository.get_by_id(unit.unit_id)
            if garrison:
                poi = await self.poi_repository.get_by_id(garrison.poi_id)
                garrisons.append((unit, garrison, poi))

        return GetGarrisonQueryResponse(success=True, server_config=server_config, player=player_profile, garrisons=garrisons)
