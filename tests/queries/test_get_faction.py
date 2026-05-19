import asyncio
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import GetFactionQuery, GetFactionQueryRequest
from domain import RecordNotFoundException
from tests.helper.default_setup import DefaultSetup


class TestGetFactionQuery(unittest.TestCase):
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

    def test_get_faction_by_name(self):
        # Arrange — "Enemy Faction" is seeded in setupData
        request = GetFactionQueryRequest(
            guild=self.default_setup.discord_guild,
            faction_name="Enemy Faction"
        )

        # Act
        response = asyncio.run(GetFactionQuery(request).execute())

        # Assert
        self.assertTrue(response.success)
        self.assertEqual(response.faction.name, "Enemy Faction")
        self.assertGreater(len(response.members), 0)

        roles = [m.role for m, _ in response.members]
        self.assertIn("Leader", roles)

    def test_get_faction_by_id(self):
        # Arrange — look up "Ally Faction" first to get its ID
        ds = self.default_setup
        server_id = ds.server_config.server.server_id
        faction = asyncio.run(ds.faction_repository.get_by_name("Ally Faction", server_id))
        self.assertIsNotNone(faction)

        request = GetFactionQueryRequest(
            guild=ds.discord_guild,
            faction_id=faction.faction_id
        )

        # Act
        response = asyncio.run(GetFactionQuery(request).execute())

        # Assert
        self.assertTrue(response.success)
        self.assertEqual(response.faction.faction_id, faction.faction_id)
        self.assertEqual(response.faction.name, "Ally Faction")

    def test_get_faction_not_found(self):
        # Arrange — nonexistent faction name
        request = GetFactionQueryRequest(
            guild=self.default_setup.discord_guild,
            faction_name="Phantom Faction"
        )

        # Act & Assert
        with self.assertRaises(RecordNotFoundException):
            asyncio.run(GetFactionQuery(request).execute())

    def test_get_faction_neither_name_nor_id(self):
        # Arrange — no lookup parameter provided
        request = GetFactionQueryRequest(
            guild=self.default_setup.discord_guild
        )

        # Act & Assert — faction is None → raises RecordNotFoundException
        with self.assertRaises(RecordNotFoundException):
            asyncio.run(GetFactionQuery(request).execute())


if __name__ == "__main__":
    unittest.main()
