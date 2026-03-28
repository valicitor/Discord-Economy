from datetime import datetime

class User:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}

        self.user_id: int|None = kwargs.get('user_id')
        self.guild_id: int|None = kwargs.get('guild_id')
        self.username: str|None = kwargs.get('username')
        self.avatar: str|None = kwargs.get('avatar')
        
        self.cash_balance: int|None = kwargs.get('cash_balance', 0)
        self.bank_balance: int|None = kwargs.get('bank_balance', 0)

        self.last_work: datetime|None = kwargs.get('last_work', 0)

        self.rank: int|None = kwargs.get('rank', 999)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'guild_id': self.guild_id,
            'username': self.username,
            'avatar': self.avatar,

            'cash_balance': self.cash_balance,
            'bank_balance': self.bank_balance,

            'last_work': self.last_work,

            'rank': self.rank
        }