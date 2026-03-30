class Server:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}

        self.server_id: int|None = kwargs.get('server_id')
        self.guild_id: int|None = kwargs.get('guild_id')
        self.name: str|None = kwargs.get('name')
        self.created_at: str|None = kwargs.get('created_at')

    def to_dict(self):
        return {
            'server_id': self.server_id,
            'guild_id': self.guild_id,
            'name': self.name,
            'created_at': self.created_at
        }