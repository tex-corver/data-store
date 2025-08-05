"""Integration tests for basic MongoDB operations.

These tests validate basic CRUD operations work correctly with actual MongoDB connections.
"""

import pytest

from data_store.nosql_store.nosql_store import NoSQLStore

# Dummy data for testing
DUMMY_DOCUMENT = {"name": "Test User", "age": 30, "email": "test@example.com"}
DUMMY_DOCUMENT_2 = {"name": "Test User 2", "age": 25, "email": "test2@example.com"}
DUMMY_UPDATED_DOCUMENT = {"age": 35, "status": "updated"}

TEST_COLLECTION = "test_collection_integration"


class TestBasicOperations:
    """Test basic MongoDB operations without context manager."""

    def test_basic_insert_and_find(self, mongodb_store):
        """Test basic insert and find operations."""
        # Insert a document
        test_document = DUMMY_DOCUMENT.copy()
        inserted_id = mongodb_store.insert(TEST_COLLECTION, test_document)

        # Verify the document was inserted
        assert inserted_id is not None
        assert isinstance(inserted_id, str)
        assert len(inserted_id) > 0

        # Find the document
        results = mongodb_store.find(TEST_COLLECTION, filters={"name": "Test User"})
        assert len(results) == 1
        assert results[0]["name"] == "Test User"
        assert results[0]["age"] == 30

    def test_basic_update_operation(self, mongodb_store):
        """Test basic update operation."""
        # Insert a document first
        test_document = DUMMY_DOCUMENT.copy()
        mongodb_store.insert(TEST_COLLECTION, test_document)

        # Update the document
        modified_count = mongodb_store.update(
            TEST_COLLECTION,
            filters={"name": "Test User"},
            update_data=DUMMY_UPDATED_DOCUMENT,
            upsert=False,
        )

        # Verify the document was updated
        assert modified_count == 1
        results = mongodb_store.find(TEST_COLLECTION, filters={"name": "Test User"})
        assert len(results) == 1
        assert results[0]["age"] == 35
        assert results[0]["status"] == "updated"

    def test_basic_delete_operation(self, mongodb_store):
        """Test basic delete operation."""
        # Insert documents first
        doc1 = DUMMY_DOCUMENT.copy()
        doc2 = DUMMY_DOCUMENT_2.copy()
        doc1["status"] = "to_delete"
        doc2["status"] = "to_delete"
        mongodb_store.insert(TEST_COLLECTION, doc1)
        mongodb_store.insert(TEST_COLLECTION, doc2)

        # Delete documents
        deleted_count = mongodb_store.delete(TEST_COLLECTION, {"status": "to_delete"})

        # Verify documents were deleted
        assert deleted_count == 2
        results = mongodb_store.find(TEST_COLLECTION, {"status": "to_delete"})
        assert len(results) == 0

    def test_basic_bulk_operations(self, mongodb_store):
        """Test basic bulk operations."""
        # Bulk insert
        test_documents = [
            {"name": "Bulk User 1", "age": 25, "type": "bulk_test"},
            {"name": "Bulk User 2", "age": 30, "type": "bulk_test"},
            {"name": "Bulk User 3", "age": 35, "type": "bulk_test"},
        ]
        result = mongodb_store.bulk_insert(TEST_COLLECTION, test_documents)
        assert result == "3"

        # Verify documents exist
        results = mongodb_store.find(TEST_COLLECTION, {"type": "bulk_test"})
        assert len(results) == 3

        # Bulk update
        update_data = [{"status": "processed"}]
        modified_count = mongodb_store.bulk_update(
            TEST_COLLECTION,
            filters={"type": "bulk_test"},
            update_data=update_data,
            upsert=False,
        )
        assert modified_count == 3

        # Verify updates
        results = mongodb_store.find(TEST_COLLECTION, {"status": "processed"})
        assert len(results) == 3

        # Bulk delete
        deleted_count = mongodb_store.bulk_delete(
            TEST_COLLECTION, {"type": "bulk_test"}
        )
        assert deleted_count == 3

        # Verify documents were deleted
        results = mongodb_store.find(TEST_COLLECTION, {"type": "bulk_test"})
        assert len(results) == 0
