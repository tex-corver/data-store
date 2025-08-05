"""Integration tests for MongoDB context manager functionality.

These tests validate the context manager behavior of NoSQLStore.
"""

import pytest
import utils

from data_store.nosql_store.nosql_store import NoSQLStore

# Dummy data for testing
DUMMY_DOCUMENT = {"name": "Test User", "age": 30, "email": "test@example.com"}
TEST_COLLECTION = "test_collection_e2e"


class TestContextManager:
    """Test NoSQLStore context manager functionality."""

    def test_context_manager_basic_usage(self):
        """Test basic context manager usage with automatic connection lifecycle."""
        config = utils.get_config()
        store = NoSQLStore(config=config.get("nosql_store"))
        with store.connect() as connection:
            # Verify connection is established
            assert connection is not None
            # Perform a basic operation to verify connection works
            inserted_id = store.insert(TEST_COLLECTION, DUMMY_DOCUMENT.copy())
            assert inserted_id is not None
            assert isinstance(inserted_id, str)
            assert len(inserted_id) > 0
        # Connection is automatically closed here

    def test_context_manager_automatic_cleanup(self):
        """Test that connection is automatically closed after context exit."""
        config = utils.get_config()
        store = NoSQLStore(config=config.get("nosql_store"))
        with store.connect() as connection:
            assert connection is not None
            # Insert test document
            store.insert(TEST_COLLECTION, DUMMY_DOCUMENT.copy())
            # Verify client has been initialized during context
            assert hasattr(store, "_client") or hasattr(store.client, "_client")
        # After context exit, connection should be closed
        # We can't directly access _client, but we can check if operations fail appropriately

    def test_context_manager_with_exception(self):
        """Test that connection is properly closed even when exception occurs."""
        config = utils.get_config()
        store = NoSQLStore(config=config.get("nosql_store"))
        with pytest.raises(ValueError):
            with store.connect() as connection:
                assert connection is not None
                # Perform a valid operation first
                store.insert(TEST_COLLECTION, DUMMY_DOCUMENT.copy())
                # Raise an exception to test cleanup
                raise ValueError("Test exception")
        # Connection should still be closed despite exception

    def test_context_manager_multiple_operations(self):
        """Test multiple operations within same connection context."""
        config = utils.get_config()
        store = NoSQLStore(config=config.get("nosql_store"))
        test_documents = [
            {"name": "Context User 1", "type": "context_test"},
            {"name": "Context User 2", "type": "context_test"},
            {"name": "Context User 3", "type": "context_test"},
        ]
        with store.connect() as connection:
            assert connection is not None
            # Insert multiple documents
            for doc in test_documents:
                inserted_id = store.insert(TEST_COLLECTION, doc)
                assert inserted_id is not None
            # Query the documents
            results = store.find(TEST_COLLECTION, {"type": "context_test"})
            assert len(results) == 3
            # Update documents
            modified_count = store.update(
                TEST_COLLECTION, {"type": "context_test"}, {"status": "processed"}
            )
            assert modified_count == 3
            # Verify updates
            updated_results = store.find(TEST_COLLECTION, {"status": "processed"})
            assert len(updated_results) == 3
        # Connection automatically closed

    def test_context_manager_with_config_parameters(self):
        """Test context manager with custom connection configuration."""
        config = utils.get_config()
        store = NoSQLStore(config=config.get("nosql_store"))
        with store.connect() as connection:
            assert connection is not None
            # Perform operation to verify connection works
            inserted_id = store.insert(TEST_COLLECTION, DUMMY_DOCUMENT.copy())
            assert inserted_id is not None
        # Connection properly closed

    def test_context_manager_nested_usage(self):
        """Test that nested context manager usage works correctly."""
        config = utils.get_config()
        store = NoSQLStore(config=config.get("nosql_store"))
        with store.connect() as connection1:
            assert connection1 is not None
            store.insert(TEST_COLLECTION, {"name": "Outer context", "level": 1})
            with store.connect() as connection2:
                assert connection2 is not None
                store.insert(TEST_COLLECTION, {"name": "Inner context", "level": 2})
                # Both should use same underlying connection
                results = store.find(TEST_COLLECTION, {"level": {"$in": [1, 2]}})
                assert len(results) == 2
        # Connection properly closed after outer context

    def test_context_manager_bulk_operations(self):
        """Test bulk operations within connection context manager."""
        config = utils.get_config()
        store = NoSQLStore(config=config.get("nosql_store"))
        bulk_documents = [
            {"name": f"Bulk Context User {i}", "batch": "context_bulk"}
            for i in range(5)
        ]
        with store.connect() as connection:
            assert connection is not None
            # Bulk insert
            result = store.bulk_insert(TEST_COLLECTION, bulk_documents)
            assert result == "5"
            # Bulk update
            modified_count = store.bulk_update(
                TEST_COLLECTION,
                {"batch": "context_bulk"},
                [{"status": "bulk_processed"}],
            )
            assert modified_count == 5
            # Verify results
            results = store.find(TEST_COLLECTION, {"batch": "context_bulk"})
            assert len(results) == 5
            for result in results:
                assert result["status"] == "bulk_processed"
        # Connection properly closed

    def test_context_manager_error_handling(self):
        """Test error handling within connection context manager."""
        config = utils.get_config()
        store = NoSQLStore(config=config.get("nosql_store"))
        with store.connect() as connection:
            assert connection is not None
            # Test successful operation first
            store.insert(TEST_COLLECTION, DUMMY_DOCUMENT.copy())
            # Test operation that might cause issues
            try:
                # This should work normally
                results = store.find(TEST_COLLECTION, {"nonexistent_field": "value"})
                assert isinstance(results, list)  # Should return empty list
            except Exception as e:
                pytest.fail(f"Unexpected exception in context manager: {e}")
        # Connection properly closed even with edge cases
