from domain import User, GuildConfig
from domain import GuildNotFoundException, UserNotFoundException
from infrastructure import UserRepository, GuildConfigRepository

async def _ensure_guild(guild_id: int) -> GuildConfig|None:
    """Ensure a guild exists in the database, creating a config if necessary."""
    guild_config_repository = GuildConfigRepository()

    if not await guild_config_repository.exists(guild_id):
        new_guild_config = GuildConfig(guild_id=guild_id, starting_balance=0, currency_symbol='$', currency_emoji='')
        await guild_config_repository.add(new_guild_config)
    
    return await guild_config_repository.get_by_id(guild_id)

async def _ensure_user(guild_id: int, user_id: int, username: str, starting_balance: int) -> User|None:
    """Ensure a user exists in the database, creating an account if necessary."""
    user_repository = UserRepository()

    if not await user_repository.exists(user_id, guild_id):
        new_user = User(user_id=user_id, guild_id=guild_id, username=username, cash_balance=starting_balance)
        await user_repository.add(new_user)
    
    return await user_repository.get_by_id(user_id)

async def ensure_users(guild_id: int, users: list[User] = []) -> None:
    if len(users) == 0:
        return None

    guild_config = await _ensure_guild(guild_id)

    if guild_config is None:
        raise GuildNotFoundException(f"Failed to ensure guild with ID {guild_id}.");

    for user in users:
        member_rec = await _ensure_user(guild_id, user.user_id, user.username, guild_config.starting_balance)
    
        if member_rec is None:
            raise UserNotFoundException(f"Failed to ensure user {user.user_id} in guild {guild_id}.")
    