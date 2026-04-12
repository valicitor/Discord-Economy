from domain import (
    Player, 
    PlayerBalance,
    Server, 
    ServerSetting,
    Currency, 
    Bank,
    BankAccount,
    Faction,
    FactionMember
)
from domain import RecordNotFoundException, CreateFailedException, SeederErrorException
from infrastructure import (
    PlayerRepository, 
    PlayerBalanceRepository,
    ServerRepository, 
    ServerSettingRepository,
    CurrencyRepository,
    BankRepository,
    BankAccountRepository,
    FactionRepository,
    FactionMemberRepository,
    PlayerActionRepository
)
from infrastructure import (
    PointOfInterestSeeder,
    LocationsSeeder,
    RacesSeeder,
    RaceStatsSeeder,
    EquipmentsSeeder,
    EquipmentStatsSeeder,
    UnitsSeeder,
    UnitStatsSeeder,
    VehiclesSeeder,
    VehicleStatsSeeder,
    BusinessesSeeder,
    ActionsSeeder,
    KeywordsSeeder
)
from application import (
    DiscordGuild, 
    DiscordUser, 
    ServerConfig, 
    ServerSettingsCollection, 
    PlayerProfile, 
    PlayerFaction, 
    PlayerBalancesCollection, 
    PlayerBankAccountsCollection,
    PlayerActionsCollection
)

