class GuildConfig:
    
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}

        self.guild_id = kwargs.get('guild_id')
        self.starting_balance = kwargs.get('starting_balance', 0)
        self.currency_symbol = kwargs.get('currency_symbol', '$')
        self.currency_emoji = kwargs.get('currency_emoji', '')

    def to_dict(self):
        return {
            'guild_id': self.guild_id,
            'starting_balance': self.starting_balance,
            'currency_symbol': self.currency_symbol,
            'currency_emoji': self.currency_emoji
        }