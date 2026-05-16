from attr import dataclass

from infrastructure import BankRepository
from application import DiscordGuild, ServerConfig
from application.services.helpers import Helpers
from domain import Bank, CreateFailedException, DuplicateRecordException

@dataclass
class CreateBankCommandRequest:
    guild: DiscordGuild
    name: str
    interest_rate: float
    x: int
    y: int
    range: int | None = None
    max_accounts: int | None = None

@dataclass
class CreateBankCommandResponse:
    success: bool
    server_config: ServerConfig
    bank: Bank

class CreateBankCommand:

    def __init__(self, request: CreateBankCommandRequest):
        self.request = request

    async def execute(self) -> CreateBankCommandResponse:
        self.bank_repository = await BankRepository().get_instance()

        server_config = await Helpers.get_server_config(self.request.guild.guild_id)

        existing = await self.bank_repository.get_by_name(self.request.name, server_config.server.server_id)
        if existing:
            raise DuplicateRecordException(f"A bank named '{self.request.name}' already exists.")

        new_bank = Bank(
            server_id=server_config.server.server_id,
            name=self.request.name,
            interest_rate=self.request.interest_rate,
            x=self.request.x,
            y=self.request.y,
            range=self.request.range,
            max_accounts=self.request.max_accounts,
        )
        bank_id = await self.bank_repository.insert(new_bank)
        if not bank_id:
            raise CreateFailedException("Failed to create bank.")

        new_bank.bank_id = bank_id
        return CreateBankCommandResponse(success=True, server_config=server_config, bank=new_bank)
