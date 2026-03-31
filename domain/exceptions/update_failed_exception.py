class UpdateFailedException(Exception):
    def __init__(self, message="failed to update record."):
        self.message = message
        super().__init__(self.message)