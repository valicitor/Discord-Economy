from attr import dataclass

from infrastructure import BankRepository
from application import DiscordGuild, ServerConfig
from application.services.helpers import Helpers
from domain import Bank, UpdateFailedException, RecordNotFoundException

@dataclass
class UpdateBankCommandRequest:
    guild: DiscordGuild
    bank_id: int
    name: str | None = None
    interest_rate: float | None = None
    x: int | None = None
    y: int | None = None
    range: int | None = None
    max_accounts: int | None = None

@dataclass
class UpdateBankCommandResponse:
    success: bool
    server_config: ServerConfig
    bank: Bank

class UpdateBankCommand:

    def __init__(self, request: UpdateBankCommandRequest):
        self.request = request

    async def execute(self) -> UpdateBankCommandResponse:
        self.bank_repository = await BankRepository().get_instance()

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)

        bank = await self.bank_repository.get_by_id(self.request.bank_id)
        if not bank:
            raise RecordNotFoundException(f"Bank with id '{self.request.bank_id}' not found.")

        if self.request.name is not None:
            bank.name = self.request.name
        if self.request.interest_rate is not None:
            bank.interest_rate = self.request.interest_rate
        if self.request.x is not None:
            bank.x = self.request.x
        if self.request.y is not None:
            bank.y = self.request.y
        if self.request.range is not None:
            bank.range = self.request.range
        if self.request.max_accounts is not None:
            bank.max_accounts = self.request.max_accounts

        success = await self.bank_repository.update(bank)
        if not success:
            raise UpdateFailedException("Failed to update bank.")

        return UpdateBankCommandResponse(success=True, server_config=server_config, bank=bank)
