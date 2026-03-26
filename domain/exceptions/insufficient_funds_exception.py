class InsufficientFundsException(Exception):
    def __init__(self, message="Insufficient funds."):
        self.message = message
        super().__init__(self.message)