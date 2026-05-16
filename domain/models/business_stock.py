class BusinessStock:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}
        self.stock_id: int|None = kwargs.get('stock_id')
        self.business_id: int|None = kwargs.get('business_id')
        self.market_points: int = kwargs.get('market_points', 100)
        self.base_price: int = kwargs.get('base_price', 100)
        self.dividend_rate: float = kwargs.get('dividend_rate', 0.05)

    @property
    def current_price(self) -> int:
        return max(1, int(self.base_price * (self.market_points / 100)))

    def to_dict(self):
        return {
            'stock_id': self.stock_id,
            'business_id': self.business_id,
            'market_points': self.market_points,
            'base_price': self.base_price,
            'dividend_rate': self.dividend_rate,
        }
