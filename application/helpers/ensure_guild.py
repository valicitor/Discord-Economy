from infrastructure import ServerConfigRepository

async def ensure_guild(guild_id: int) -> None:
    """Ensure a guild exists in the database, creating a config if necessary."""
    server_config_repository = ServerConfigRepository()

    if not await server_config_repository.exists(guild_id):
        entity = {
            'id': guild_id,
            'starting_balance': 0,
            'currency_symbol': '$',
            'currency_emoji': ''
        }
        await server_config_repository.add(entity)