from application import (
    DiscordGuild, 
    DiscordUser, 
    ServerConfig,
    PlayerProfile,
)
from application import SetupServerCommand, SetupServerCommandRequest
from application import SetupPlayerCommand, SetupPlayerCommandRequest
from application import GetPlayerQuery, GetPlayerQueryRequest
from application import GetServerQuery, GetServerQueryRequest

class Helpers:
    @staticmethod
    def format_countdown(remaining_seconds: int) -> str:
        hours = remaining_seconds // 3600
        minutes = (remaining_seconds % 3600) // 60
        seconds = remaining_seconds % 60

        formatted_hours = f"{hours}h " if hours > 0 else ""
        formatted_minutes = f"{minutes}m " if minutes > 0 else ""
        formatted_seconds = f"{seconds}s"
        countdown = f"{formatted_hours}{formatted_minutes}{formatted_seconds}"

        return countdown
    
    @staticmethod
    def format_cash_amount(cash_amount: int) -> str:
        if cash_amount >= 1_000_000_000:
            return f"{cash_amount / 1_000_000_000:.0f}B"
        elif cash_amount >= 1_000_000:
            return f"{cash_amount / 1_000_000:.0f}M"
        elif cash_amount >= 100_000:
            return f"{cash_amount / 1_000:.0f}K"
        else:
            return f"{cash_amount:,}"
    
    @staticmethod
    async def get_player_profile(discord_guild_id: int, discord_user_id: int) -> PlayerProfile:
        request = GetPlayerQueryRequest(discord_guild_id=discord_guild_id, discord_user_id=discord_user_id)
        response = await GetPlayerQuery(request).execute()
        return response.player
    
    @staticmethod
    async def get_server_config(discord_guild_id: int) -> ServerConfig:
        request = GetServerQueryRequest(discord_guild_id=discord_guild_id)
        response = await GetServerQuery(request).execute()
        return response.server_config
    
    
    @staticmethod
    async def ensure_user(server_config: ServerConfig, discord_user: DiscordUser) -> PlayerProfile:
        request = SetupPlayerCommandRequest(server_config=server_config, discord_user=discord_user, name="Default", race="Human", backstory="None", x=0, y=0)
        await SetupPlayerCommand(request).execute()

        return await Helpers.get_player_profile(discord_guild_id=server_config.server.guild_id, discord_user_id=discord_user.user_id)
    
    @staticmethod
    async def ensure_guild(discord_guild: DiscordGuild) -> ServerConfig:
        request = SetupServerCommandRequest(guild=discord_guild, seed_data=True)
        await SetupServerCommand(request).execute()

        return await Helpers.get_server_config(discord_guild_id=discord_guild.guild_id)


    @staticmethod
    async def ensure_guild_and_user(discord_guild: DiscordGuild, discord_user: DiscordUser) -> tuple[ServerConfig, PlayerProfile]:
        server_config = await Helpers.ensure_guild(discord_guild)
        player_profile = await Helpers.ensure_user(server_config, discord_user)

        return server_config, player_profile

    @staticmethod
    async def ensure_users(server_config: ServerConfig, discord_users: list[DiscordUser] = []) -> list[PlayerProfile]:
        if len(discord_users) == 0:
            return []
        
        player_profiles = []
        for discord_user in discord_users:
            player_profile = await Helpers.ensure_user(server_config, discord_user)
            player_profiles.append(player_profile)
        
        return player_profiles

    @staticmethod
    async def ensure_guild_and_users(discord_guild: DiscordGuild, discord_users: list[DiscordUser]) -> tuple[ServerConfig, list[PlayerProfile]]:
        server_config = await Helpers.ensure_guild(discord_guild)
        player_profiles = await Helpers.ensure_users(server_config, discord_users)

        return server_config, player_profiles