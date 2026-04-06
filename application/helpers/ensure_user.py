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
from domain import RecordNotFoundException, CreateFailedException
from infrastructure import (
    BaseRepository,
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

    if not await ServerRepository().exists_by_guild_id(discord_guild.guild_id):
        try:
            await ServerRepository().begin_transaction()

            new_server = Server(guild_id=discord_guild.guild_id, name=discord_guild.name)
            (server_success, server_id) = await ServerRepository().add(new_server)
            if not server_success:
                raise CreateFailedException(f"Failed to create server for guild ID {discord_guild.guild_id}.")

            new_currency = Currency(server_id=server_id, name="Cash", emoji="💰", symbol="$")
            (currency_success, currency_id) = await CurrencyRepository().add(new_currency)
            if not currency_success:
                raise CreateFailedException(f"Failed to create currency for guild ID {discord_guild.guild_id}.")
            
            new_faction = Faction(server_id=server_id, name="Unaligned", description="A neutral faction for locations and players.", color="#FFFFFF")
            (faction_success, faction_id) = await FactionRepository().add(new_faction)
            if not faction_success:
                raise CreateFailedException(f"Failed to create default faction for guild ID {discord_guild.guild_id}.")

            new_bank = Bank(server_id=server_id, poi_id=None, name="Bank", interest_rate=0.01, max_accounts=None, range=None)
            (bank_success, bank_id) = await BankRepository().add(new_bank)
            if not bank_success:
                raise CreateFailedException(f"Failed to create bank for guild ID {discord_guild.guild_id}.")

            new_server_setting = ServerSetting(server_id=server_id, key="default_currency_id", value=str(currency_id))
            (server_setting_success, setting_id) = await ServerSettingRepository().add(new_server_setting)
            if not server_setting_success:
                raise CreateFailedException(f"Failed to create default currency setting for guild ID {discord_guild.guild_id}.")

            new_server_setting = ServerSetting(server_id=server_id, key="default_bank_id", value=str(bank_id))
            (server_setting_success, setting_id) = await ServerSettingRepository().add(new_server_setting)
            if not server_setting_success:
                raise CreateFailedException(f"Failed to create default bank setting for guild ID {discord_guild.guild_id}.")
            
            new_server_setting = ServerSetting(server_id=server_id, key="default_faction_id", value=str(faction_id))
            (server_setting_success, setting_id) = await ServerSettingRepository().add(new_server_setting)
            if not server_setting_success:
                raise CreateFailedException(f"Failed to create default faction setting for guild ID {discord_guild.guild_id}.")

            await BusinessesSeeder(server_id).Seed()
            await ActionsSeeder(server_id).Seed()

            await PointOfInterestSeeder(server_id).Seed()
            await LocationsSeeder(server_id).Seed()

            await EquipmentsSeeder(server_id).Seed()
            await EquipmentStatsSeeder(server_id).Seed()
            await RacesSeeder(server_id).Seed()
            await RaceStatsSeeder(server_id).Seed()
            await UnitsSeeder(server_id).Seed()
            await UnitStatsSeeder(server_id).Seed()
            await VehiclesSeeder(server_id).Seed()
            await VehicleStatsSeeder(server_id).Seed()
            await KeywordsSeeder(server_id).Seed()

            await ServerRepository().commit_transaction()
        except Exception as e:
            await ServerRepository().rollback_transaction()
            raise CreateFailedException(f"Failed to seed initial data for guild ID {discord_guild.guild_id}: {str(e)}")
    
    server = await ServerRepository().get_by_guild_id(discord_guild.guild_id)
    if server is None:
        raise RecordNotFoundException(f"Failed to ensure guild with ID {discord_guild.guild_id}.")
    
    server_settings = await ServerSettingRepository().get_all_by_server_id(server.server_id)
    
    return ServerConfig(
        server, 
        ServerSettingsCollection(server_settings)
    )

async def ensure_user(server_config: ServerConfig, discord_user: DiscordUser) -> PlayerProfile:
    """Ensure a user exists in the database, creating an account if necessary."""

    if not await PlayerRepository().exists_by_discord_id(discord_user.user_id, server_config.server.guild_id):
        try:
            await PlayerRepository().begin_transaction()

            new_player = Player(discord_id=discord_user.user_id, discord_guild_id=server_config.server.guild_id, server_id=server_config.server.server_id, username=discord_user.name, avatar=discord_user.display_avatar)
            (player_success, player_id) = await PlayerRepository().add(new_player)
            if not player_success:
                raise CreateFailedException(f"Failed to create player for user ID {discord_user.user_id} in guild ID {server_config.server.guild_id}.")

            _, default_currency_id = server_config.server_settings.get_by_key("default_currency_id")
            new_balance = PlayerBalance(player_id=player_id, currency_id=default_currency_id.value, amount=0)
            balance_success, _ = await PlayerBalanceRepository().add(new_balance)
            if not balance_success:
                raise CreateFailedException(f"Failed to create balance for player ID {player_id}.")
            
            _, default_bank_id = server_config.server_settings.get_by_key("default_bank_id")
            new_bank_account = BankAccount(bank_id=default_bank_id.value, player_id=player_id, balance=0)
            bank_account_success, _ = await BankAccountRepository().add(new_bank_account)
            if not bank_account_success:
                raise CreateFailedException(f"Failed to create bank account for player ID {player_id}.")
        
            _, default_faction_id = server_config.server_settings.get_by_key("default_faction_id")
            new_faction_member = FactionMember(faction_id=default_faction_id.value, player_id=player_id)
            faction_member_success, _ = await FactionMemberRepository().add(new_faction_member)
            if not faction_member_success:
                raise CreateFailedException(f"Failed to create faction membership for player ID {player_id}.")
            
            await PlayerRepository().commit_transaction()
        except Exception as e:
            await PlayerRepository().rollback_transaction()
            raise CreateFailedException(f"Failed to ensure user with ID {discord_user.user_id} in guild ID {server_config.server.guild_id}: {str(e)}")

    player = await PlayerRepository().get_by_discord_id(discord_user.user_id)
    if player is None:
        raise RecordNotFoundException(f"User with ID {discord_user.user_id} not found in guild {server_config.server.guild_id}.")

    return get_player_profile(player)

async def get_player_profile(player: Player) -> PlayerProfile:

    faction_member = await FactionMemberRepository().get_by_player_id(player.player_id)
    faction = await FactionRepository().get_by_id(faction_member.faction_id) if faction_member else None
    balances = await PlayerBalanceRepository().get_all(player_id=player.player_id)
    bank_accounts = await BankAccountRepository().get_all(player_id=player.player_id)
    actions = await PlayerActionRepository().get_all_by_player_id(player_id=player.player_id)

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
    server_config = ensure_guild(discord_guild)
    player_profile = await ensure_user(server_config, discord_user)

    return server_config, player_profile

async def ensure_guild_and_users(discord_guild: DiscordGuild, discord_users: list[DiscordUser]) -> tuple[ServerConfig, list[PlayerProfile]]:
    server_config = ensure_guild(discord_guild)
    player_profiles = await ensure_users(server_config, discord_users)

    return server_config, player_profiles