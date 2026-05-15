import asyncio
import json
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import AssignPlayerEquipmentCommand, AssignPlayerEquipmentCommandRequest
from domain import Catalogue, PlayerInventory, Item, InvalidDataException
from tests.helper.default_setup import DefaultSetup

class TestAssignPlayerEquipmentCommand(unittest.TestCase):
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
        asyncio.run(self._seed_item())

    async def _seed_item(self):
        server_id = self.default_setup.server_config.server.server_id
        player_id = self.default_setup.player_profile1.player.player_id

        catalogue_id = await self.default_setup.catalogue_repository.insert(Catalogue(
            server_id=server_id, name="Test Knife", type="Weapon", description="", status="active",
            metadata=json.dumps({"stats": {"Attacks": 1, "S": 3, "AP": 0, "D": 1}})
        ))
        item_id = await self.default_setup.items_repository.insert(Item(
            server_id=server_id, catalogue_id=catalogue_id, name="Test Knife",
            icon="🔪", price=100, description="A test knife", stock=10, sellable=True
        ))
        self.item_catalogue_id = catalogue_id

        await self.default_setup.player_inventory_repository.insert(PlayerInventory(
            player_id=player_id, catalogue_id=catalogue_id, status='stored', quantity=1
        ))

    def _equip(self, user, item_name):
        request = AssignPlayerEquipmentCommandRequest(
            guild=self.default_setup.discord_guild,
            user=user,
            item_name=item_name,
            equip=True
        )
        return asyncio.run(AssignPlayerEquipmentCommand(request).execute())

    def _unequip(self, user, item_name):
        request = AssignPlayerEquipmentCommandRequest(
            guild=self.default_setup.discord_guild,
            user=user,
            item_name=item_name,
            equip=False
        )
        return asyncio.run(AssignPlayerEquipmentCommand(request).execute())

    def test_equip_item(self):
        player_id = self.default_setup.player_profile1.player.player_id

        response = self._equip(self.default_setup.discord_user1, "Test Knife")

        self.assertTrue(response.success)
        self.assertTrue(response.equipped)

        # Item should be in character slot
        character_slot = asyncio.run(self.default_setup.player_inventory_repository.get_by_player_catalogue_id(
            player_id, self.item_catalogue_id, status='character'
        ))
        self.assertIsNotNone(character_slot)
        self.assertEqual(character_slot.quantity, 1)

        # Item should no longer be in stored
        stored = asyncio.run(self.default_setup.player_inventory_repository.get_by_player_catalogue_id(
            player_id, self.item_catalogue_id, status='stored'
        ))
        self.assertIsNone(stored)

    def test_unequip_item(self):
        player_id = self.default_setup.player_profile1.player.player_id

        self._equip(self.default_setup.discord_user1, "Test Knife")
        response = self._unequip(self.default_setup.discord_user1, "Test Knife")

        self.assertTrue(response.success)
        self.assertFalse(response.equipped)

        # Item should be back in stored
        stored = asyncio.run(self.default_setup.player_inventory_repository.get_by_player_catalogue_id(
            player_id, self.item_catalogue_id, status='stored'
        ))
        self.assertIsNotNone(stored)
        self.assertEqual(stored.quantity, 1)

        # Character slot should be gone
        character_slot = asyncio.run(self.default_setup.player_inventory_repository.get_by_player_catalogue_id(
            player_id, self.item_catalogue_id, status='character'
        ))
        self.assertIsNone(character_slot)

    def test_equip_item_not_in_inventory(self):
        # player2 doesn't have the knife
        with self.assertRaises(InvalidDataException):
            self._equip(self.default_setup.discord_user2, "Test Knife")

    def test_unequip_item_not_equipped(self):
        # Knife is in stored, not character
        with self.assertRaises(InvalidDataException):
            self._unequip(self.default_setup.discord_user1, "Test Knife")

if __name__ == "__main__":
    unittest.main()
