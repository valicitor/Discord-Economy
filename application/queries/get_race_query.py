from attr import dataclass
import ast

from domain import Race, RaceStat, Keyword
from domain import RecordNotFoundException
from infrastructure import RaceRepository, RaceStatRepository, KeywordRepository

from application import DiscordGuild, ServerConfig
from application.helpers.ensure_user import ensure_guild

@dataclass
class GetRaceQueryRequest:
    guild: DiscordGuild
    name: str

@dataclass
class GetRaceQueryResponse:
    success: bool
    server_config: ServerConfig
    race: Race
    stats: list[RaceStat]
    keywords: list[Keyword]

class GetRaceQuery:

    def __init__(self, request: GetRaceQueryRequest):
        self.request = request
        return

    async def execute(self) -> GetRaceQueryResponse:
        server_config = await ensure_guild(self.request.guild)

        race = await RaceRepository().get_by_name(self.request.name, server_config.server.server_id)
        if not race:
            raise RecordNotFoundException(f"Race with name '{self.request.name}' not found in guild '{self.request.guild.guild_id}'")
        
        stats = await RaceStatRepository().get_all(race.race_id)

        # Convert metadata string to dictionary using ast.literal_eval
        keywords = ast.literal_eval(race.metadata).get("keywords", [])
        found_keywords = []
        for keyword in keywords:
            keyword_record = await KeywordRepository().get_by_name(keyword, server_config.server.server_id)
            if keyword_record:
                found_keywords.append(keyword_record)

        return GetRaceQueryResponse(success=True, server_config=server_config, race=race, stats=stats, keywords=found_keywords)