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
    VehicleRepository, 
    VehicleStatRepository, 
    FactionRepository,
    VehiclesSeeder, 
    VehicleStatsSeeder
)
from application import DiscordGuild
from application.helpers.ensure_user import ensure_guild

class TestVehiclesSeeder(unittest.TestCase):
    def setUp(self):
        self.server_repository = ServerRepository(db_path=":memory:")
        self.server_setting_repository = ServerSettingRepository(db_path=":memory:")
        self.currency_repository = CurrencyRepository(db_path=":memory:")
        self.bank_repository = BankRepository(db_path=":memory:")
        self.faction_repository = FactionRepository(db_path=":memory:")

        self.discord_guild = DiscordGuild(guild_id=12911, name="TestGuild")
        self.server_config = ensure_guild(self.discord_guild)
    
        self.vehicle_repository = VehicleRepository(seeder=VehiclesSeeder(self.server_config.server.server_id), db_path=":memory:")  # Use in-memory database for testing
        self.vehicle_stat_repository = VehicleStatRepository(seeder=VehicleStatsSeeder(self.server_config.server.server_id), db_path=":memory:")  # Use in-memory database for testing

    def tearDown(self):
        # Remove test database
        self.faction_repository.delete_all(self.server_config.server.server_id)
        self.bank_repository.delete_all(self.server_config.server.server_id)
        self.currency_repository.delete_all(self.server_config.server.server_id)
        self.server_setting_repository.delete_all(self.server_config.server.server_id)
        self.server_repository.delete(self.server_config.server)

        self.vehicle_repository.delete_all(self.server_config.server.server_id)
        self.vehicle_stat_repository.delete_all()

    def test_seed_vehicles_and_vehicle_stats_if_empty(self):
        # Act

        # Assert
        vehicles = self.vehicle_repository.get_all(self.server_config.server.server_id)
        vehicle_stats = self.vehicle_stat_repository.get_all()
        self.assertGreater(len(vehicles), 0)  # Assuming the seed file has at least 1 vehicle
        self.assertGreater(len(vehicle_stats), 0)  # Assuming the seed file has at least 1 vehicle stat

if __name__ == "__main__":
    unittest.main()