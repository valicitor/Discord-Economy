import asyncio
import json
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import CreateCustomUnitCommand, CreateCustomUnitCommandRequest, UnassignEquipmentCommand, UnassignEquipmentCommandRequest
from domain import Catalogue, PlayerInventory, InvalidDataException, RecordNotFoundException
from tests.helper.default_setup import DefaultSetup

class TestUnassignEquipmentCommand(unittest.TestCase):
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
        asyncio.run(self._seed_and_create_unit())

    async def _seed_and_create_unit(self):
        server_id = self.default_setup.server_config.server.server_id
        player_id = self.default_setup.player_profile1.player.player_id

        race_id = await self.default_setup.catalogue_repository.insert(Catalogue(
            server_id=server_id, name="Test Human", type="Race", description="", status="active",
            metadata=json.dumps({"slots": {"primary": "Weapon"}, "stats": {}})
        ))
        weapon_id = await self.default_setup.catalogue_repository.insert(Catalogue(
            server_id=server_id, name="Test Sword", type="Weapon", description="", status="active",
            metadata=json.dumps({"stats": {}})
        ))
        self.weapon_catalogue_id = weapon_id

        await self.default_setup.player_inventory_repository.insert(PlayerInventory(
            player_id=player_id, catalogue_id=race_id, status='stored', quantity=1
        ))
        await self.default_setup.player_inventory_repository.insert(PlayerInventory(
            player_id=player_id, catalogue_id=weapon_id, status='stored', quantity=1
        ))

        # Create unit with the weapon equipped
        request = CreateCustomUnitCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            unit_name="Armed Warrior",
            race_name="Test Human",
            equipment={"primary": "Test Sword"}
        )
        await CreateCustomUnitCommand(request).execute()

    def _unassign(self, user, unit_name, slot_name):
        request = UnassignEquipmentCommandRequest(
            guild=self.default_setup.discord_guild,
            user=user,
            unit_name=unit_name,
            slot_name=slot_name
        )
        return asyncio.run(UnassignEquipmentCommand(request).execute())

    def test_unassign_equipment_returns_to_inventory(self):
        player_id = self.default_setup.player_profile1.player.player_id

        response = self._unassign(self.default_setup.discord_user1, "Armed Warrior", "primary")

        self.assertTrue(response.success)
        self.assertEqual(response.unassigned_item, "Test Sword")
        self.assertNotIn("primary", response.unit.metadata.get("assigned", {}))

        # Weapon should be back in stored inventory
        stored = asyncio.run(self.default_setup.player_inventory_repository.get_by_player_catalogue_id(
            player_id, self.weapon_catalogue_id, status='stored'
        ))
        self.assertIsNotNone(stored)
        self.assertEqual(stored.quantity, 1)

        # Weapon should no longer be equipped
        equipped = asyncio.run(self.default_setup.player_inventory_repository.get_by_player_catalogue_id(
            player_id, self.weapon_catalogue_id, status='equipped'
        ))
        self.assertIsNone(equipped)

    def test_unassign_unit_not_found(self):
        with self.assertRaises(RecordNotFoundException):
            self._unassign(self.default_setup.discord_user1, "Nonexistent Unit", "primary")

    def test_unassign_empty_slot(self):
        # First unassign to clear the slot, then try again
        self._unassign(self.default_setup.discord_user1, "Armed Warrior", "primary")
        with self.assertRaises(InvalidDataException):
            self._unassign(self.default_setup.discord_user1, "Armed Warrior", "primary")

if __name__ == "__main__":
    unittest.main()