async def ensure_guild(discord_guild: DiscordGuild) -> ServerConfig:
    """Ensure a guild exists in the database, creating a config if necessary."""

    server_repo = await ServerRepository().get_instance()
    server_setting_repo = await ServerSettingRepository().get_instance()
    currency_repo = await CurrencyRepository().get_instance()
    faction_repo = await FactionRepository().get_instance()
    bank_repo = await BankRepository().get_instance()

    create_new_server = False

    async with server_repo.transaction():
        create_new_server = not await server_repo.exists_by_guild_id(discord_guild.guild_id)
        if create_new_server:
            try:
                new_server = Server(guild_id=discord_guild.guild_id, name=discord_guild.name)
                server_id = await server_repo.insert(new_server)
                if not server_id:
                    raise CreateFailedException(f"Failed to create server for guild ID {discord_guild.guild_id}.")

                new_currency = Currency(server_id=server_id, name="Cash", emoji="💰", symbol="$")
                currency_id = await currency_repo.insert(new_currency)
                if not currency_id:
                    raise CreateFailedException(f"Failed to create currency for guild ID {discord_guild.guild_id}.")
                
                new_faction = Faction(server_id=server_id, name="Unaligned", description="A neutral faction for locations and players.", color="#FFFFFF")
                faction_id = await faction_repo.insert(new_faction)
                if not faction_id:
                    raise CreateFailedException(f"Failed to create default faction for guild ID {discord_guild.guild_id}.")

                new_bank = Bank(server_id=server_id, poi_id=None, name="Bank", interest_rate=0.01, max_accounts=None, range=None)
                bank_id = await bank_repo.insert(new_bank)
                if not bank_id:
                    raise CreateFailedException(f"Failed to create bank for guild ID {discord_guild.guild_id}.")

                new_server_setting = ServerSetting(server_id=server_id, key="default_currency_id", value=str(currency_id))
                setting_id = await server_setting_repo.insert(new_server_setting)
                if not setting_id:
                    raise CreateFailedException(f"Failed to create default currency setting for guild ID {discord_guild.guild_id}.")

                new_server_setting = ServerSetting(server_id=server_id, key="default_bank_id", value=str(bank_id))
                setting_id = await server_setting_repo.insert(new_server_setting)
                if not setting_id:
                    raise CreateFailedException(f"Failed to create default bank setting for guild ID {discord_guild.guild_id}.")
                
                new_server_setting = ServerSetting(server_id=server_id, key="default_faction_id", value=str(faction_id))
                setting_id = await server_setting_repo.insert(new_server_setting)
                if not setting_id:
                    raise CreateFailedException(f"Failed to create default faction setting for guild ID {discord_guild.guild_id}.")
                
            except Exception as e:
                raise CreateFailedException(f"Failed to to initialize server data for guild ID {discord_guild.guild_id}: {str(e)}")

    # Don't wrap in a transaction since seeders may create their own transactions
    if create_new_server:
        try:
            businesses_seeder = BusinessesSeeder()
            result = await businesses_seeder.seed(server_id=server_id)
            if not result.status == "completed":
                raise SeederErrorException(f"Failed to seed businesses for guild ID {discord_guild.guild_id}.")
            
            actions_seeder = ActionsSeeder()
            result = await actions_seeder.seed(server_id=server_id)
            if not result.status == "completed":
                raise SeederErrorException(f"Failed to seed actions for guild ID {discord_guild.guild_id}.")

            point_of_interest_seeder = PointOfInterestSeeder()
            result = await point_of_interest_seeder.seed(server_id=server_id)
            if not result.status == "completed":
                raise SeederErrorException(f"Failed to seed point of interest for guild ID {discord_guild.guild_id}.")
            
            locations_seeder = LocationsSeeder()
            result = await locations_seeder.seed(server_id=server_id)
            if not result.status == "completed":
                raise SeederErrorException(f"Failed to seed locations for guild ID {discord_guild.guild_id}.")

            equipment_seeder = EquipmentsSeeder()
            result = await equipment_seeder.seed(server_id=server_id)
            if not result.status == "completed":
                raise SeederErrorException(f"Failed to seed equipments for guild ID {discord_guild.guild_id}.")
            
            equipment_stat_seeder = EquipmentStatsSeeder()
            result = await equipment_stat_seeder.seed(server_id=server_id)
            if not result.status == "completed":
                raise SeederErrorException(f"Failed to seed equipment stats for guild ID {discord_guild.guild_id}.")

            race_seeder = RacesSeeder()
            result = await race_seeder.seed(server_id=server_id)
            if not result.status == "completed":
                raise SeederErrorException(f"Failed to seed races for guild ID {discord_guild.guild_id}.")
            
            race_stat_seeder = RaceStatsSeeder()
            result = await race_stat_seeder.seed(server_id=server_id)
            if not result.status == "completed":
                raise SeederErrorException(f"Failed to seed race stats for guild ID {discord_guild.guild_id}.")

            unit_seeder = UnitsSeeder()
            result = await unit_seeder.seed(server_id=server_id)
            if not result.status == "completed":
                raise SeederErrorException(f"Failed to seed units for guild ID {discord_guild.guild_id}.")
            
            unit_stat_seeder = UnitStatsSeeder()
            result = await unit_stat_seeder.seed(server_id=server_id)
            if not result.status == "completed":
                raise SeederErrorException(f"Failed to seed unit stats for guild ID {discord_guild.guild_id}.")
            
            vehicle_seeder = VehiclesSeeder()
            result = await vehicle_seeder.seed(server_id=server_id)
            if not result.status == "completed":
                raise SeederErrorException(f"Failed to seed vehicles for guild ID {discord_guild.guild_id}.")
            
            vehicle_stat_seeder = VehicleStatsSeeder()
            result = await vehicle_stat_seeder.seed(server_id=server_id)
            if not result.status == "completed":
                raise SeederErrorException(f"Failed to seed vehicle stats for guild ID {discord_guild.guild_id}.")
            
            keyword_seeder = KeywordsSeeder()
            result = await keyword_seeder.seed(server_id=server_id)
            if not result.status == "completed":
                raise SeederErrorException(f"Failed to seed keywords for guild ID {discord_guild.guild_id}.")
            
        except Exception as e:
            raise SeederErrorException(f"Failed to to seed server data for guild ID {discord_guild.guild_id}: {str(e)}")
    
    server = await server_repo.get_by_guild_id(discord_guild.guild_id)
    if server is None:
        raise RecordNotFoundException(f"Failed to ensure guild with ID {discord_guild.guild_id}.")
    
    server_settings = await server_setting_repo.get_all_by_server_id(server.server_id)
    
    return ServerConfig(
        server, 
        ServerSettingsCollection(server_settings)
    )

