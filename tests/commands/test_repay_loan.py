import asyncio
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import TakeLoanCommand, TakeLoanCommandRequest, RepayLoanCommand, RepayLoanCommandRequest
from domain import RecordNotFoundException, InsufficientFundsException
from tests.helper.default_setup import DefaultSetup


class TestRepayLoanCommand(unittest.TestCase):
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

    def _take_loan(self, discord_user, amount):
        request = TakeLoanCommandRequest(
            guild=self.default_setup.discord_guild,
            user=discord_user,
            amount=amount
        )
        return asyncio.run(TakeLoanCommand(request).execute())

    def test_partial_repay(self):
        # Arrange — player1 takes 500 loan (balance_remaining=505), repays 200
        self._take_loan(self.default_setup.discord_user1, 500)
        request = RepayLoanCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            amount=200
        )

        # Act
        response = asyncio.run(RepayLoanCommand(request).execute())

        # Assert partial repayment
        self.assertTrue(response.success)
        self.assertEqual(response.amount_paid, 200)
        self.assertEqual(response.loan.balance_remaining, 305)  # 505 - 200
        self.assertEqual(response.loan.status, 'active')
        self.assertEqual(response.player.balances[0].balance, 1800)  # 1500 + 500 - 200

    def test_full_repay_marks_loan_repaid(self):
        # Arrange — player1 takes 500 loan, repays full balance (505)
        self._take_loan(self.default_setup.discord_user1, 500)
        request = RepayLoanCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            amount=505
        )

        # Act
        response = asyncio.run(RepayLoanCommand(request).execute())

        # Assert loan marked repaid
        self.assertTrue(response.success)
        self.assertEqual(response.amount_paid, 505)
        self.assertEqual(response.loan.balance_remaining, 0)
        self.assertEqual(response.loan.status, 'repaid')
        self.assertEqual(response.player.balances[0].balance, 1495)  # 1500 + 500 - 505

    def test_repay_no_loan(self):
        # Arrange — player1 has no active loan
        request = RepayLoanCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            amount=100
        )

        # Act & Assert
        with self.assertRaises(RecordNotFoundException):
            asyncio.run(RepayLoanCommand(request).execute())

    def test_repay_insufficient_funds(self):
        # Arrange — player1 takes 500 loan (cash: 1500→2000), then reduce cash to 10
        self._take_loan(self.default_setup.discord_user1, 500)

        balance = self.default_setup.player_profile1.balances[0]
        balance.balance = 10
        asyncio.run(self.default_setup.player_balance_repository.update(balance))

        request = RepayLoanCommandRequest(
            guild=self.default_setup.discord_guild,
            user=self.default_setup.discord_user1,
            amount=505  # min(505, 505) = 505, but player only has 10
        )

        # Act & Assert
        with self.assertRaises(InsufficientFundsException):
            asyncio.run(RepayLoanCommand(request).execute())


if __name__ == "__main__":
    unittest.main()
