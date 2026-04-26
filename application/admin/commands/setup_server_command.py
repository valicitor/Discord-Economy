from attr import dataclass

from domain import Server, Currency, ServerSetting, Faction, Bank
from domain import CreateFailedException, SeederErrorException, RecordNotFoundException
from infrastructure import ServerRepository, CurrencyRepository, ServerSettingRepository, FactionRepository, BankRepository
from infrastructure import BusinessesSeeder, ActionsSeeder, PointOfInterestSeeder, LocationsSeeder, CatalogueSeeder, KeywordsSeeder, ShopItemsSeeder
from application import DiscordGuild, ServerConfig, ServerSettingsCollection

@dataclass
class SetupServerCommandRequest:
    guild: DiscordGuild
    seed_data: bool = False

@dataclass
class SetupServerCommandResponse:
    success: bool

class SetupServerCommand:

    def __init__(self, request: SetupServerCommandRequest):
        self.request = request
        return

    async def execute(self) -> SetupServerCommandResponse:
        server_repo = await ServerRepository().get_instance()
        server_setting_repo = await ServerSettingRepository().get_instance()
        currency_repo = await CurrencyRepository().get_instance()
        faction_repo = await FactionRepository().get_instance()
        bank_repo = await BankRepository().get_instance()

        create_new_server = False

        async with server_repo.transaction():
            create_new_server = not await server_repo.exists_by_guild_id(self.request.guild.guild_id)
            if create_new_server:
                try:
                    new_server = Server(guild_id=self.request.guild.guild_id, name=self.request.guild.name)
                    server_id = await server_repo.insert(new_server)
                    if not server_id:
                        raise CreateFailedException(f"Failed to create server for guild ID {self.request.guild.guild_id}.")

                    new_currency = Currency(server_id=server_id, name="Cash", emoji="💰", symbol="$")
                    currency_id = await currency_repo.insert(new_currency)
                    if not currency_id:
                        raise CreateFailedException(f"Failed to create currency for guild ID {self.request.guild.guild_id}.")
                    
                    new_faction = Faction(server_id=server_id, name="Unaligned", description="A neutral faction for locations and players.", color="#FFFFFF")
                    faction_id = await faction_repo.insert(new_faction)
                    if not faction_id:
                        raise CreateFailedException(f"Failed to create default faction for guild ID {self.request.guild.guild_id}.")

                    new_bank = Bank(server_id=server_id, name="Bank", interest_rate=0.01, max_accounts=None, x=0, y=0, range=None)
                    bank_id = await bank_repo.insert(new_bank)
                    if not bank_id:
                        raise CreateFailedException(f"Failed to create bank for guild ID {self.request.guild.guild_id}.")

                    new_server_setting = ServerSetting(server_id=server_id, key="default_currency_id", value=str(currency_id))
                    setting_id = await server_setting_repo.insert(new_server_setting)
                    if not setting_id:
                        raise CreateFailedException(f"Failed to create default currency setting for guild ID {self.request.guild.guild_id}.")

                    new_server_setting = ServerSetting(server_id=server_id, key="default_bank_id", value=str(bank_id))
                    setting_id = await server_setting_repo.insert(new_server_setting)
                    if not setting_id:
                        raise CreateFailedException(f"Failed to create default bank setting for guild ID {self.request.guild.guild_id}.")
                    
                    new_server_setting = ServerSetting(server_id=server_id, key="default_faction_id", value=str(faction_id))
                    setting_id = await server_setting_repo.insert(new_server_setting)
                    if not setting_id:
                        raise CreateFailedException(f"Failed to create default faction setting for guild ID {self.request.guild.guild_id}.")
                    
                except Exception as e:
                    raise CreateFailedException(f"Failed to to initialize server data for guild ID {self.request.guild.guild_id}: {str(e)}")

        # Don't wrap in a transaction since seeders may create their own transactions
        if create_new_server and self.request.seed_data:
            try:
                businesses_seeder = BusinessesSeeder()
                result = await businesses_seeder.seed(server_id=server_id)
                if not result.status == "completed":
                    raise SeederErrorException(f"Failed to seed businesses for guild ID {self.request.guild.guild_id}.")
                
                actions_seeder = ActionsSeeder()
                result = await actions_seeder.seed(server_id=server_id)
                if not result.status == "completed":
                    raise SeederErrorException(f"Failed to seed actions for guild ID {self.request.guild.guild_id}.")

                point_of_interest_seeder = PointOfInterestSeeder()
                result = await point_of_interest_seeder.seed(server_id=server_id)
                if not result.status == "completed":
                    raise SeederErrorException(f"Failed to seed point of interest for guild ID {self.request.guild.guild_id}.")
                
                locations_seeder = LocationsSeeder()
                result = await locations_seeder.seed(server_id=server_id)
                if not result.status == "completed":
                    raise SeederErrorException(f"Failed to seed locations for guild ID {self.request.guild.guild_id}.")

                catalogue_seeder = CatalogueSeeder()
                result = await catalogue_seeder.seed(server_id=server_id)
                if not result.status == "completed":
                    raise SeederErrorException(f"Failed to seed catalogue items for guild ID {self.request.guild.guild_id}.")
                
                keyword_seeder = KeywordsSeeder()
                result = await keyword_seeder.seed(server_id=server_id)
                if not result.status == "completed":
                    raise SeederErrorException(f"Failed to seed keywords for guild ID {self.request.guild.guild_id}.")

                items_seeder = ShopItemsSeeder()
                result = await items_seeder.seed(server_id=server_id)
                if not result.status == "completed":
                    raise SeederErrorException(f"Failed to seed shop items for guild ID {self.request.guild.guild_id}.")
                
            except Exception as e:
                raise SeederErrorException(f"Failed to to seed server data for guild ID {self.request.guild.guild_id}: {str(e)}")

        return SetupServerCommandResponse(success=create_new_server)
