import asyncio
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import TakeLoanCommand, TakeLoanCommandRequest
from domain import InvalidDataException
from tests.helper.default_setup import DefaultSetup


class TestTakeLoanCommand(unittest.TestCase):
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

    def test_take_loan_success(self):
        # Arrange — player1 has 1500 cash, bank interest_rate=0.01, range=None
        request = TakeLoanCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            amount=500
        )

        # Act
        response = asyncio.run(TakeLoanCommand(request).execute())

        # Assert loan created
        self.assertTrue(response.success)
        self.assertEqual(response.loan.principal, 500)
        self.assertEqual(response.loan.balance_remaining, 505)  # 500 * 1.01
        self.assertEqual(response.loan.status, 'active')

        # Assert cash increased
        self.assertEqual(response.player.balances[0].balance, 2000)  # 1500 + 500

    def test_take_loan_duplicate(self):
        # Arrange — take first loan
        request = TakeLoanCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            amount=500
        )
        asyncio.run(TakeLoanCommand(request).execute())

        # Act & Assert — second loan should fail
        with self.assertRaises(InvalidDataException):
            asyncio.run(TakeLoanCommand(request).execute())

    def test_take_loan_invalid_amount(self):
        # Arrange — zero amount is rejected
        request = TakeLoanCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            amount=0
        )

        # Act & Assert
        with self.assertRaises(InvalidDataException):
            asyncio.run(TakeLoanCommand(request).execute())


if __name__ == "__main__":
    unittest.main()
