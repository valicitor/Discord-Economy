class RecordNotFoundException(Exception):
    def __init__(self, message="Record not found."):
        self.message = message
        super().__init__(self.message)