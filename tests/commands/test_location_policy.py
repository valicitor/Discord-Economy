import asyncio
import sys
import os

from config import BASE_DIR
sys.path.insert(0, os.path.abspath(BASE_DIR))

import unittest
from application import (
    CreateLocationPolicyCommand, CreateLocationPolicyCommandRequest,
    UpdateLocationPolicyCommand, UpdateLocationPolicyCommandRequest,
    DeleteLocationPolicyCommand, DeleteLocationPolicyCommandRequest,
)
from domain import RecordNotFoundException, DuplicateRecordException
from tests.helper.default_setup import DefaultSetup


class TestLocationPolicyCommands(unittest.TestCase):
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

    def _get_alderaan_id(self):
        ds = self.default_setup
        server_id = ds.server_config.server.server_id
        location = asyncio.run(ds.location_repository.get_by_name("Alderaan", server_id))
        self.assertIsNotNone(location, "Alderaan should be seeded")
        return location.location_id

    def test_create_policy_success(self):
        # Arrange — delete existing policy for Alderaan so we can create a new one
        location_id = self._get_alderaan_id()
        policy = asyncio.run(self.default_setup.location_policy_repository.get_by_location(location_id))
        if policy:
            asyncio.run(self.default_setup.location_policy_repository.delete(policy))

        request = CreateLocationPolicyCommandRequest(
            location_id=location_id,
            tax_rate=0.05,
            trade_tariff=0.02
        )

        # Act
        response = asyncio.run(CreateLocationPolicyCommand(request).execute())

        # Assert
        self.assertTrue(response.success)
        self.assertEqual(response.policy.location_id, location_id)
        self.assertAlmostEqual(response.policy.tax_rate, 0.05)
        self.assertAlmostEqual(response.policy.trade_tariff, 0.02)

    def test_create_policy_already_exists(self):
        # Arrange — Alderaan already has a policy (seeded by SetupServerCommand)
        location_id = self._get_alderaan_id()

        request = CreateLocationPolicyCommandRequest(location_id=location_id)

        # Act & Assert
        with self.assertRaises(DuplicateRecordException):
            asyncio.run(CreateLocationPolicyCommand(request).execute())

    def test_create_policy_location_not_found(self):
        # Arrange — nonexistent location_id
        request = CreateLocationPolicyCommandRequest(location_id=99999)

        # Act & Assert
        with self.assertRaises(RecordNotFoundException):
            asyncio.run(CreateLocationPolicyCommand(request).execute())

    def test_update_policy_success(self):
        # Arrange — Alderaan already has a policy
        location_id = self._get_alderaan_id()

        request = UpdateLocationPolicyCommandRequest(
            location_id=location_id,
            tax_rate=0.15,
            import_restricted=True
        )

        # Act
        response = asyncio.run(UpdateLocationPolicyCommand(request).execute())

        # Assert
        self.assertTrue(response.success)
        self.assertAlmostEqual(response.policy.tax_rate, 0.15)
        self.assertTrue(response.policy.import_restricted)

    def test_update_policy_not_found(self):
        # Arrange — location with no policy
        request = UpdateLocationPolicyCommandRequest(location_id=99999, tax_rate=0.1)

        # Act & Assert
        with self.assertRaises(RecordNotFoundException):
            asyncio.run(UpdateLocationPolicyCommand(request).execute())

    def test_delete_policy_success(self):
        # Arrange — Alderaan already has a policy
        location_id = self._get_alderaan_id()

        request = DeleteLocationPolicyCommandRequest(location_id=location_id)

        # Act
        response = asyncio.run(DeleteLocationPolicyCommand(request).execute())

        # Assert
        self.assertTrue(response.success)
        self.assertEqual(response.location_id, location_id)

        # Confirm policy is gone
        policy = asyncio.run(self.default_setup.location_policy_repository.get_by_location(location_id))
        self.assertIsNone(policy)

    def test_delete_policy_not_found(self):
        # Arrange — nonexistent location_id
        request = DeleteLocationPolicyCommandRequest(location_id=99999)

        # Act & Assert
        with self.assertRaises(RecordNotFoundException):
            asyncio.run(DeleteLocationPolicyCommand(request).execute())


if __name__ == "__main__":
    unittest.main()
