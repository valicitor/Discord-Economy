from attr import dataclass

from infrastructure import FactionRepository, FactionMemberRepository, PlayerRepository
from application import DiscordGuild, ServerConfig
from application.services.helpers import Helpers
from domain import Faction, FactionMember, Player, RecordNotFoundException

@dataclass
class GetFactionQueryRequest:
    guild: DiscordGuild
    faction_name: str | None = None
    faction_id: int | None = None

@dataclass
class GetFactionQueryResponse:
    success: bool
    server_config: ServerConfig
    faction: Faction
    members: list[tuple[FactionMember, Player]]

class GetFactionQuery:

    def __init__(self, request: GetFactionQueryRequest):
        self.request = request

    async def execute(self) -> GetFactionQueryResponse:
        self.faction_repository = await FactionRepository().get_instance()
        self.faction_member_repository = await FactionMemberRepository().get_instance()
        self.player_repository = await PlayerRepository().get_instance()

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)

        faction = None
        if self.request.faction_id is not None:
            faction = await self.faction_repository.get_by_id(self.request.faction_id)
        elif self.request.faction_name is not None:
            faction = await self.faction_repository.get_by_name(self.request.faction_name, server_config.server.server_id)

        if not faction:
            raise RecordNotFoundException("Faction not found.")

        raw_members = await self.faction_member_repository.get_all(faction.faction_id)
        members = []
        for m in raw_members:
            player = await self.player_repository.get_by_id(m.player_id)
            if player:
                members.append((m, player))

        return GetFactionQueryResponse(success=True, server_config=server_config, faction=faction, members=members)
