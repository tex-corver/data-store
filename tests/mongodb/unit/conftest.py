"""MongoDB-specific fixtures for tests."""

import pytest
import utils

from data_store.nosql_store.nosql_store import NoSQLStore

TEST_COLLECTION = "test_collection_e2e"

logger = utils.get_logger(__name__)


@pytest.fixture(scope="function")
def mongodb_store(request: pytest.FixtureRequest):
    """Create a NoSQLStore instance for MongoDB testing with proper cleanup."""
    store = None
    try:
        store = NoSQLStore()
        store._connect()
        collection = request.node.get_closest_marker("collection")
        if collection:
            # If a collection name is provided via marker, use it
            collection_name = collection.args[0]
        else:
            collection_name = TEST_COLLECTION

        # Ensure clean state before test
        _safe_cleanup(store, collection_name)
        yield store
        _safe_cleanup(store, collection_name)

    finally:
        # Cleanup after test, even if test fails
        if store:
            try:
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
