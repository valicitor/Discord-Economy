class Action:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}
        self.action_id: int|None = kwargs.get('action_id')
        self.name: str|None = kwargs.get('name')
        self.cooldown_seconds: int = kwargs.get('cooldown_seconds', 86400)
        self.base_reward: int = kwargs.get('base_reward', 0)
        self.reward_currency_id: int|None = kwargs.get('reward_currency_id')
        self.success_rate: float = kwargs.get('success_rate', 1.0)

    def to_dict(self):
        return {
            'action_id': self.action_id,
            'name': self.name,
            'cooldown_seconds': self.cooldown_seconds,
            'base_reward': self.base_reward,
            'reward_currency_id': self.reward_currency_id,
            'success_rate': self.success_rate
        }