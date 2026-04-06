from attr import dataclass
import ast

from domain import Equipment, EquipmentStat, Keyword
from domain import RecordNotFoundException
from infrastructure import EquipmentRepository, EquipmentStatRepository, KeywordRepository

from application import DiscordGuild, ServerConfig
from application.helpers.ensure_user import ensure_guild

@dataclass
class GetEquipmentQueryRequest:
    guild: DiscordGuild
    name: str

@dataclass
class GetEquipmentQueryResponse:
    success: bool
    server_config: ServerConfig
    equipment: Equipment
    stats: list[EquipmentStat]
    keywords: list[Keyword]

class GetEquipmentQuery:

    def __init__(self, request: GetEquipmentQueryRequest):
        self.request = request
        return

    async def execute(self) -> GetEquipmentQueryResponse:
        server_config = await ensure_guild(self.request.guild)

        equipment = await EquipmentRepository().get_by_name(self.request.name, server_config.server.server_id)
        if not equipment:
            raise RecordNotFoundException(f"Equipment with name '{self.request.name}' not found in guild '{self.request.guild.guild_id}'")
        
        stats = await EquipmentStatRepository().get_all(equipment.equipment_id)

        # Convert metadata string to dictionary using ast.literal_eval
        keywords = ast.literal_eval(equipment.metadata).get("keywords", [])
        found_keywords = []
        for keyword in keywords:
            keyword_record = await KeywordRepository().get_by_name(keyword, server_config.server.server_id)
            if keyword_record:
                found_keywords.append(keyword_record)

        return GetEquipmentQueryResponse(success=True, server_config=server_config, equipment=equipment, stats=stats, keywords=found_keywords)