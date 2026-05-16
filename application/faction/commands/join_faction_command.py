from attr import dataclass

from infrastructure import FactionRepository, FactionMemberRepository
from application import DiscordGuild, DiscordUser, ServerConfig, PlayerProfile
from application.services.helpers import Helpers
from domain import Faction, FactionMember, InvalidDataException, RecordNotFoundException, CreateFailedException

@dataclass
class JoinFactionCommandRequest:
    guild: DiscordGuild
    user: DiscordUser
    faction_name: str

@dataclass
class JoinFactionCommandResponse:
    success: bool
    server_config: ServerConfig
    player: PlayerProfile
    faction: Faction

class JoinFactionCommand:

    def __init__(self, request: JoinFactionCommandRequest):
        self.request = request

    async def execute(self) -> JoinFactionCommandResponse:
        self.faction_repository = await FactionRepository().get_instance()
        self.faction_member_repository = await FactionMemberRepository().get_instance()

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)
        player_profile = await Helpers.get_player_profile(self.request.guild.guild_id, self.request.user.user_id)

        if await self.faction_member_repository.exists_by_player_id(player_profile.player.player_id):
            raise InvalidDataException("You are already a member of a faction. Leave it before joining another.")

        faction = await self.faction_repository.get_by_name(self.request.faction_name, server_config.server.server_id)
        if not faction:
            raise RecordNotFoundException(f"Faction '{self.request.faction_name}' not found.")

        member = FactionMember(faction_id=faction.faction_id, player_id=player_profile.player.player_id, role='member')
        member_id = await self.faction_member_repository.insert(member)
        if not member_id:
            raise CreateFailedException("Failed to join faction. Please try again.")

        return JoinFactionCommandResponse(success=True, server_config=server_config, player=player_profile, faction=faction)
