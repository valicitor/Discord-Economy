from attr import dataclass

from domain import Catalogue
from infrastructure import CatalogueRepository, ServerRepository

from application import DiscordGuild

@dataclass
class SearchCatalogueQueryRequest:
    guild: DiscordGuild
    search: str
    limit: int = 25

@dataclass
class SearchCatalogueQueryResponse:
    success: bool
    results: list[Catalogue]

class SearchCatalogueQuery:

    def __init__(self, request: SearchCatalogueQueryRequest):
        self.request = request

    async def execute(self) -> SearchCatalogueQueryResponse:
        server_repo = await ServerRepository().get_instance()
        catalogue_repo = await CatalogueRepository().get_instance()

        server = await server_repo.get_by_guild_id(self.request.guild.guild_id)
        if server is None:
            return SearchCatalogueQueryResponse(success=True, results=[])

        results = await catalogue_repo.search_by_name(self.request.search, server.server_id, ['active'], self.request.limit)
        return SearchCatalogueQueryResponse(success=True, results=results)
