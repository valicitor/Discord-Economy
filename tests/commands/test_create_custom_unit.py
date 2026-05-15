import asyncio
import json
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import CreateCustomUnitCommand, CreateCustomUnitCommandRequest
from domain import Catalogue, PlayerInventory, InvalidDataException, DuplicateRecordException
from tests.helper.default_setup import DefaultSetup

class TestCreateCustomUnitCommand(unittest.TestCase):
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
        asyncio.run(self._seed_test_catalogue())

    async def _seed_test_catalogue(self):
        server_id = self.default_setup.server_config.server.server_id
        player_id = self.default_setup.player_profile1.player.player_id

        race_id = await self.default_setup.catalogue_repository.insert(Catalogue(
            server_id=server_id,
            name="Test Human",
            type="Race",
            description="A test race",
            status="active",
            metadata=json.dumps({"slots": {"primary": "Weapon", "body": "Armor"}, "stats": {"WS": 3, "T": 3, "W": 1}})
        ))
        weapon_id = await self.default_setup.catalogue_repository.insert(Catalogue(
            server_id=server_id,
            name="Test Sword",
            type="Weapon",
            description="A test sword",
            status="active",
            metadata=json.dumps({"stats": {"Attacks": 1, "S": 4, "AP": 0, "D": 1}})
        ))

        self.race_catalogue_id = race_id
        self.weapon_catalogue_id = weapon_id

        # Give player1 the race and weapon in stored inventory
        await self.default_setup.player_inventory_repository.insert(PlayerInventory(
            player_id=player_id, catalogue_id=race_id, status='stored', quantity=1
        ))
        await self.default_setup.player_inventory_repository.insert(PlayerInventory(
            player_id=player_id, catalogue_id=weapon_id, status='stored', quantity=1
        ))

    def _create_unit(self, user, unit_name, race_name, equipment=None):
        request = CreateCustomUnitCommandRequest(
            guild=self.default_setup.discord_guild,
            user=user,
            unit_name=unit_name,
            race_name=race_name,
            equipment=equipment or {}
        )
        return asyncio.run(CreateCustomUnitCommand(request).execute())

    def test_create_unit_no_equipment(self):
        response = self._create_unit(self.default_setup.discord_user1, "My Warrior", "Test Human")

        self.assertTrue(response.success)
        self.assertEqual(response.unit.name, "My Warrior")
        self.assertEqual(response.unit.custom, 1)
        self.assertEqual(response.unit.quantity, 1)

        # Race should have moved from stored to equipped
        player_id = self.default_setup.player_profile1.player.player_id
        stored = asyncio.run(self.default_setup.player_inventory_repository.get_by_player_catalogue_id(
            player_id, self.race_catalogue_id, status='stored'
        ))
        self.assertIsNone(stored)

        equipped = asyncio.run(self.default_setup.player_inventory_repository.get_by_player_catalogue_id(
            player_id, self.race_catalogue_id, status='equipped'
        ))
        self.assertIsNotNone(equipped)
        self.assertEqual(equipped.quantity, 1)

    def test_create_unit_with_equipment(self):
        response = self._create_unit(
            self.default_setup.discord_user1,
            "Armed Warrior",
            "Test Human",
            equipment={"primary": "Test Sword"}
        )

        self.assertTrue(response.success)
        metadata = response.unit.metadata if isinstance(response.unit.metadata, dict) else json.loads(response.unit.metadata)
        assigned = metadata.get("assigned", {})
        self.assertEqual(assigned.get("primary"), "Test Sword")

        # Weapon should have moved from stored to equipped
        player_id = self.default_setup.player_profile1.player.player_id
        weapon_stored = asyncio.run(self.default_setup.player_inventory_repository.get_by_player_catalogue_id(
            player_id, self.weapon_catalogue_id, status='stored'
        ))
        self.assertIsNone(weapon_stored)

        weapon_equipped = asyncio.run(self.default_setup.player_inventory_repository.get_by_player_catalogue_id(
            player_id, self.weapon_catalogue_id, status='equipped'
        ))
        self.assertIsNotNone(weapon_equipped)

    def test_create_unit_duplicate_name(self):
        self._create_unit(self.default_setup.discord_user1, "My Warrior", "Test Human")
        with self.assertRaises(DuplicateRecordException):
            self._create_unit(self.default_setup.discord_user1, "My Warrior", "Test Human")

    def test_create_unit_invalid_slot(self):
        with self.assertRaises(InvalidDataException):
            self._create_unit(
                self.default_setup.discord_user1,
                "My Warrior",
                "Test Human",
                equipment={"nonexistent_slot": "Test Sword"}
            )

    def test_create_unit_missing_inventory(self):
        # player2 has no race in inventory
        with self.assertRaises(InvalidDataException):
            self._create_unit(self.default_setup.discord_user2, "Their Warrior", "Test Human")

if __name__ == "__main__":
    unittest.main()
