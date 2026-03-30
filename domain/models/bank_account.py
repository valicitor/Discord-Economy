class BankAccount:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}

        self.account_id: int|None = kwargs.get('account_id')
        self.bank_id: int|None = kwargs.get('bank_id')
        self.guild_id: int|None = kwargs.get('guild_id')
        self.user_id: int|None = kwargs.get('user_id')
        self.balance: int = kwargs.get('balance', 0)
        self.created_at: str|None = kwargs.get('created_at')

    def to_dict(self):
        return {
            'account_id': self.account_id,
            'bank_id': self.bank_id,
            'guild_id': self.guild_id,
            'user_id': self.user_id,
            'balance': self.balance,
            'created_at': self.created_at
        }