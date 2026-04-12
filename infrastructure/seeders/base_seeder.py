import json
import os
from typing import Any, Dict

from attr import dataclass

from config import BASE_DIR
from domain import SeederErrorException

@dataclass
class SeederResult:
    status: str
    reason: str | None = None
    inserted: int = 0
    failed: int = 0

class BaseSeeder:
    def __init__(self, server_id: int):
        self.server_id = server_id

    def _load_json(self, seed_file: str) -> Dict[str, Any]:
        try:
            with open(seed_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            raise SeederErrorException(f"Seed file not found: {seed_file}")
        except json.JSONDecodeError as e:
            raise SeederErrorException(f"Invalid JSON in {seed_file}: {e}")

    def _resolve_seed_file(self, seed_file: str | None, filename: str) -> str:
        if seed_file:
            return seed_file
        return os.path.join(BASE_DIR, "shared", "assets", "seed_data", filename)