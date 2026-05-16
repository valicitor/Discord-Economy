from attr import dataclass

from infrastructure import ItemRepository, CatalogueRepository
from application import DiscordGuild, ServerConfig
from application.services.helpers import Helpers
from domain import Item, CreateFailedException, RecordNotFoundException, DuplicateRecordException

@dataclass
class CreateItemCommandRequest:
    guild: DiscordGuild
    catalogue_id: int
    name: str
    price: int
    description: str = ''
    icon: str = ''
    stock: int | None = None
    inventory: bool = True
    usable: bool = True
    sellable: bool = True
    business_id: int | None = None

@dataclass
class CreateItemCommandResponse:
    success: bool
    server_config: ServerConfig
    item: Item

class CreateItemCommand:

    def __init__(self, request: CreateItemCommandRequest):
        self.request = request

    async def execute(self) -> CreateItemCommandResponse:
        self.item_repository = await ItemRepository().get_instance()
        self.catalogue_repository = await CatalogueRepository().get_instance()

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)

        catalogue_item = await self.catalogue_repository.get_by_id(self.request.catalogue_id)
        if not catalogue_item:
            raise RecordNotFoundException(f"Catalogue entry with id '{self.request.catalogue_id}' not found.")

        existing = await self.item_repository.get_by_name(self.request.name)
        if existing and existing.server_id == server_config.server.server_id:
            raise DuplicateRecordException(f"An item named '{self.request.name}' already exists in the shop.")

        new_item = Item(
            server_id=server_config.server.server_id,
            catalogue_id=self.request.catalogue_id,
            name=self.request.name,
            price=self.request.price,
            description=self.request.description,
            icon=self.request.icon,
            stock=self.request.stock,
            inventory=self.request.inventory,
            usable=self.request.usable,
            sellable=self.request.sellable,
            business_id=self.request.business_id,
        )
        item_id = await self.item_repository.insert(new_item)
        if not item_id:
            raise CreateFailedException("Failed to create shop item.")

        new_item.item_id = item_id
        return CreateItemCommandResponse(success=True, server_config=server_config, item=new_item)
