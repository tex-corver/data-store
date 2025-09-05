"""MongoDB-specific fixtures for tests."""

import pytest

from data_store.nosql_store.nosql_store import NoSQLStore
import utils

TEST_COLLECTION = "test_collection_e2e"

logger = utils.get_logger(__name__)

@pytest.fixture(scope="function")
def mongodb_store():
    """Create a NoSQLStore instance for MongoDB testing with proper cleanup."""
    store = None
    try:
        store = NoSQLStore()
        store._connect()
        
        # Ensure clean state before test
        _safe_cleanup(store, TEST_COLLECTION)
        
        yield store
        
    finally:
        # Cleanup after test, even if test fails
        if store:
            try:
                _safe_cleanup(store, TEST_COLLECTION)
                store._close()
            except Exception as e:
                logger.warning(f"Error during teardown: {e}")


def _safe_cleanup(store: NoSQLStore, collection: str):
    """Safely cleanup collection with error handling."""
    try:
        # Use empty dict {} to delete all documents in collection
        deleted_count = store.bulk_delete(collection, {})
        logger.debug(f"Cleaned {deleted_count} documents from {collection}")
    except Exception as e:
        logger.warning(f"Error during collection cleanup: {e}")
        # Don't re-raise to avoid breaking tests


@pytest.fixture(scope="function")
def clean_mongodb_store(mongodb_store):
    """Alias for mongodb_store - provides clean collection state.
    
    Use this instead of combining mongodb_store + clean_collection fixtures.
    """
    return mongodb_store