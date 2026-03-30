class Business:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}

        self.business_id: int|None = kwargs.get('business_id')
        self.guild_id: int|None = kwargs.get('guild_id')
        self.owner_id: int|None = kwargs.get('owner_id')
        self.name: str|None = kwargs.get('name')
        self.balance: int = kwargs.get('balance', 0)
        self.type: str|None = kwargs.get('type')

    def to_dict(self):
        return {
            'business_id': self.business_id,
            'guild_id': self.guild_id,
            'owner_id': self.owner_id,
            'name': self.name,
            'balance': self.balance,
            'type': self.type
        }