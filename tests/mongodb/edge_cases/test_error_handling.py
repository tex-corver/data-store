"""Edge case tests for MongoDB error handling.

These tests validate error handling behavior in various scenarios.
"""

import pytest

from data_store.nosql_store.configurations import NoSQLConnection
from data_store.nosql_store.nosql_store import NoSQLStore

# Test collection name
TEST_COLLECTION = "test_collection_error_handling"


class TestErrorHandling:
    """Test MongoDB error handling scenarios."""

    def test_invalid_collection_name(self, mongodb_store):
        """Test behavior with invalid collection names."""
        # Test with empty collection name
        with pytest.raises(Exception):  # Expect some kind of error
            mongodb_store.insert("", {"test": "data"})

        # Test with None collection name
        with pytest.raises(Exception):  # Expect some kind of error
            mongodb_store.insert(None, {"test": "data"})

    def test_invalid_document_structure(self, mongodb_store):
        """Test behavior with invalid document structures."""
        # Test with None document
        with pytest.raises(Exception):  # Expect some kind of error
            mongodb_store.insert(TEST_COLLECTION, None)

        # Test with non-dict document
        with pytest.raises(Exception):  # Expect some kind of error
            mongodb_store.insert(TEST_COLLECTION, "not a dict")

        # Test with non-dict filters
        with pytest.raises(Exception):  # Expect some kind of error
            mongodb_store.find(TEST_COLLECTION, "not a dict")

    def test_invalid_update_operations(self, mongodb_store):
        """Test behavior with invalid update operations."""
        # Insert a document first
        mongodb_store.insert(TEST_COLLECTION, {"name": "test", "value": "original"})

        # Test update with None filters
        with pytest.raises(Exception):  # Expect some kind of error
            mongodb_store.update(TEST_COLLECTION, None, {"value": "updated"})

        # Test update with None update_data
        with pytest.raises(Exception):  # Expect some kind of error
            mongodb_store.update(TEST_COLLECTION, {"name": "test"}, None)

    def test_invalid_delete_operations(self, mongodb_store):
        """Test behavior with invalid delete operations."""
        # Insert a document first
        mongodb_store.insert(TEST_COLLECTION, {"name": "test", "value": "original"})

        # Test delete with None filters
        with pytest.raises(Exception):  # Expect some kind of error
            mongodb_store.delete(TEST_COLLECTION, None)

    def test_invalid_bulk_operations(self, mongodb_store):
        """Test behavior with invalid bulk operations."""
        # Test bulk_insert with None data
        with pytest.raises(Exception):  # Expect some kind of error
            mongodb_store.bulk_insert(TEST_COLLECTION, None)

        # Test bulk_insert with non-list data
        with pytest.raises(Exception):  # Expect some kind of error
            mongodb_store.bulk_insert(TEST_COLLECTION, "not a list")

        # Test bulk_update with None filters
        with pytest.raises(Exception):  # Expect some kind of error
            mongodb_store.bulk_update(TEST_COLLECTION, None, [{"value": "updated"}])

        # Test bulk_update with None update_data
        with pytest.raises(Exception):  # Expect some kind of error
            mongodb_store.bulk_update(TEST_COLLECTION, {"name": "test"}, None)

        # Test bulk_delete with None filters
        with pytest.raises(Exception):  # Expect some kind of error
            mongodb_store.bulk_delete(TEST_COLLECTION, None)

    def test_connection_error_after_close(self, mongodb_store):
        """Test behavior when operations are attempted after connection is closed."""
        # This is difficult to test with the fixture since it manages connection lifecycle
        # In a real scenario, this would be tested by manually managing the connection
        pass

    def test_duplicate_key_error(self, mongodb_store):
        """Test behavior with duplicate key constraints.

        Note: This requires a collection with a unique index to be meaningful.
        """
        # Insert a document
        doc = {"name": "unique_test", "email": "test@example.com"}
        mongodb_store.insert(TEST_COLLECTION, doc)

        # In a real scenario with unique indexes, inserting a duplicate would fail
        # But without unique indexes, this will succeed
        # This test is more of a placeholder for environments with unique indexes
        doc2 = {"name": "unique_test", "email": "test@example.com"}
        inserted_id = mongodb_store.insert(TEST_COLLECTION, doc2)
        assert inserted_id is not None  # Will succeed without unique indexes

    def test_configuration_validation_errors(self):
        """Test configuration validation error handling."""
        # Test NoSQLConnection validation
        with pytest.raises(ValueError, match="Either 'uri' or 'host' must be provided"):
            NoSQLConnection()

        # Test creating store with invalid configuration
        with pytest.raises(ValueError):
            NoSQLStore(config={"invalid": "config"})
