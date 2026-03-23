from infrastructure import UserRepository

async def ensure_user(user_id: int, guild_id: int, starting_balance: int) -> None:
    """Ensure a user exists in the database, creating an account if necessary."""
    user_repository = UserRepository()

    if not await user_repository.exists(user_id, guild_id):
        entity = {
            'id': user_id,
            'guild_id': guild_id,
            'balance': starting_balance
        }
        await user_repository.add(entity)