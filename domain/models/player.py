class Player:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}
        self.player_id: int|None = kwargs.get('player_id')
        self.discord_id: int|None = kwargs.get('discord_id')
        self.discord_guild_id: int|None = kwargs.get('discord_guild_id')
        self.server_id: int|None = kwargs.get('server_id')
        self.username: str|None = kwargs.get('username')
        self.avatar: str|None = kwargs.get('avatar')
        self.created_at: str|None = kwargs.get('created_at')

    def to_dict(self):
        return {
            'player_id': self.player_id,
            'discord_id': self.discord_id,
            'discord_guild_id': self.discord_guild_id,
            'server_id': self.server_id,
            'username': self.username,
            'avatar': self.avatar,
            'created_at': self.created_at
        }