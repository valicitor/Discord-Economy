class LocationPolicy:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}
        self.policy_id: int | None = kwargs.get('policy_id')
        self.location_id: int | None = kwargs.get('location_id')
        self.tax_rate: float = float(kwargs.get('tax_rate', 0.0))
        self.trade_tariff: float = float(kwargs.get('trade_tariff', 0.0))
        self.import_restricted: bool = bool(kwargs.get('import_restricted', False))
        self.export_restricted: bool = bool(kwargs.get('export_restricted', False))
        self.interest_rate_modifier: float = float(kwargs.get('interest_rate_modifier', 1.0))
        self.smuggling_risk_modifier: float = float(kwargs.get('smuggling_risk_modifier', 1.0))

    def to_dict(self):
        return {
            'policy_id': self.policy_id,
            'location_id': self.location_id,
            'tax_rate': self.tax_rate,
            'trade_tariff': self.trade_tariff,
            'import_restricted': int(self.import_restricted),
            'export_restricted': int(self.export_restricted),
            'interest_rate_modifier': self.interest_rate_modifier,
            'smuggling_risk_modifier': self.smuggling_risk_modifier,
        }
