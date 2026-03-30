class Transaction:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}
        self.transaction_id: int|None = kwargs.get('transaction_id')
        self.player_id: int|None = kwargs.get('player_id')
        self.type: str|None = kwargs.get('type')
        self.currency_id: int|None = kwargs.get('currency_id')
        self.amount: int = kwargs.get('amount', 0)
        self.reference_id: int|None = kwargs.get('reference_id')
        self.created_at: str|None = kwargs.get('created_at')

    def to_dict(self):
        return {
            'transaction_id': self.transaction_id,
            'player_id': self.player_id,
            'type': self.type,
            'currency_id': self.currency_id,
            'amount': self.amount,
            'reference_id': self.reference_id,
            'created_at': self.created_at
        }