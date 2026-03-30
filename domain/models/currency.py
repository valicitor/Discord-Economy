class Currency:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}
        self.currency_id: int|None = kwargs.get('currency_id')
        self.server_id: int|None = kwargs.get('server_id')
        self.name: str|None = kwargs.get('name')
        self.emoji: str|None = kwargs.get('emoji')
        self.symbol: str|None = kwargs.get('symbol')

    def to_dict(self):
        return {
            'currency_id': self.currency_id,
            'server_id': self.server_id,
            'name': self.name,
            'emoji': self.emoji,
            'symbol': self.symbol
        }