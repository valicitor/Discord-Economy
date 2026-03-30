class PlayerBalance:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}
        self.balance_id: int|None = kwargs.get('balance_id')
        self.player_id: int|None = kwargs.get('player_id')
        self.currency_id: int|None = kwargs.get('currency_id')
        self.balance: int = kwargs.get('balance', 0)

    def to_dict(self):
        return {
            'balance_id': self.balance_id,
            'player_id': self.player_id,
            'currency_id': self.currency_id,
            'balance': self.balance
        }