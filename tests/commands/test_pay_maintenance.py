import asyncio
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import PayMaintenanceCommand, PayMaintenanceCommandRequest
from domain import Catalogue, PlayerUnit, InsufficientFundsException
from tests.helper.default_setup import DefaultSetup


class TestPayMaintenanceCommand(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.default_setup = DefaultSetup()
        asyncio.run(cls.default_setup.setUpClass())

    @classmethod
    def tearDownClass(cls):
        asyncio.run(cls.default_setup.tearDownClass())

    def setUp(self):
        asyncio.run(self.default_setup.setUp())
        asyncio.run(self.default_setup.setupData())

    def _add_unit_with_maintenance(self, player_id, unit_name, maintenance_cost, quantity=1):
        ds = self.default_setup
        server_id = ds.server_config.server.server_id

        catalogue = Catalogue(
            server_id=server_id,
            name=unit_name,
            type="Unit",
            description="Test unit",
            status="active",
            metadata={"maintenance_cost": maintenance_cost}
        )
        asyncio.run(ds.catalogue_repository.insert(catalogue))

        unit = PlayerUnit(player_id=player_id, name=unit_name, quantity=quantity, custom=True)
        asyncio.run(ds.player_unit_repository.insert(unit))

    def test_pay_maintenance_no_units(self):
        # Arrange — player1 has no units
        request = PayMaintenanceCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1
        )

        # Act
        response = asyncio.run(PayMaintenanceCommand(request).execute())

        # Assert — zero cost, no balance change
        self.assertTrue(response.success)
        self.assertEqual(response.total_cost, 0)

    def test_pay_maintenance_deducts_cost(self):
        # Arrange — player1 has 2 units with maintenance_cost=50 each → total=100
        player_id = self.default_setup.player_profile1.player.player_id
        self._add_unit_with_maintenance(player_id, "Maintenance Unit", maintenance_cost=50, quantity=2)

        request = PayMaintenanceCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1
        )

        # Act
        response = asyncio.run(PayMaintenanceCommand(request).execute())

        # Assert — 50 * 2 = 100 deducted
        self.assertTrue(response.success)
        self.assertEqual(response.total_cost, 100)
        self.assertEqual(response.player.balances[0].balance, 1400)  # 1500 - 100

    def test_pay_maintenance_insufficient_funds(self):
        # Arrange — player2 has 50 cash, unit costs 200
        player_id = self.default_setup.player_profile2.player.player_id
        self._add_unit_with_maintenance(player_id, "Expensive Unit", maintenance_cost=200, quantity=1)

        request = PayMaintenanceCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user2
        )

        # Act & Assert
        with self.assertRaises(InsufficientFundsException):
            asyncio.run(PayMaintenanceCommand(request).execute())


if __name__ == "__main__":
    unittest.main()
