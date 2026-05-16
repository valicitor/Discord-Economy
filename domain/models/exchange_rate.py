class ExchangeRate:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}
        self.rate_id: int|None = kwargs.get('rate_id')
        self.server_id: int|None = kwargs.get('server_id')
        self.from_currency_id: int|None = kwargs.get('from_currency_id')
        self.to_currency_id: int|None = kwargs.get('to_currency_id')
        self.rate: float = kwargs.get('rate', 1.0)

    def to_dict(self):
        return {
            'rate_id': self.rate_id,
            'server_id': self.server_id,
            'from_currency_id': self.from_currency_id,
            'to_currency_id': self.to_currency_id,
            'rate': self.rate,
        }
