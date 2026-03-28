class User:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}

        self.user_id = kwargs.get('user_id')
        self.guild_id = kwargs.get('guild_id')
        self.username = kwargs.get('username')
        self.avatar = kwargs.get('avatar')
        self.cash_balance = kwargs.get('cash_balance', 0)
        self.bank_balance = kwargs.get('bank_balance', 0)
        self.rank = kwargs.get('rank', 999)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'guild_id': self.guild_id,
            'username': self.username,
            'avatar': self.avatar,
            'cash_balance': self.cash_balance,
            'bank_balance': self.bank_balance,
            'rank': self.rank
        }