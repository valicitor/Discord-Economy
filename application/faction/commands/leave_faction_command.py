from attr import dataclass

from infrastructure import FactionRepository, FactionMemberRepository
from application import DiscordGuild, DiscordUser, ServerConfig, PlayerProfile
from application.services.helpers import Helpers
from domain import Faction, InvalidDataException, RecordNotFoundException

@dataclass
class LeaveFactionCommandRequest:
    guild: DiscordGuild
    user: DiscordUser

@dataclass
class LeaveFactionCommandResponse:
    success: bool
    server_config: ServerConfig
    player: PlayerProfile
    faction: Faction

class LeaveFactionCommand:

    def __init__(self, request: LeaveFactionCommandRequest):
        self.request = request

    async def execute(self) -> LeaveFactionCommandResponse:
        self.faction_repository = await FactionRepository().get_instance()
        self.faction_member_repository = await FactionMemberRepository().get_instance()

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)
        player_profile = await Helpers.get_player_profile(self.request.guild.guild_id, self.request.user.user_id)

        membership = await self.faction_member_repository.get_by_player_id(player_profile.player.player_id)
        if not membership:
            raise RecordNotFoundException("You are not a member of any faction.")

        if membership.role == 'owner':
            raise InvalidDataException("You cannot leave a faction you own. Disband it instead.")

        faction = await self.faction_repository.get_by_id(membership.faction_id)

        removed = await self.faction_member_repository.delete_by_player_id(player_profile.player.player_id)
        if not removed:
            raise RecordNotFoundException("Failed to remove faction membership. Please try again.")

        return LeaveFactionCommandResponse(success=True, server_config=server_config, player=player_profile, faction=faction)
