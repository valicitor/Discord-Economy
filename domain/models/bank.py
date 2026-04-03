class Bank:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}

        self.bank_id: int|None = kwargs.get('bank_id')
        self.server_id: int|None = kwargs.get('server_id')
        self.poi_id: int|None = kwargs.get('poi_id')
        self.name: str|None = kwargs.get('name')
        self.interest_rate: float = kwargs.get('interest_rate', 0.0)
        self.max_accounts: int = kwargs.get('max_accounts', 0)
        self.range: int|None = kwargs.get('range')

    def to_dict(self):
        return {
            'bank_id': self.bank_id,
            'server_id': self.server_id,
            'poi_id': self.poi_id,
            'name': self.name,
            'interest_rate': self.interest_rate,
            'max_accounts': self.max_accounts,
            'range': self.range
        }