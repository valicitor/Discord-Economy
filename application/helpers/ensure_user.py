from domain import User, GuildConfig
from domain import GuildNotFoundException, UserNotFoundException
from infrastructure import UserRepository, GuildConfigRepository

def ensure_guild(guild_id: int):
    """Ensure a guild exists in the database, creating a config if necessary."""

    if not GuildConfigRepository().exists(guild_id):
        new_guild_config = GuildConfig(guild_id=guild_id, starting_balance=0, currency_symbol='$', currency_emoji='')
        GuildConfigRepository().add(new_guild_config)

def ensure_user(guild_config: GuildConfig, user: User):
    """Ensure a user exists in the database, creating an account if necessary."""
    if not UserRepository().exists(user.user_id, guild_config.guild_id):
        new_user = User(user_id=user.user_id, guild_id=guild_config.guild_id, username=user.username, avatar=user.avatar, cash_balance=guild_config.starting_balance, bank_balance=0)
        UserRepository().add(new_user)

def ensure_users(guild_config: GuildConfig, users: list[User] = []):
    if len(users) == 0:
        return None
    
    for user in users:
        ensure_user(guild_config, user)

def ensure_guild_and_user(guild_id: int, user: User) -> tuple[GuildConfig, User]:
    """Ensure the guild and user exist, returning the saved objects."""
    ensure_guild(guild_id)
    guild_config = GuildConfigRepository().get_by_id(guild_id)
    if guild_config is None:
        raise GuildNotFoundException(f"Failed to ensure guild with ID {guild_id}.")

    ensure_user(guild_config, user)
    user_record = UserRepository().get_by_id(user.guild_id, user.user_id)
    if user_record is None:
        raise UserNotFoundException(f"User with ID {user.user_id} not found in guild {user.guild_id}.")

    return guild_config, user_record

def ensure_guild_and_users(guild_id: int, users: list[User]) -> tuple[GuildConfig, list[User]]:
    """Ensure the guild and users exist, returning the saved objects."""
    ensure_guild(guild_id)
    guild_config = GuildConfigRepository().get_by_id(guild_id)
    if guild_config is None:
        raise GuildNotFoundException(f"Failed to ensure guild with ID {guild_id}.")

    ensure_users(guild_config, users)
    user_records = []
    for user in users:
        user_record = UserRepository().get_by_id(user.guild_id, user.user_id)
        if user_record is None:
            raise UserNotFoundException(f"User with ID {user.user_id} not found in guild {user.guild_id}.")
        user_records.append(user_record)

    return guild_config, user_records