import json
import os
from config import BASE_DIR

from domain import Business, Action
from infrastructure import BusinessRepository, ActionRepository

class BusinessesSeeder:
    def __init__(self, server_id: int|None = None):
        self.server_id = server_id

    def Seed(self, seed_file: str) -> bool:
        if not seed_file:
            seed_file = os.path.join(BASE_DIR, "infrastructure", "seed", "data", "businesses_seed.json")

        with open(seed_file, "r") as f:
            data = json.load(f)

        business_data = data["businesses"]

        existing = BusinessRepository().get_all(self.server_id)
        if existing:
            return False

        has_failures = False
        for b in business_data["data"]:
            business = Business(data=b)
            business.server_id = self.server_id
            success, _ = BusinessRepository().add(business)
            if not success:
                has_failures = True

        return has_failures

class ActionsSeeder:
    def __init__(self, server_id: int):
        self.server_id = server_id

    def Seed(self, seed_file: str|None = None) -> bool:
        if not seed_file:
            seed_file = os.path.join(BASE_DIR, "infrastructure", "seed", "data", "businesses_seed.json")

        with open(seed_file, "r") as f:
            data = json.load(f)

        action_data = data["actions"]

        has_failures = False
        for action in action_data["data"]:
            business = BusinessRepository().get_by_name(action["business_name"], self.server_id)
            if not business:
                continue  # or raise error

            action_obj = Action(data=action)
            action_obj.business_id = business.business_id

            success, _ = ActionRepository().add(action_obj)
            if not success:
                has_failures = True

        return has_failures