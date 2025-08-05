"""Integration tests for MongoDB connection pooling.

These tests validate connection pooling behavior in MongoDB.
"""

import pytest
import utils

from data_store.nosql_store.nosql_store import NoSQLStore

# Dummy data for testing
DUMMY_DOCUMENT = {"name": "Test User", "age": 30, "email": "test@example.com"}
TEST_COLLECTION = "test_collection_pooling"


class TestConnectionPooling:
    """Test MongoDB connection pooling functionality."""

    def test_connection_pooling_basic(self):
        """Test basic connection pooling behavior.

        This test verifies that multiple operations can be performed
        with the same store instance, utilizing connection pooling.
        """
        config = utils.get_config()
        store = NoSQLStore(config=config.get("nosql_store"))

        # Perform multiple operations with the same store instance
        for i in range(5):
            doc = {"name": f"User {i}", "age": 20 + i, "type": "pooling_test"}
            inserted_id = store.insert(TEST_COLLECTION, doc)
            assert inserted_id is not None

        # Verify all documents were inserted
        results = store.find(TEST_COLLECTION, {"type": "pooling_test"})
        assert len(results) == 5

        # Clean up
        deleted_count = store.delete(TEST_COLLECTION, {"type": "pooling_test"})
        assert deleted_count == 5

    def test_connection_pooling_with_context_manager(self):
        """Test connection pooling with context manager.

        This test verifies that the context manager properly
        manages connection pooling.
        """
        config = utils.get_config()
        store = NoSQLStore(config=config.get("nosql_store"))

        with store.connect() as connection:
            # Perform multiple operations within the same context
            for i in range(3):
                doc = {
                    "name": f"Context User {i}",
                    "age": 25 + i,
                    "type": "context_pooling_test",
                }
                inserted_id = store.insert(TEST_COLLECTION, doc)
                assert inserted_id is not None

            # Verify all documents were inserted
            results = store.find(TEST_COLLECTION, {"type": "context_pooling_test"})
            assert len(results) == 3

    def test_multiple_store_instances_connection_pooling(self):
        """Test connection pooling with multiple store instances.

        This test verifies that multiple store instances can
        operate independently while sharing connection pooling resources.
        """
        config = utils.get_config()

        # Create multiple store instances
        store1 = NoSQLStore(config=config.get("nosql_store"))
        store2 = NoSQLStore(config=config.get("nosql_store"))

        # Insert documents using different store instances
        doc1 = {"name": "Store1 User", "type": "multi_store_test"}
        doc2 = {"name": "Store2 User", "type": "multi_store_test"}

        inserted_id1 = store1.insert(TEST_COLLECTION, doc1)
        inserted_id2 = store2.insert(TEST_COLLECTION, doc2)

        assert inserted_id1 is not None
        assert inserted_id2 is not None

        # Verify both documents exist
        results = store1.find(TEST_COLLECTION, {"type": "multi_store_test"})
        assert len(results) == 2

        # Clean up using different store instance
        deleted_count = store2.delete(TEST_COLLECTION, {"type": "multi_store_test"})
        assert deleted_count == 2
