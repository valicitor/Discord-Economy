import asyncio
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import (
    CreateFactionCommand, CreateFactionCommandRequest,
    JoinFactionCommand, JoinFactionCommandRequest,
    LeaveFactionCommand, LeaveFactionCommandRequest,
)
from domain import InvalidDataException, RecordNotFoundException
from tests.helper.default_setup import DefaultSetup


class TestCreateFactionCommand(unittest.TestCase):
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

    def _remove_player1_faction(self):
        ds = self.default_setup
        player_id = ds.player_profile1.player.player_id
        server_id = ds.server_config.server.server_id

        faction = asyncio.run(ds.faction_repository.get_by_owner_id(player_id, server_id))
        if faction:
            asyncio.run(ds.faction_repository.delete(faction))
        asyncio.run(ds.faction_member_repository.delete_by_player_id(player_id))

    def test_create_faction_success(self):
        # Arrange — remove player1 from all faction associations
        self._remove_player1_faction()

        request = CreateFactionCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            name="New Faction",
            description="A brand new faction",
            color="#123456"
        )

        # Act
        response = asyncio.run(CreateFactionCommand(request).execute())

        # Assert
        self.assertTrue(response.success)
        self.assertEqual(response.faction.name, "New Faction")

        # Owner is now a member with role='owner'
        member = asyncio.run(self.default_setup.faction_member_repository.get_by_player_id(
            self.default_setup.player_profile1.player.player_id
        ))
        self.assertIsNotNone(member)
        self.assertEqual(member.role, 'owner')

    def test_create_faction_already_owner(self):
        # Arrange — player1 already owns "Third Faction"
        request = CreateFactionCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            name="Another Faction",
            description=None,
            color=None
        )

        # Act & Assert
        with self.assertRaises(InvalidDataException):
            asyncio.run(CreateFactionCommand(request).execute())

    def test_create_faction_already_member(self):
        # Arrange — delete player1's faction (so not owner) but keep member record
        ds = self.default_setup
        player_id = ds.player_profile1.player.player_id
        server_id = ds.server_config.server.server_id

        faction = asyncio.run(ds.faction_repository.get_by_owner_id(player_id, server_id))
        if faction:
            asyncio.run(ds.faction_repository.delete(faction))

        request = CreateFactionCommandRequest(
            guild=ds.discord_guild,
            user=ds.discord_user1,
            name="New Faction 2",
            description=None,
            color=None
        )

        # Act & Assert — fails because player is still a member
        with self.assertRaises(InvalidDataException):
            asyncio.run(CreateFactionCommand(request).execute())


class TestJoinFactionCommand(unittest.TestCase):
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

    def test_join_faction_success(self):
        # Arrange — remove player1 from all factions
        asyncio.run(self.default_setup.faction_member_repository.delete_by_player_id(
            self.default_setup.player_profile1.player.player_id
        ))

        request = JoinFactionCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            faction_name="Enemy Faction"
        )

        # Act
        response = asyncio.run(JoinFactionCommand(request).execute())

        # Assert
        self.assertTrue(response.success)
        self.assertEqual(response.faction.name, "Enemy Faction")

        member = asyncio.run(self.default_setup.faction_member_repository.get_by_player_id(
            self.default_setup.player_profile1.player.player_id
        ))
        self.assertIsNotNone(member)
        self.assertEqual(member.role, 'member')

    def test_join_faction_already_member(self):
        # Arrange — player1 is already in "Third Faction"
        request = JoinFactionCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            faction_name="Enemy Faction"
        )

        # Act & Assert
        with self.assertRaises(InvalidDataException):
            asyncio.run(JoinFactionCommand(request).execute())

    def test_join_faction_not_found(self):
        # Arrange — remove player1 membership, then try to join nonexistent faction
        asyncio.run(self.default_setup.faction_member_repository.delete_by_player_id(
            self.default_setup.player_profile1.player.player_id
        ))

        request = JoinFactionCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            faction_name="Nonexistent Faction"
        )

        # Act & Assert
        with self.assertRaises(RecordNotFoundException):
            asyncio.run(JoinFactionCommand(request).execute())


class TestLeaveFactionCommand(unittest.TestCase):
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

    def test_leave_faction_success(self):
        # Arrange — player1 is in "Third Faction" with role="Leader" (not "owner")
        request = LeaveFactionCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1
        )

        # Act
        response = asyncio.run(LeaveFactionCommand(request).execute())

        # Assert
        self.assertTrue(response.success)
        self.assertEqual(response.faction.name, "Third Faction")

        # Player no longer a member
        member = asyncio.run(self.default_setup.faction_member_repository.get_by_player_id(
            self.default_setup.player_profile1.player.player_id
        ))
        self.assertIsNone(member)

    def test_leave_faction_owner_cannot_leave(self):
        # Arrange — change player1's role to "owner"
        member = asyncio.run(self.default_setup.faction_member_repository.get_by_player_id(
            self.default_setup.player_profile1.player.player_id
        ))
        member.role = 'owner'
        asyncio.run(self.default_setup.faction_member_repository.update(member))

        request = LeaveFactionCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1
        )

        # Act & Assert
        with self.assertRaises(InvalidDataException):
            asyncio.run(LeaveFactionCommand(request).execute())

    def test_leave_faction_not_in_faction(self):
        # Arrange — remove player1 from all factions
        asyncio.run(self.default_setup.faction_member_repository.delete_by_player_id(
            self.default_setup.player_profile1.player.player_id
        ))

        request = LeaveFactionCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1
        )

        # Act & Assert
        with self.assertRaises(RecordNotFoundException):
            asyncio.run(LeaveFactionCommand(request).execute())


if __name__ == "__main__":
    unittest.main()
