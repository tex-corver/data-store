"""Unit tests for MongoDB bulk operations.

These tests validate bulk insert, update, and delete operations.
"""

import pytest

from data_store.nosql_store.nosql_store import NoSQLStore

# Dummy data for testing
DUMMY_DOCUMENT = {"name": "Test User", "age": 30, "email": "test@example.com"}
DUMMY_DOCUMENT_2 = {"name": "Test User 2", "age": 25, "email": "test2@example.com"}

TEST_COLLECTION = "test_collection_e2e"


class TestBulkOperations:
    """Test bulk operations: bulk_insert, bulk_update, bulk_delete."""

    def test_bulk_insert_documents(self, mongodb_store):
        """Test bulk inserting multiple documents."""
        test_documents = [
            {"name": "Bulk User 1", "age": 25, "type": "bulk_test"},
            {"name": "Bulk User 2", "age": 30, "type": "bulk_test"},
            {"name": "Bulk User 3", "age": 35, "type": "bulk_test"},
        ]
        result = mongodb_store.bulk_insert(TEST_COLLECTION, test_documents)
        assert result == "3"
        results = mongodb_store.find(TEST_COLLECTION, {"type": "bulk_test"})
        assert len(results) == 3

    def test_bulk_update_documents_without_upsert(self, mongodb_store):
        """Test bulk updating multiple documents without upsert."""
        test_documents = [
            {"name": "Update User 1", "age": 25, "status": "pending"},
            {"name": "Update User 2", "age": 30, "status": "pending"},
        ]
        mongodb_store.bulk_insert(TEST_COLLECTION, test_documents)
        update_data = [{"status": "processed", "updated_at": "2024-01-01"}]
        modified_count = mongodb_store.bulk_update(
            TEST_COLLECTION,
            filters={"status": "pending"},
            update_data=update_data,
            upsert=False,
        )
        assert modified_count == 2
        results = mongodb_store.find(TEST_COLLECTION, {"status": "processed"})
        assert len(results) == 2

    def test_bulk_update_documents_with_upsert(self, mongodb_store):
        """Test bulk updating multiple documents with upsert enabled."""
        filters = {"category": "new_category"}
        update_data = [
            {"name": "New Item 1", "price": 100, "category": "new_category"},
            {"name": "New Item 2", "price": 200, "category": "new_category"},
        ]
        modified_count = mongodb_store.bulk_update(
            TEST_COLLECTION, filters=filters, update_data=update_data, upsert=True
        )
        assert modified_count >= 0
        results = mongodb_store.find(TEST_COLLECTION, {"category": "new_category"})
        assert len(results) >= 1

    def test_bulk_delete_documents_with_dict_filters(self, mongodb_store):
        """Test bulk deleting documents using dict filters."""
        test_documents = [
            {"name": "Delete User 1", "status": "obsolete"},
            {"name": "Delete User 2", "status": "obsolete"},
            {"name": "Keep User", "status": "active"},
        ]
        mongodb_store.bulk_insert(TEST_COLLECTION, test_documents)
        deleted_count = mongodb_store.bulk_delete(
            TEST_COLLECTION, {"status": "obsolete"}
        )
        assert deleted_count == 2
        results = mongodb_store.find(TEST_COLLECTION)
        assert len(results) == 1
        assert results[0]["status"] == "active"

    def test_bulk_delete_documents_with_list_filters(self, mongodb_store):
        """Test bulk deleting documents using list of filters."""
        test_documents = [
            {"name": "User 1", "status": "inactive", "type": "test"},
            {"name": "User 2", "verified": False, "type": "test"},
            {"name": "User 3", "status": "active", "verified": True, "type": "test"},
        ]
        mongodb_store.bulk_insert(TEST_COLLECTION, test_documents)
        filters = [{"status": "inactive"}, {"verified": False}]
        deleted_count = mongodb_store.bulk_delete(TEST_COLLECTION, filters)
        assert deleted_count == 2
        results = mongodb_store.find(TEST_COLLECTION, {"type": "test"})
        assert len(results) == 1
        assert results[0]["status"] == "active"
        assert results[0]["verified"] is True
