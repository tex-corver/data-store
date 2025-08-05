"""Edge case tests for MongoDB bulk operations.

These tests validate behavior with edge cases in bulk operations.
"""

import pytest
from bson import ObjectId

from data_store.nosql_store.nosql_store import NoSQLStore

# Test collection name
TEST_COLLECTION = "test_collection_bulk_edge_cases"


@pytest.fixture(autouse=True)
def cleanup_bulk_collection(mongodb_store):
    """Clean up bulk test collection before and after each test."""
    try:
        mongodb_store.delete(TEST_COLLECTION, {})
    except Exception:
        pass
    yield
    try:
        mongodb_store.delete(TEST_COLLECTION, {})
    except Exception:
        pass


class TestBulkEdgeCases:
    """Test MongoDB bulk operation edge cases."""

    def test_bulk_insert_empty_array(self, mongodb_store):
        """Test bulk insert with empty array."""
        with pytest.raises(ValueError):
            mongodb_store.bulk_insert(TEST_COLLECTION, [])

    def test_bulk_insert_single_document(self, mongodb_store):
        """Test bulk insert with single document."""
        docs = [{"name": "Single Doc Test", "value": 1}]
        result = mongodb_store.bulk_insert(TEST_COLLECTION, docs)
        assert len(result) == 1
        assert isinstance(result[0], str)

    def test_bulk_insert_duplicate_keys(self, mongodb_store):
        """Test bulk insert with duplicate keys in same batch."""
        docs = [
            {"_id": "test_id", "name": "Duplicate Key 1"},
            {"_id": "test_id", "name": "Duplicate Key 2"},
        ]
        with pytest.raises(Exception):
            mongodb_store.bulk_insert(TEST_COLLECTION, docs)

    def test_bulk_insert_mixed_valid_invalid(self, mongodb_store):
        """Test bulk insert with mixed valid and invalid documents."""
        docs = [
            {"name": "Valid Doc 1"},
            {"name": "Valid Doc 2"},
            "invalid_document",
            {"name": "Valid Doc 3"},
        ]
        with pytest.raises(Exception):
            mongodb_store.bulk_insert(TEST_COLLECTION, docs)

    def test_bulk_update_empty_array(self, mongodb_store):
        """Test bulk update with empty array."""
        with pytest.raises(ValueError):
            mongodb_store.bulk_update(TEST_COLLECTION, {}, [])

    def test_bulk_update_conflicting_operations(self, mongodb_store):
        """Test bulk update with conflicting operations."""
        # First insert some documents
        docs = [{"name": f"Doc {i}", "value": i} for i in range(3)]
        mongodb_store.bulk_insert(TEST_COLLECTION, docs)

        # Try conflicting updates
        updates = [{"$set": {"value": 10}}, {"$inc": {"value": 5}}]
        with pytest.raises(Exception):
            mongodb_store.bulk_update(TEST_COLLECTION, {}, updates)

    @pytest.mark.skip(reason="Bulk delete with empty filters is allowed")
    def test_bulk_delete_empty_filters(self, mongodb_store):
        """Test bulk delete with empty filters array."""
        with pytest.raises(ValueError):
            mongodb_store.bulk_delete(TEST_COLLECTION, [])

    def test_bulk_delete_partial_failures(self, mongodb_store):
        """Test bulk delete with filters that cause partial failures."""
        # First insert some documents
        docs = [{"name": f"Doc {i}", "value": i} for i in range(3)]
        mongodb_store.bulk_insert(TEST_COLLECTION, docs)

        # Try deleting with some invalid filters
        filters = [
            {"value": 0},  # Valid
            "invalid_filter",  # Invalid
            {"value": 2},  # Valid
        ]
        with pytest.raises(Exception):
            mongodb_store.bulk_delete(TEST_COLLECTION, filters)
