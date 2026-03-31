class CreateFailedException(Exception):
    def __init__(self, message="failed to create record."):
        self.message = message
        super().__init__(self.message)