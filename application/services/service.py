class SingletonService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SingletonService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # guard against reinitialization
        if not hasattr(self, "_initialized"):
            self._initialized = True
    
    