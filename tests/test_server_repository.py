import asyncio
import sqlite3
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application.dtos.discord_guild import DiscordGuild
from domain import Server
from infrastructure import ServerRepository

class TestServerRepository(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Initialize shared resources for all tests
        cls.server_repository = asyncio.run(ServerRepository.get_instance(db_path=":memory:"))

    @classmethod
    def tearDownClass(cls):
        # Cleanup shared resources after all tests. Technically not needed for in-memory, and close_all will shutdown all connections for all repositories, but good practice.
        asyncio.run(cls.server_repository.close_all())

    def setUp(self):
        # Ensure the database is clean before each test
        asyncio.run(self.server_repository.clear_all())
        pass

    def test_add_server_valid(self):
        # Arrange
        discord_guild = DiscordGuild(guild_id=12343, name="TestGuild")
        new_server = Server(guild_id=discord_guild.guild_id, name=discord_guild.name)

        # Act
        server_id = asyncio.run(self.server_repository.insert(new_server))

        # Assert
        self.assertGreater(server_id, 0, "Server ID should be greater than 0.")

    def test_insert_server_duplicate(self):
        # Arrange
        discord_guild = DiscordGuild(guild_id=12344, name="TestGuild")
        new_server = Server(guild_id=discord_guild.guild_id, name=discord_guild.name)
        asyncio.run(self.server_repository.insert(new_server))

        # Act
        server_id = None
        with self.assertRaises(sqlite3.IntegrityError):
            server_id = asyncio.run(self.server_repository.insert(new_server))

        # Assert
        self.assertIsNone(server_id, "Server ID should be None for duplicate entries.")

    def test_get_server_by_id(self):
        # Arrange
        discord_guild = DiscordGuild(guild_id=12345, name="TestGuild")
        new_server = Server(guild_id=discord_guild.guild_id, name=discord_guild.name)
        server_id = asyncio.run(self.server_repository.insert(new_server))

        # Act
        retrieved_server = asyncio.run(self.server_repository.get_by_id(server_id))

        # Assert
        self.assertIsNotNone(retrieved_server, "Retrieved server should not be None.")
        self.assertEqual(retrieved_server.guild_id, discord_guild.guild_id, "Guild ID should match.")
        self.assertEqual(retrieved_server.name, discord_guild.name, "Server name should match.")

if __name__ == "__main__":
    unittest.main()