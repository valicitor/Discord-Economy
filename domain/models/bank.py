class Bank:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}

        self.bank_id: int|None = kwargs.get('bank_id')
        self.guild_id: int|None = kwargs.get('guild_id')
        self.name: str|None = kwargs.get('name')
        self.interest_rate: float = kwargs.get('interest_rate', 0.0)
        self.max_accounts: int = kwargs.get('max_accounts', 0)

    def to_dict(self):
        return {
            'bank_id': self.bank_id,
            'guild_id': self.guild_id,
            'name': self.name,
            'interest_rate': self.interest_rate,
            'max_accounts': self.max_accounts
        }