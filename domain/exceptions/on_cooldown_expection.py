class OnCooldownException(Exception):
    def __init__(self, message="You are on cooldown. Please wait before you try again."):
        self.message = message
        super().__init__(self.message)