import asyncio
import os

from attr import dataclass

from config import BASE_DIR
from domain import Server, Currency, ServerSetting, Faction, Bank
from domain import CreateFailedException, SeederErrorException, RecordNotFoundException
from infrastructure import ServerRepository, CurrencyRepository, ServerSettingRepository, FactionRepository, BankRepository
from infrastructure import BusinessesSeeder, ActionsSeeder, PointOfInterestSeeder, LocationsSeeder, CatalogueSeeder, KeywordsSeeder, ShopItemsSeeder, ResourceNodesSeeder, RecipesSeeder, LocationPoliciesSeeder
from application import DiscordGuild, ServerConfig, ServerSettingsCollection

@dataclass
class SetupServerCommandRequest:
    guild: DiscordGuild
    theme: str = "star_wars"

@dataclass
class SetupServerCommandResponse:
    success: bool

class SetupServerCommand:

    def __init__(self, request: SetupServerCommandRequest):
        self.request = request
        return

    async def execute(self) -> SetupServerCommandResponse:
        (
            server_repo,
            server_setting_repo,
            currency_repo,
            faction_repo,
            bank_repo,
        ) = await asyncio.gather(
            ServerRepository().get_instance(),
            ServerSettingRepository().get_instance(),
            CurrencyRepository().get_instance(),
            FactionRepository().get_instance(),
            BankRepository().get_instance(),
        )

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

                    new_server_setting = ServerSetting(server_id=server_id, key="travel_speed", value="10")
                    setting_id = await server_setting_repo.insert(new_server_setting)
                    if not setting_id:
                        raise CreateFailedException(f"Failed to create travel_speed setting for guild ID {self.request.guild.guild_id}.")

                except Exception as e:
                    raise CreateFailedException(f"Failed to to initialize server data for guild ID {self.request.guild.guild_id}: {str(e)}")

        # Don't wrap in a transaction since seeders may create their own transactions
        if create_new_server and self.request.theme != "none":
            theme_dir = os.path.join(BASE_DIR, "shared", "assets", "seed_data", self.request.theme)

            def seed_path(filename: str) -> str:
                themed = os.path.join(theme_dir, filename)
                return themed if os.path.exists(themed) else None

            try:
                businesses_seeder = BusinessesSeeder()
                result = await businesses_seeder.seed(server_id=server_id, seed_file=seed_path("businesses_seed.json"))
                if not result.status == "completed":
                    raise SeederErrorException(f"Failed to seed businesses for guild ID {self.request.guild.guild_id}.")

                actions_seeder = ActionsSeeder()
                result = await actions_seeder.seed(server_id=server_id, seed_file=seed_path("businesses_seed.json"))
                if not result.status == "completed":
                    raise SeederErrorException(f"Failed to seed actions for guild ID {self.request.guild.guild_id}.")

                point_of_interest_seeder = PointOfInterestSeeder()
                result = await point_of_interest_seeder.seed(server_id=server_id, seed_file=seed_path("point_of_interest_seed.json"))
                if not result.status == "completed":
                    raise SeederErrorException(f"Failed to seed point of interest for guild ID {self.request.guild.guild_id}.")

                locations_seeder = LocationsSeeder()
                result = await locations_seeder.seed(server_id=server_id, seed_file=seed_path("point_of_interest_seed.json"))
                if not result.status == "completed":
                    raise SeederErrorException(f"Failed to seed locations for guild ID {self.request.guild.guild_id}.")

                location_policies_seeder = LocationPoliciesSeeder()
                result = await location_policies_seeder.seed(server_id=server_id)
                if not result.status == "completed":
                    raise SeederErrorException(f"Failed to seed location policies for guild ID {self.request.guild.guild_id}.")

                catalogue_seeder = CatalogueSeeder()
                result = await catalogue_seeder.seed(server_id=server_id, seed_file=seed_path("catalogue_seed.json"))
                if not result.status == "completed":
                    raise SeederErrorException(f"Failed to seed catalogue items for guild ID {self.request.guild.guild_id}.")

                keyword_seeder = KeywordsSeeder()
                result = await keyword_seeder.seed(server_id=server_id, seed_file=seed_path("keywords_seed.json"))
                if not result.status == "completed":
                    raise SeederErrorException(f"Failed to seed keywords for guild ID {self.request.guild.guild_id}.")

                items_seeder = ShopItemsSeeder()
                result = await items_seeder.seed(server_id=server_id, seed_file=seed_path("shop_items_seed.json"))
                if not result.status == "completed":
                    raise SeederErrorException(f"Failed to seed shop items for guild ID {self.request.guild.guild_id}.")

                resource_nodes_seeder = ResourceNodesSeeder()
                result = await resource_nodes_seeder.seed(server_id=server_id, seed_file=seed_path("resource_nodes_seed.json"))
                if not result.status == "completed":
                    raise SeederErrorException(f"Failed to seed resource nodes for guild ID {self.request.guild.guild_id}.")

                recipes_seeder = RecipesSeeder()
                result = await recipes_seeder.seed(server_id=server_id, seed_file=seed_path("recipes_seed.json"))
                if not result.status == "completed":
                    raise SeederErrorException(f"Failed to seed recipes for guild ID {self.request.guild.guild_id}.")

            except Exception as e:
                raise SeederErrorException(f"Failed to to seed server data for guild ID {self.request.guild.guild_id}: {str(e)}")

        return SetupServerCommandResponse(success=create_new_server)
