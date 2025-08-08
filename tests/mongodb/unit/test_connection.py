"""Unit tests for MongoDB connection operations.

These tests validate connection establishment, closure, and failure scenarios.
"""

import pytest
import utils

from data_store.nosql_store.nosql_store import NoSQLStore


# Using the mongodb_store fixture from conftest.py for connection establishment test
class TestConnection:
    def test_connection_establishment(self, mongodb_store):
        """Test that MongoDB connection is established successfully."""
        client = mongodb_store.client
        # Assert that the client and underlying connection are available
        assert client is not None
        assert client._client is not None

    def test_connection_closure(self):
        """Test closing MongoDB connection."""
        # Create a new store instance and manually connect and close
        config = utils.get_config().get("nosql_store")
        store = NoSQLStore(config=config)
        store._connect()
        store._close()
        # Since _close() does not return anything, we assume success if no exception is raised
        assert True

    @pytest.mark.timeout(3)
    def test_connection_fail(self):
        """Test connection failure with invalid host configuration."""
        bad_config = {
            "framework": "mongodb",
            "connection": {
                "host": "invalid_host",
                "port": 27017,
                "username": "invalid_user",
                "password": "invalid_pass",
                "connection_timeout": 1,  # Short timeout for testing
            },
        }
        with pytest.raises(RuntimeError) as excinfo:
            store = NoSQLStore(config=bad_config.get("nosql_store", bad_config))
            store._connect()
            store._close()
        # Check for timeout error message in exception
        assert "timeout" in str(excinfo.value).lower()
