import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import GetLeaderboardQuery, GetLeaderboardQueryRequest
from tests.helper.default_setup import DefaultSetup

class TestGetLeaderboardQuery(unittest.TestCase):
    def setUp(self):
        self.defaultSetup = DefaultSetup()
        self.defaultSetup.setUp()

    def tearDown(self):
        self.defaultSetup.tearDown()

    def test_get_leaderboard_cash(self):
        # Arrange
        request = GetLeaderboardQueryRequest(
            guild=self.defaultSetup.discord_guild,
            page=1,
            sort_by="Cash"
        )

        # Act
        response = GetLeaderboardQuery(request).execute()

        # Assert
        self.assertEqual(response.server_config.server.guild_id, 12345)
        self.assertEqual(response.players[0].player.rank, 1)


if __name__ == "__main__":
    unittest.main()