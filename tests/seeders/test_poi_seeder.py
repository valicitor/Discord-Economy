import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from infrastructure import (
    ServerRepository,
    ServerSettingRepository,
    CurrencyRepository,
    BankRepository,
    FactionRepository,
    PointOfInterestRepository, 
    PointOfInterestSeeder
)
from application import DiscordGuild
from application.helpers.ensure_user import ensure_guild

class TestPOISeeder(unittest.TestCase):
    def setUp(self):
        self.server_repository = ServerRepository(db_path=":memory:")
        self.server_setting_repository = ServerSettingRepository(db_path=":memory:")
        self.currency_repository = CurrencyRepository(db_path=":memory:")
        self.bank_repository = BankRepository(db_path=":memory:")
        self.faction_repository = FactionRepository(db_path=":memory:")

        self.discord_guild = DiscordGuild(guild_id=12911, name="TestGuild")
        self.server_config = ensure_guild(self.discord_guild)
    
        self.POI_repository = PointOfInterestRepository(seeder=PointOfInterestSeeder(self.server_config.server.server_id), db_path=":memory:")  # Use in-memory database for testing

    def tearDown(self):
        # Remove test database
        self.faction_repository.delete_all(self.server_config.server.server_id)
        self.bank_repository.delete_all(self.server_config.server.server_id)
        self.currency_repository.delete_all(self.server_config.server.server_id)
        self.server_setting_repository.delete_all(self.server_config.server.server_id)
        self.server_repository.delete(self.server_config.server)

        self.POI_repository.delete_all(self.server_config.server.server_id)

    def test_seed_point_of_interests_if_empty(self):
        # Act

        # Assert
        pois = self.POI_repository.get_all(self.server_config.server.server_id)
        self.assertGreater(len(pois), 0)  # Assuming the seed file has at least 1 POI

if __name__ == "__main__":
    unittest.main()