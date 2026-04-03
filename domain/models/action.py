class Action:
    def __init__(self, data: dict = None, **kwargs):
        if data:
            kwargs = {**data, **kwargs}
        self.action_id: int|None = kwargs.get('action_id')
        self.business_id: int|None = kwargs.get('business_id')
        self.name: str|None = kwargs.get('name')
        self.cooldown_seconds: int = kwargs.get('cooldown_seconds', 86400)
        self.base_reward: int = kwargs.get('base_reward', 0)
        self.success_rate: float = kwargs.get('success_rate', 1.0)
        self.risk_rate: float = kwargs.get('risk_rate', 0.0)
        self.fine_amount: int = kwargs.get('fine_amount', 0)
        self.success_message: str = kwargs.get('success_message', "You successfully completed the action!")
        self.failure_message: str = kwargs.get('failure_message', "You failed to complete the action.")

    def to_dict(self):
        return {
            'action_id': self.action_id,
            'business_id': self.business_id,
            'name': self.name,
            'cooldown_seconds': self.cooldown_seconds,
            'base_reward': self.base_reward,
            'success_rate': self.success_rate,
            'risk_rate': self.risk_rate,
            'fine_amount': self.fine_amount,
            'success_message': self.success_message,
            'failure_message': self.failure_message
        }