async def ensure_user(server_config: ServerConfig, discord_user: DiscordUser) -> PlayerProfile:
    """Ensure a user exists in the database, creating an account if necessary."""

    player_repo = await PlayerRepository().get_instance()
    player_balance_repo = await PlayerBalanceRepository().get_instance()
    bank_account_repo = await BankAccountRepository().get_instance()
    faction_member_repo = await FactionMemberRepository().get_instance()

    if not await player_repo.exists_by_discord_id(discord_user.user_id, server_config.server.guild_id):
        try:
            new_player = Player(discord_id=discord_user.user_id, discord_guild_id=server_config.server.guild_id, server_id=server_config.server.server_id, username=discord_user.name, avatar=discord_user.display_avatar)
            player_id = await player_repo.insert(new_player)
            if not player_id:
                raise CreateFailedException(f"Failed to create player for user ID {discord_user.user_id} in guild ID {server_config.server.guild_id}.")

            _, default_currency_id = server_config.server_settings.get_by_key("default_currency_id")
            new_balance = PlayerBalance(player_id=player_id, currency_id=default_currency_id.value, amount=0)
            business_id = await player_balance_repo.insert(new_balance)
            if not business_id:
                raise CreateFailedException(f"Failed to create balance for player ID {player_id}.")
            
            _, default_bank_id = server_config.server_settings.get_by_key("default_bank_id")
            new_bank_account = BankAccount(bank_id=default_bank_id.value, player_id=player_id, balance=0)
            bank_account_id = await bank_account_repo.insert(new_bank_account)
            if not bank_account_id:
                raise CreateFailedException(f"Failed to create bank account for player ID {player_id}.")
        
            _, default_faction_id = server_config.server_settings.get_by_key("default_faction_id")
            new_faction_member = FactionMember(faction_id=default_faction_id.value, player_id=player_id)
            faction_member_id = await faction_member_repo.insert(new_faction_member)
            if not faction_member_id:
                raise CreateFailedException(f"Failed to create faction membership for player ID {player_id}.")
            
        except Exception as e:
            raise CreateFailedException(f"Failed to ensure user with ID {discord_user.user_id} in guild ID {server_config.server.guild_id}: {str(e)}")

    player = await player_repo.get_by_discord_id(discord_user.user_id)
    if player is None:
        raise RecordNotFoundException(f"User with ID {discord_user.user_id} not found in guild {server_config.server.guild_id}.")

    return await get_player_profile(player)

async def get_player_profile(player: Player) -> PlayerProfile:

    player_balance_repo = await PlayerBalanceRepository().get_instance()
    bank_account_repo = await BankAccountRepository().get_instance()
    faction_member_repo = await FactionMemberRepository().get_instance()
    faction_repo = await FactionRepository().get_instance()
    player_action_repo = await PlayerActionRepository().get_instance()

    faction_member = await faction_member_repo.get_by_player_id(player.player_id)
    faction = await faction_repo.get_by_id(faction_member.faction_id) if faction_member else None
    balances = await player_balance_repo.get_all(player_id=player.player_id)
    bank_accounts = await bank_account_repo.get_all(player_id=player.player_id)
    actions = await player_action_repo.get_all_by_player_id(player_id=player.player_id)

    return PlayerProfile(
        player, 
        PlayerFaction(
            faction.faction_id, 
            faction.name, 
            faction.description, 
            faction.color
        ) if faction else None, 
        PlayerBalancesCollection(balances), 
        PlayerBankAccountsCollection(bank_accounts),
        PlayerActionsCollection(actions)
    )

async def ensure_users(server_config: ServerConfig, discord_users: list[DiscordUser] = []) -> list[PlayerProfile]:
    if len(discord_users) == 0:
        return []
    
    profiles = []
    for discord_user in discord_users:
        profiles.append(await ensure_user(server_config, discord_user))
    
    return profiles

async def ensure_guild_and_user(discord_guild: DiscordGuild, discord_user: DiscordUser) -> tuple[ServerConfig, PlayerProfile]:
    server_config = await ensure_guild(discord_guild)
    player_profile = await ensure_user(server_config, discord_user)

    return server_config, player_profile

async def ensure_guild_and_users(discord_guild: DiscordGuild, discord_users: list[DiscordUser]) -> tuple[ServerConfig, list[PlayerProfile]]:
    server_config = await ensure_guild(discord_guild)
    player_profiles = await ensure_users(server_config, discord_users)

    return server_config, player_profiles