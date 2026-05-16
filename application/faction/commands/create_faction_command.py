from attr import dataclass

from infrastructure import FactionRepository, FactionMemberRepository
from application import DiscordGuild, DiscordUser, ServerConfig, PlayerProfile
from application.services.helpers import Helpers
from domain import Faction, FactionMember, InvalidDataException, CreateFailedException

@dataclass
class CreateFactionCommandRequest:
    guild: DiscordGuild
    user: DiscordUser
    name: str
    description: str | None
    color: str | None

@dataclass
class CreateFactionCommandResponse:
    success: bool
    server_config: ServerConfig
    player: PlayerProfile
    faction: Faction

class CreateFactionCommand:

    def __init__(self, request: CreateFactionCommandRequest):
        self.request = request

    async def execute(self) -> CreateFactionCommandResponse:
        self.faction_repository = await FactionRepository().get_instance()
        self.faction_member_repository = await FactionMemberRepository().get_instance()

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)
        player_profile = await Helpers.get_player_profile(self.request.guild.guild_id, self.request.user.user_id)

        if await self.faction_repository.exists_by_owner_id(player_profile.player.player_id, server_config.server.server_id):
            raise InvalidDataException("You already own a faction.")

        if await self.faction_member_repository.exists_by_player_id(player_profile.player.player_id):
            raise InvalidDataException("You are already a member of a faction. Leave it before creating a new one.")

        faction = Faction(
            server_id=server_config.server.server_id,
            owner_id=player_profile.player.player_id,
            name=self.request.name,
            description=self.request.description,
            color=self.request.color
        )
        faction_id = await self.faction_repository.insert(faction)
        if not faction_id:
            raise CreateFailedException("Failed to create faction. Please try again.")
        faction.faction_id = faction_id

        member = FactionMember(faction_id=faction_id, player_id=player_profile.player.player_id, role='owner')
        member_id = await self.faction_member_repository.insert(member)
        if not member_id:
            raise CreateFailedException("Failed to add owner as faction member. Please try again.")

        return CreateFactionCommandResponse(success=True, server_config=server_config, player=player_profile, faction=faction)
