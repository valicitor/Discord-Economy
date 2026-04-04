import json
import os
from config import BASE_DIR

from domain import Keyword
from infrastructure import KeywordRepository

class KeywordsSeeder:
    def __init__(self, server_id: int|None = None):
        self.server_id = server_id

    def Seed(self, seed_file: str|None = None) -> bool:
        if not seed_file:
            seed_file = os.path.join(BASE_DIR, "infrastructure", "seed", "data", "keywords_seed.json")

        with open(seed_file, "r") as f:
            data = json.load(f)

        keyword_data = data["keywords"]

        existing = KeywordRepository().get_all(self.server_id)
        if existing:
            return False

        has_failures = False
        for k in keyword_data["data"]:
            keyword = Keyword(data=k)
            keyword.server_id = self.server_id
            success, _ = KeywordRepository().add(keyword)
            if not success:
                has_failures = True

        return has_failures