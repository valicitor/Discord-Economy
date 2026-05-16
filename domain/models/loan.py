class Loan:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}
        self.loan_id: int|None = kwargs.get('loan_id')
        self.player_id: int|None = kwargs.get('player_id')
        self.bank_id: int|None = kwargs.get('bank_id')
        self.principal: int = kwargs.get('principal', 0)
        self.interest_rate: float = kwargs.get('interest_rate', 0.1)
        self.balance_remaining: int = kwargs.get('balance_remaining', 0)
        self.status: str = kwargs.get('status', 'active')  # active, repaid, defaulted
        self.created_at: str|None = kwargs.get('created_at')

    def to_dict(self):
        return {
            'loan_id': self.loan_id,
            'player_id': self.player_id,
            'bank_id': self.bank_id,
            'principal': self.principal,
            'interest_rate': self.interest_rate,
            'balance_remaining': self.balance_remaining,
            'status': self.status,
            'created_at': self.created_at,
        }
