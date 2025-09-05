"""MongoDB-specific fixtures for tests."""

import pytest

from data_store.nosql_store.nosql_store import NoSQLStore
import utils

logger = utils.get_logger(__name__)

@pytest.fixture(scope="function")
def mongodb_store():
    """Create a NoSQLStore instance for MongoDB testing with proper cleanup."""
    store = None
    try:
        store = NoSQLStore()
        store._connect()
        
        # Ensure clean state before test
        _cleanup_all_collections(store)

        
        yield store
        
    finally:
        # Cleanup after test, even if test fails
        if store:
            try:
                _cleanup_all_collections(store)
                store._close()
            except Exception as e:
                logger.warning(f"Error during teardown: {e}")

# Track collections used during test session
_test_collections: set[str] = set()

def _cleanup_all_collections(store: NoSQLStore):
    """Safely cleanup all registered test collections."""
    # Default collections to always clean
    default_collections = {
        # "test_collection_e2e",
        # "test_collection_auth_errors",
        # "test_collection_bulk_edge_cases", 
        # "test_collection_context_edge_cases",
        # "test_collection_data_edge_cases",
        # "test_collection_error_handling"
    }
    
    # Combine registered and default collections
    all_collections = _test_collections.union(default_collections)
    
    for collection in all_collections:
        try:
            deleted_count = store.bulk_delete(collection, {})
            logger.debug(f"Cleaned {deleted_count} documents from {collection}")
        except Exception as e:
            logger.warning(f"Error during collection cleanup for {collection}: {e}")

def register_test_collection(collection_name: str):
    """Register a collection name for cleanup tracking."""
    _test_collections.add(collection_name)


# Auto-register collections from test files
def pytest_runtest_setup(item):
    """Auto-discover and register TEST_COLLECTION constants from test modules."""
    if hasattr(item.module, 'TEST_COLLECTION'):
        register_test_collection(item.module.TEST_COLLECTION)