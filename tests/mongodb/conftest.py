"""MongoDB-specific fixtures for tests."""

import pytest
import utils

from data_store.nosql_store.nosql_store import NoSQLStore

TEST_COLLECTION = "test_collection_e2e"


@pytest.fixture
def mongodb_store():
    """Create a NoSQLStore instance for MongoDB testing."""
    config = utils.get_config().get("nosql_store")
    store: NoSQLStore = NoSQLStore(config=config)
    store._connect()
    store.bulk_delete(TEST_COLLECTION, {})  # Clear the collection before tests

    yield store
    store._close()
    store.bulk_delete(
        TEST_COLLECTION, {}
    )  # cheat because delete filters must not be empty
