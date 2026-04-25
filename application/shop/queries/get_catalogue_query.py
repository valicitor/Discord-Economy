import json

from attr import dataclass

from domain import Catalogue, Keyword
from domain import RecordNotFoundException, InvalidDataException
from infrastructure import CatalogueRepository, KeywordRepository

from application import DiscordGuild, ServerConfig
from application.helpers.helpers import Helpers

@dataclass
class GetCatalogueQueryRequest:
    guild: DiscordGuild
    name: str

@dataclass
class GetCatalogueQueryResponse:
    success: bool
    server_config: ServerConfig
    catalogue_item: Catalogue
    related_items: list[Catalogue]
    keywords: list[Keyword]

class GetCatalogueQuery:

    def __init__(self, request: GetCatalogueQueryRequest):
        self.request = request
        return

    async def execute(self) -> GetCatalogueQueryResponse:
        self.catalogue_repository = await CatalogueRepository().get_instance()
        self.keyword_repository = await KeywordRepository().get_instance()

        server_config = await Helpers.ensure_guild(self.request.guild)

        catalogue_item = await self.catalogue_repository.get_by_name(self.request.name, server_config.server.server_id)
        related_items = []
        if not catalogue_item:
            raise RecordNotFoundException(f"Catalogue item with name '{self.request.name}' not found in guild '{self.request.guild.guild_id}'")
    
        metadata = json.loads(catalogue_item.metadata)
        keywords = metadata.get("keywords", [])
        if not isinstance(keywords, list):
            raise InvalidDataException("Catalogue item metadata is not valid.")

        if catalogue_item.type == "Unit":
            starting_gear = metadata.get("starting_gear", {})
            if not isinstance(starting_gear, dict):
                raise InvalidDataException("Catalogue item metadata is not valid.")
            
            related_catalogue_items = list(starting_gear.values())
            for item_name in related_catalogue_items:
                related_item = await self.catalogue_repository.get_by_name(item_name, server_config.server.server_id)
                if related_item:
                    related_items.append(related_item)
                    keywords.extend(json.loads(related_item.metadata).get("keywords", []))
        
        found_keywords = []
        for keyword in keywords:
            keyword_record = await self.keyword_repository.get_by_name(keyword, server_config.server.server_id)
            if keyword_record:
                found_keywords.append(keyword_record)

        return GetCatalogueQueryResponse(success=True, server_config=server_config, catalogue_item=catalogue_item, related_items=related_items, keywords=found_keywords)
