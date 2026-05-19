import asyncio
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import StartTransportCommand, StartTransportCommandRequest
from domain import Business, BusinessInventory, Catalogue, InvalidDataException, RecordNotFoundException
from tests.helper.default_setup import DefaultSetup


class TestStartTransportCommand(unittest.TestCase):
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
        self._setup_businesses()

    def _setup_businesses(self):
        ds = self.default_setup
        server_id = ds.server_config.server.server_id

        # Register ore in the catalogue
        ore = Catalogue(server_id=server_id, name="Ore", type="material")
        self.ore_catalogue_id = asyncio.run(ds.catalogue_repository.insert(ore))

        # Businesses at (0, 0) with range=None so player is always in range
        biz_a = Business(server_id=server_id, name="Source Base", type="production", x=0, y=0, range=None)
        self.biz_a_id = asyncio.run(ds.business_repository.insert(biz_a))

        biz_b = Business(server_id=server_id, name="Dest Base", type="production", x=0, y=0, range=None)
        self.biz_b_id = asyncio.run(ds.business_repository.insert(biz_b))

        # Seed 100 ore at source
        inventory = BusinessInventory(business_id=self.biz_a_id, catalogue_id=self.ore_catalogue_id, quantity=100)
        asyncio.run(ds.business_inventory_repository.insert(inventory))

    def test_start_transport_success(self):
        request = StartTransportCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            from_business_id=self.biz_a_id,
            to_business_id=self.biz_b_id,
            catalogue_id=self.ore_catalogue_id,
            quantity=50
        )

        response = asyncio.run(StartTransportCommand(request).execute())

        self.assertTrue(response.success)
        self.assertEqual(response.transport.catalogue_id, self.ore_catalogue_id)
        self.assertEqual(response.transport.quantity, 50)
        self.assertEqual(response.transport.status, "in_transit")
        self.assertIsNotNone(response.transport.transport_id)

        updated = asyncio.run(self.default_setup.business_inventory_repository.get_by_business_catalogue(
            self.biz_a_id, self.ore_catalogue_id
        ))
        self.assertEqual(updated.quantity, 50)  # 100 - 50

    def test_start_transport_insufficient_resource(self):
        request = StartTransportCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            from_business_id=self.biz_a_id,
            to_business_id=self.biz_b_id,
            catalogue_id=self.ore_catalogue_id,
            quantity=200
        )

        with self.assertRaises(InvalidDataException):
            asyncio.run(StartTransportCommand(request).execute())

    def test_start_transport_source_not_found(self):
        request = StartTransportCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            from_business_id=99999,
            to_business_id=self.biz_b_id,
            catalogue_id=self.ore_catalogue_id,
            quantity=10
        )

        with self.assertRaises(RecordNotFoundException):
            asyncio.run(StartTransportCommand(request).execute())

    def test_start_transport_invalid_quantity(self):
        request = StartTransportCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            from_business_id=self.biz_a_id,
            to_business_id=self.biz_b_id,
            catalogue_id=self.ore_catalogue_id,
            quantity=0
        )

        with self.assertRaises(InvalidDataException):
            asyncio.run(StartTransportCommand(request).execute())


if __name__ == "__main__":
    unittest.main()
