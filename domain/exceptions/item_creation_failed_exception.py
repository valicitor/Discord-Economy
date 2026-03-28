class ItemCreationFailedException(Exception):
    def __init__(self, message="Item creation failed."):
        self.message = message
        super().__init__(self.message)