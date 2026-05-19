import asyncio
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import CompleteTransportCommand, CompleteTransportCommandRequest
from domain import Business, BusinessInventory, Catalogue, Transport, RecordNotFoundException
from tests.helper.default_setup import DefaultSetup


class TestCompleteTransportCommand(unittest.TestCase):
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

        # Register crystals in the catalogue
        crystals = Catalogue(server_id=server_id, name="Crystals", type="material")
        self.crystals_catalogue_id = asyncio.run(ds.catalogue_repository.insert(crystals))

        biz_a = Business(server_id=server_id, name="Transport Source", type="production", x=0, y=0, range=None)
        self.biz_a_id = asyncio.run(ds.business_repository.insert(biz_a))

        biz_b = Business(server_id=server_id, name="Transport Dest", type="production", x=0, y=0, range=None)
        self.biz_b_id = asyncio.run(ds.business_repository.insert(biz_b))

    def _insert_arrived_transport(self, player_id, quantity=25):
        transport = Transport(
            player_id=player_id,
            from_business_id=self.biz_a_id,
            to_business_id=self.biz_b_id,
            catalogue_id=self.crystals_catalogue_id,
            quantity=quantity,
            status="in_transit",
            arrive_at="2000-01-01 00:00:00"  # well in the past
        )
        asyncio.run(self.default_setup.transport_repository.insert(transport))

    def test_complete_transport_success(self):
        player_id = self.default_setup.player_profile1.player.player_id
        self._insert_arrived_transport(player_id, quantity=25)

        request = CompleteTransportCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1
        )

        response = asyncio.run(CompleteTransportCommand(request).execute())

        self.assertTrue(response.success)
        self.assertEqual(len(response.completed), 1)
        self.assertEqual(response.completed[0].status, "arrived")
        self.assertEqual(response.completed[0].quantity, 25)

        dest_inventory = asyncio.run(self.default_setup.business_inventory_repository.get_by_business_catalogue(
            self.biz_b_id, self.crystals_catalogue_id
        ))
        self.assertIsNotNone(dest_inventory)
        self.assertEqual(dest_inventory.quantity, 25)

    def test_complete_transport_no_arrived(self):
        request = CompleteTransportCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1
        )

        with self.assertRaises(RecordNotFoundException):
            asyncio.run(CompleteTransportCommand(request).execute())

    def test_complete_transport_adds_to_existing_inventory(self):
        # Destination already has 10 crystals, transport delivers 25 more
        existing = BusinessInventory(business_id=self.biz_b_id, catalogue_id=self.crystals_catalogue_id, quantity=10)
        asyncio.run(self.default_setup.business_inventory_repository.insert(existing))

        player_id = self.default_setup.player_profile1.player.player_id
        self._insert_arrived_transport(player_id, quantity=25)

        request = CompleteTransportCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1
        )

        asyncio.run(CompleteTransportCommand(request).execute())

        dest_inventory = asyncio.run(self.default_setup.business_inventory_repository.get_by_business_catalogue(
            self.biz_b_id, self.crystals_catalogue_id
        ))
        self.assertEqual(dest_inventory.quantity, 35)  # 10 + 25


if __name__ == "__main__":
    unittest.main()
