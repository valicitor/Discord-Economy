class Player:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}
        self.player_id: int|None = kwargs.get('player_id')
        self.discord_id: int|None = kwargs.get('discord_id')
        self.discord_guild_id: int|None = kwargs.get('discord_guild_id')
        self.server_id: int|None = kwargs.get('server_id')
        self.rank: int|None = kwargs.get('rank', None)
        self.username: str|None = kwargs.get('username')
        self.avatar: str|None = kwargs.get('avatar')
        self.name: str|None = kwargs.get('name')
        self.race: str|None = kwargs.get('race')
        self.backstory: str|None = kwargs.get('backstory')
        self.x: str|None = kwargs.get('x')
        self.y: str|None = kwargs.get('y')
        self.created_at: str|None = kwargs.get('created_at')

    def to_dict(self):
        return {
            'player_id': self.player_id,
            'discord_id': self.discord_id,
            'discord_guild_id': self.discord_guild_id,
            'server_id': self.server_id,
            'rank': self.rank,
            'username': self.username,
            'avatar': self.avatar,
            'name': self.name,
            'race': self.race,
            'backstory': self.backstory,
            'x': self.x,
            'y': self.y,
            'created_at': self.created_at
        }