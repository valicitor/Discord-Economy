from attr import dataclass

from infrastructure import ItemRepository
from application import DiscordGuild, ServerConfig
from application.services.helpers import Helpers
from domain import Item, UpdateFailedException, RecordNotFoundException

@dataclass
class UpdateItemCommandRequest:
    guild: DiscordGuild
    item_id: int
    name: str | None = None
    price: int | None = None
    description: str | None = None
    icon: str | None = None
    stock: int | None = None
    inventory: bool | None = None
    usable: bool | None = None
    sellable: bool | None = None
    business_id: int | None = None

@dataclass
class UpdateItemCommandResponse:
    success: bool
    server_config: ServerConfig
    item: Item

class UpdateItemCommand:

    def __init__(self, request: UpdateItemCommandRequest):
        self.request = request

    async def execute(self) -> UpdateItemCommandResponse:
        self.item_repository = await ItemRepository().get_instance()

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)

        item = await self.item_repository.get_by_id(self.request.item_id)
        if not item:
            raise RecordNotFoundException(f"Item with id '{self.request.item_id}' not found.")

        if self.request.name is not None:
            item.name = self.request.name
        if self.request.price is not None:
            item.price = self.request.price
        if self.request.description is not None:
            item.description = self.request.description
        if self.request.icon is not None:
            item.icon = self.request.icon
        if self.request.stock is not None:
            item.stock = self.request.stock
        if self.request.inventory is not None:
            item.inventory = self.request.inventory
        if self.request.usable is not None:
            item.usable = self.request.usable
        if self.request.sellable is not None:
            item.sellable = self.request.sellable
        if self.request.business_id is not None:
            item.business_id = self.request.business_id

        success = await self.item_repository.update(item)
        if not success:
            raise UpdateFailedException("Failed to update item.")

        return UpdateItemCommandResponse(success=True, server_config=server_config, item=item)
