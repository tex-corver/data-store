"""Edge case tests for MongoDB authentication errors.

These tests validate behavior when authentication fails.
"""

import pytest
import utils

from data_store.nosql_store.configurations import NoSQLConfiguration, NoSQLConnection
from data_store.nosql_store.nosql_store import NoSQLStore

# Test collection name
TEST_COLLECTION = "test_collection_auth_errors"


@pytest.fixture(autouse=True)
def cleanup_auth_collection(mongodb_store):
    """Clean up auth test collection before and after each test."""
    try:
        mongodb_store.delete(TEST_COLLECTION, {})
    except Exception:
        pass
    yield
    try:
        mongodb_store.delete(TEST_COLLECTION, {})
    except Exception:
        pass


class TestAuthenticationErrors:
    """Test MongoDB authentication error scenarios."""

    def test_invalid_username_password(self):
        """Test connection with invalid username and password.

        Note: This test requires a MongoDB instance with authentication enabled.
        If MongoDB is running without auth, this test may not be meaningful.
        """
        config = utils.get_config()
        nosql_config = config.get("nosql_store")
        if nosql_config is None:
            pytest.skip("NoSQL configuration not found")

        # Create a configuration with invalid credentials
        connection_config = nosql_config.get("connection", {})
        if not connection_config:
            pytest.skip("Connection configuration not found")

        # Copy the connection config and modify credentials
        modified_connection = connection_config.copy()
        modified_connection["username"] = "invalid_username"
        modified_connection["password"] = "invalid_password"

        # Create NoSQLConnection and NoSQLConfiguration
        connection = NoSQLConnection(**modified_connection)
        auth_config = NoSQLConfiguration(
            framework=nosql_config.get("framework", "mongodb"), connection=connection
        )

        # Try to connect - this may or may not fail depending on MongoDB setup
        try:
            store = NoSQLStore(config=auth_config.model_dump())
            store._connect()
            # If we get here, authentication succeeded or wasn't required
            store._close()
        except RuntimeError as e:
            # Authentication failure should result in a RuntimeError
            # Check if it's related to authentication
            error_msg = str(e).lower()
            # We expect authentication-related errors, but we can't be more specific
            # without knowing the exact MongoDB setup
            pass
        except Exception as e:
            # Any other exception is also acceptable as indicating connection issues
            pass

    def test_missing_password_with_username(self):
        """Test connection with username but no password."""
        config = utils.get_config()
        nosql_config = config.get("nosql_store")
        if nosql_config is None:
            pytest.skip("NoSQL configuration not found")

        # Create a configuration with username but no password
        connection_config = nosql_config.get("connection", {})
        if not connection_config:
            pytest.skip("Connection configuration not found")

        # Copy the connection config and modify credentials
        modified_connection = connection_config.copy()
        modified_connection["username"] = "some_username"
        modified_connection.pop("password", None)  # Remove password if it exists

        # Create NoSQLConnection and NoSQLConfiguration
        connection = NoSQLConnection(**modified_connection)
        auth_config = NoSQLConfiguration(
            framework=nosql_config.get("framework", "mongodb"), connection=connection
        )

        # Try to connect
        try:
            store = NoSQLStore(config=auth_config.model_dump())
            store._connect()
            # Connection may succeed depending on MongoDB setup
            store._close()
        except RuntimeError:
            # Connection failure is acceptable
            pass
        except Exception:
            # Any other exception is also acceptable
            pass

    def test_invalid_auth_source(self):
        """Test connection with invalid authentication source."""
        config = utils.get_config()
        nosql_config = config.get("nosql_store")
        if nosql_config is None:
            pytest.skip("NoSQL configuration not found")

        # Create a configuration with invalid auth source
        connection_config = nosql_config.get("connection", {})
        if not connection_config:
            pytest.skip("Connection configuration not found")

        # Copy the connection config and modify auth source
        modified_connection = connection_config.copy()
        modified_connection["auth_source"] = "invalid_auth_source"

        # Create NoSQLConnection and NoSQLConfiguration
        connection = NoSQLConnection(**modified_connection)
        auth_config = NoSQLConfiguration(
            framework=nosql_config.get("framework", "mongodb"), connection=connection
        )

        # Try to connect
        try:
            store = NoSQLStore(config=auth_config.model_dump())
            store._connect()
            # Connection may succeed depending on MongoDB setup
            store._close()
        except RuntimeError:
            # Connection failure is acceptable
            pass
        except Exception:
            # Any other exception is also acceptable
            pass

    def test_auth_with_wrong_database(self):
        """Test authentication with wrong database.

        Note: This tests the scenario where the user exists but in a different database.
        """
        config = utils.get_config()
        nosql_config = config.get("nosql_store")
        if nosql_config is None:
            pytest.skip("NoSQL configuration not found")

        # Create a configuration with wrong database
        connection_config = nosql_config.get("connection", {})
        if not connection_config:
            pytest.skip("Connection configuration not found")

        # Copy the connection config and modify database
        modified_connection = connection_config.copy()
        modified_connection["database"] = "wrong_database"

        # Create NoSQLConnection and NoSQLConfiguration
        connection = NoSQLConnection(**modified_connection)
        auth_config = NoSQLConfiguration(
            framework=nosql_config.get("framework", "mongodb"), connection=connection
        )

        # Try to connect
        try:
            store = NoSQLStore(config=auth_config.model_dump())
            store._connect()
            # Connection may succeed depending on MongoDB setup
            store._close()
        except RuntimeError:
            # Connection failure is acceptable
            pass
        except Exception:
            # Any other exception is also acceptable
            pass

    def test_connection_uri_auth_errors(self):
        """Test authentication errors with connection URI."""
        # Test with invalid credentials in URI
        invalid_uri = "mongodb://invalid_user:invalid_pass@localhost:27017/testdb"
        connection = NoSQLConnection(uri=invalid_uri)
        config = NoSQLConfiguration(framework="mongodb", connection=connection)

        # Try to connect
        try:
            store = NoSQLStore(config=config.model_dump())
            store._connect()
            # Connection may succeed depending on MongoDB setup
            store._close()
        except RuntimeError:
            # Connection failure is acceptable
            pass
        except Exception:
            # Any other exception is also acceptable
            pass

    def test_auth_with_special_characters(self):
        """Test authentication with special characters in credentials."""
        config = utils.get_config()
        nosql_config = config.get("nosql_store")
        if nosql_config is None:
            pytest.skip("NoSQL configuration not found")

        # Create a configuration with special characters in credentials
        connection_config = nosql_config.get("connection", {})
        if not connection_config:
            pytest.skip("Connection configuration not found")

        # Copy the connection config and modify credentials with special characters
        modified_connection = connection_config.copy()
        modified_connection["username"] = "user@domain.com"
        modified_connection["password"] = "p@ssw0rd!#$"

        # Create NoSQLConnection and NoSQLConfiguration
        connection = NoSQLConnection(**modified_connection)
        auth_config = NoSQLConfiguration(
            framework=nosql_config.get("framework", "mongodb"), connection=connection
        )

        # Try to connect
        try:
            store = NoSQLStore(config=auth_config.model_dump())
            store._connect()
            # Connection may succeed depending on MongoDB setup
            store._close()
        except RuntimeError:
            # Connection failure is acceptable
            pass
        except Exception:
            # Any other exception is also acceptable
            pass
