from attr import dataclass
import ast

from domain import Catalogue, Keyword
from domain import RecordNotFoundException
from infrastructure import CatalogueRepository, KeywordRepository

from application import DiscordGuild, ServerConfig
from application.helpers.ensure_user import ensure_guild

@dataclass
class GetCatalogueQueryRequest:
    guild: DiscordGuild
    name: str

@dataclass
class GetCatalogueQueryResponse:
    success: bool
    server_config: ServerConfig
    catalogue_item: Catalogue
    keywords: list[Keyword]

class GetCatalogueQuery:

    def __init__(self, request: GetCatalogueQueryRequest):
        self.request = request
        return

    async def execute(self) -> GetCatalogueQueryResponse:
        self.catalogue_repository = await CatalogueRepository().get_instance()
        self.keyword_repository = await KeywordRepository().get_instance()

        server_config = await ensure_guild(self.request.guild)

        catalogue = await self.catalogue_repository.get_by_name(self.request.name, server_config.server.server_id)
        if not catalogue:
            raise RecordNotFoundException(f"Catalogue item with name '{self.request.name}' not found in guild '{self.request.guild.guild_id}'")

        # Convert metadata string to dictionary using ast.literal_eval
        keywords = ast.literal_eval(catalogue.metadata).get("keywords", [])
        found_keywords = []
        for keyword in keywords:
            keyword_record = await self.keyword_repository.get_by_name(keyword, server_config.server.server_id)
            if keyword_record:
                found_keywords.append(keyword_record)

        return GetCatalogueQueryResponse(success=True, server_config=server_config, catalogue_item=catalogue, keywords=found_keywords)