import discord

from infrastructure import UserRepository, ServerConfigRepository

async def _ensure_guild(guild_id: int) -> dict|None:
    """Ensure a guild exists in the database, creating a config if necessary."""
    server_config_repository = ServerConfigRepository()

    if not await server_config_repository.exists(guild_id):
        entity = {
            'guild_id': guild_id,
            'starting_balance': 0,
            'currency_symbol': '$',
            'currency_emoji': ''
        }
        await server_config_repository.add(entity)
    
    return await server_config_repository.get_by_id(guild_id)

async def _ensure_user(guild_id: int, user_id: int, username: str, starting_balance: int) -> dict|None:
    """Ensure a user exists in the database, creating an account if necessary."""
    user_repository = UserRepository()

    if not await user_repository.exists(user_id, guild_id):
        entity = {
            'user_id': user_id,
            'guild_id': guild_id,
            'username': username,
            'balance': starting_balance
        }
        await user_repository.add(entity)
    
    return await user_repository.get_by_id(user_id)

async def ensure_users(guild_id: int, users: list = [], interaction: discord.Interaction|None = None) -> None:
    if len(users) == 0:
        return None

    guild_rec = await _ensure_guild(guild_id)

    if guild_rec is None:
        if interaction != None and interaction.response.is_done():
            await interaction.response.send_message(f"Please ensure the guild has a configuration and try again.", ephemeral=True)
        return None

    for user in users:
        member_rec = await _ensure_user(guild_id, user['user_id'], user['username'], guild_rec['starting_balance'])
    
        if member_rec is None:
            if interaction != None and interaction.response.is_done():
                await interaction.response.send_message(f"Please ensure the recipient has an account and try again.", ephemeral=True)
            return None
    