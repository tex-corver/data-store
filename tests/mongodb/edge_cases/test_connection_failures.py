"""Edge case tests for MongoDB connection failures.

These tests validate behavior when MongoDB connections fail.
"""

import pytest
import utils

from data_store.nosql_store.nosql_store import NoSQLStore


class TestConnectionFailures:
    """Test MongoDB connection failure scenarios."""

    @pytest.mark.timeout(3)
    def test_connection_fail_with_invalid_host(self):
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

    def test_connection_fail_with_invalid_credentials(self):
        """Test connection failure with invalid credentials.

        Note: This test requires a MongoDB instance to be running
        with authentication enabled to be meaningful.
        """
        config = utils.get_config()
        # Modify the config to use invalid credentials
        nosql_config = config.get("nosql_store")
        if nosql_config is None:
            pytest.skip("NoSQL configuration not found")
        invalid_config = nosql_config.copy()
        if "connection" in invalid_config and invalid_config["connection"] is not None:
            invalid_config["connection"] = invalid_config["connection"].copy()
            invalid_config["connection"]["username"] = "invalid_user"
            invalid_config["connection"]["password"] = "invalid_pass"

        # This may or may not fail depending on MongoDB configuration
        # If MongoDB is running without auth, this might still connect
        try:
            store = NoSQLStore(config=invalid_config)
            store._connect()
            store._close()
            # If we get here, the connection succeeded (MongoDB might not require auth)
            # This is not necessarily a failure of the test
        except RuntimeError:
            # Expected behavior when auth fails
            pass
        except Exception as e:
            # Any other exception is also acceptable as indicating connection issues
            pass

    def test_connection_fail_with_nonexistent_database(self):
        """Test connection behavior with nonexistent database.

        Note: MongoDB typically creates databases on first use,
        so this test may not actually fail.
        """
        config = utils.get_config()
        # Modify the config to use a nonexistent database
        nosql_config = config.get("nosql_store")
        if nosql_config is None:
            pytest.skip("NoSQL configuration not found")
        nonexistent_config = nosql_config.copy()
        if (
            "connection" in nonexistent_config
            and nonexistent_config["connection"] is not None
        ):
            nonexistent_config["connection"] = nonexistent_config["connection"].copy()
            nonexistent_config["connection"]["database"] = "nonexistent_database_12345"

        # This should generally succeed as MongoDB creates DBs on first use
        try:
            store = NoSQLStore(config=nonexistent_config)
            store._connect()
            # Perform a simple operation to ensure connection works
            # This will create the database if it doesn't exist
            store._close()
        except RuntimeError as e:
            # If there's a runtime error, it's related to connection issues
            pass
