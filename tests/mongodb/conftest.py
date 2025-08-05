"""MongoDB-specific fixtures for tests."""

import pytest
import utils

from data_store.nosql_store.nosql_store import NoSQLStore

TEST_COLLECTION = "test_collection_e2e"


@pytest.fixture(scope="module")
def mongodb_store():
    """Create a NoSQLStore instance for MongoDB testing."""
    config = utils.get_config().get("nosql_store")
    store: NoSQLStore = NoSQLStore(config=config)
    store._connect()
    yield store
    store._close()


@pytest.fixture(autouse=True)
def cleanup_collection(mongodb_store):
    """Clean up test collection before and after each test."""
    try:
        mongodb_store.delete(TEST_COLLECTION, {})
    except Exception:
        pass
    yield
    try:
        mongodb_store.delete(TEST_COLLECTION, {})
    except Exception:
        pass
