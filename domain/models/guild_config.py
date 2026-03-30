class GuildConfig:
    
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}

        self.guild_id: int|None = kwargs.get('guild_id')
        self.starting_balance: int|None = kwargs.get('starting_balance', 0)
        self.currency_symbol: str|None = kwargs.get('currency_symbol', '$')
        self.currency_emoji: str|None = kwargs.get('currency_emoji', '')

        self.work_cooldown: int|None = kwargs.get('work_cooldown', 3600)
        self.work_min_pay: int|None = kwargs.get('work_min_pay', 100)
        self.work_max_pay: int|None = kwargs.get('work_max_pay', 500)

    def to_dict(self):
        return {
            'guild_id': self.guild_id,
            'starting_balance': self.starting_balance,
            'currency_symbol': self.currency_symbol,
            'currency_emoji': self.currency_emoji,
            
            'work_cooldown': self.work_cooldown,
            'work_min_pay': self.work_min_pay,
            'work_max_pay': self.work_max_pay
        }