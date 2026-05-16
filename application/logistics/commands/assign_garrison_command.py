from attr import dataclass

from infrastructure import PlayerUnitRepository, UnitGarrisonRepository, PointOfInterestRepository
from application import DiscordGuild, DiscordUser, ServerConfig, PlayerProfile
from application.services.helpers import Helpers
from domain import PlayerUnit, UnitGarrison, PointOfInterest, RecordNotFoundException, InvalidDataException, CreateFailedException

@dataclass
class AssignGarrisonCommandRequest:
    guild: DiscordGuild
    user: DiscordUser
    unit_name: str
    poi_name: str

@dataclass
class AssignGarrisonCommandResponse:
    success: bool
    server_config: ServerConfig
    player: PlayerProfile
    garrison: UnitGarrison
    unit: PlayerUnit
    poi: PointOfInterest

class AssignGarrisonCommand:

    def __init__(self, request: AssignGarrisonCommandRequest):
        self.request = request

    async def execute(self) -> AssignGarrisonCommandResponse:
        self.player_unit_repository = await PlayerUnitRepository().get_instance()
        self.unit_garrison_repository = await UnitGarrisonRepository().get_instance()
        self.poi_repository = await PointOfInterestRepository().get_instance()

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)
        player_profile = await Helpers.get_player_profile(self.request.guild.guild_id, self.request.user.user_id)

        unit = await self.player_unit_repository.get_by_name(self.request.unit_name, player_profile.player.player_id)
        if not unit:
            raise RecordNotFoundException(f"Unit '{self.request.unit_name}' not found.")

        poi = await self.poi_repository.get_by_name(self.request.poi_name, server_config.server.server_id)
        if not poi:
            raise RecordNotFoundException(f"Location '{self.request.poi_name}' not found.")

        existing = await self.unit_garrison_repository.get_by_id(unit.unit_id)
        if existing:
            raise InvalidDataException(f"Unit '{self.request.unit_name}' is already garrisoned.")

        garrison = UnitGarrison(unit_id=unit.unit_id, poi_id=poi.poi_id)
        garrison_id = await self.unit_garrison_repository.insert(garrison)
        if not garrison_id:
            raise CreateFailedException("Failed to assign garrison. Please try again.")

        garrison.garrison_id = garrison_id
        return AssignGarrisonCommandResponse(success=True, server_config=server_config, player=player_profile, garrison=garrison, unit=unit, poi=poi)
