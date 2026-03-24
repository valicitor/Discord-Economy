import discord

from infrastructure import UserRepository, ServerConfigRepository

async def _ensure_guild(guild_id: int, server_config_repository: ServerConfigRepository = ServerConfigRepository()) -> dict|None:
    """Ensure a guild exists in the database, creating a config if necessary."""

    if not await server_config_repository.exists(guild_id):
        entity = {
            'id': guild_id,
            'starting_balance': 0,
            'currency_symbol': '$',
            'currency_emoji': ''
        }
        await server_config_repository.add(entity)
    
    return await server_config_repository.get_by_id(guild_id)

async def _ensure_user(guild_id: int, user_id: int, starting_balance: int, user_repository: UserRepository = UserRepository()) -> dict|None:
    """Ensure a user exists in the database, creating an account if necessary."""

    if not await user_repository.exists(user_id, guild_id):
        entity = {
            'id': user_id,
            'guild_id': guild_id,
            'balance': starting_balance
        }
        await user_repository.add(entity)
    
    return await user_repository.get_by_id(user_id)

async def ensure_user(guild_id: int, user_id: int, user_repository: UserRepository = UserRepository(), server_config_repository: ServerConfigRepository = ServerConfigRepository(), interaction: discord.Interaction|None = None) -> dict|None:
    guild_rec = await _ensure_guild(guild_id, server_config_repository=server_config_repository)
    if guild_rec is None:
        if interaction != None and interaction.response.is_done():
            await interaction.response.send_message(f"Please ensure the guild has a configuration and try again.", ephemeral=True)
        return None

    member_rec = await _ensure_user(guild_id, user_id, guild_rec['starting_balance'], user_repository=user_repository)
    if member_rec is None:
        if interaction != None and interaction.response.is_done():
            await interaction.response.send_message(f"Please ensure the recipient has an account and try again.", ephemeral=True)
        return None

    return member_rec

async def ensure_users(guild_id: int, users: list = [], user_repository = UserRepository(), server_config_repository = ServerConfigRepository(), interaction: discord.Interaction|None = None) -> None:
    if len(users) == 0:
        return None

    guild_rec = await _ensure_guild(guild_id, server_config_repository=server_config_repository)

    if guild_rec is None:
        if interaction != None and interaction.response.is_done():
            await interaction.response.send_message(f"Please ensure the guild has a configuration and try again.", ephemeral=True)
        return None

    for user_id in users:
        member_rec = await _ensure_user(guild_id, user_id, guild_rec['starting_balance'], user_repository=user_repository)
    
        if member_rec is None:
            if interaction != None and interaction.response.is_done():
                await interaction.response.send_message(f"Please ensure the recipient has an account and try again.", ephemeral=True)
            return None
    