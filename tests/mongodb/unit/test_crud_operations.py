"""Unit tests for MongoDB CRUD operations.

These tests validate insert, find, update, and delete operations.
"""

import pytest

from data_store.nosql_store.nosql_store import NoSQLStore

# Dummy data for testing
DUMMY_DOCUMENT = {"name": "Test User", "age": 30, "email": "test@example.com"}
DUMMY_DOCUMENT_2 = {"name": "Test User 2", "age": 25, "email": "test2@example.com"}
DUMMY_UPDATED_DOCUMENT = {"age": 35, "status": "updated"}

TEST_COLLECTION = "test_collection_e2e"


class TestSingleDocumentOperations:
    """Test single document operations: insert, find."""

    def test_insert_document(self, mongodb_store):
        """Test inserting a single document into a collection."""
        test_document = DUMMY_DOCUMENT.copy()
        inserted_id = mongodb_store.insert(TEST_COLLECTION, test_document)
        assert inserted_id is not None
        assert isinstance(inserted_id, str)
        assert len(inserted_id) > 0

    def test_find_documents_with_filters(self, mongodb_store):
        """Test finding documents in a collection with filters."""
        doc1 = DUMMY_DOCUMENT.copy()
        doc2 = DUMMY_DOCUMENT_2.copy()
        mongodb_store.insert(TEST_COLLECTION, doc1)
        mongodb_store.insert(TEST_COLLECTION, doc2)
        results = mongodb_store.find(TEST_COLLECTION, filters={"age": 30})
        assert len(results) == 1
        assert results[0]["name"] == "Test User"
        assert results[0]["age"] == 30

    def test_find_documents_without_filters(self, mongodb_store):
        """Test finding all documents without filters."""
        doc1 = DUMMY_DOCUMENT.copy()
        doc2 = DUMMY_DOCUMENT_2.copy()
        mongodb_store.insert(TEST_COLLECTION, doc1)
        mongodb_store.insert(TEST_COLLECTION, doc2)
        results = mongodb_store.find(TEST_COLLECTION)
        assert len(results) == 2

    def test_find_documents_with_projections(self, mongodb_store):
        """Test finding documents with specific field projections."""
        test_document = DUMMY_DOCUMENT.copy()
        mongodb_store.insert(TEST_COLLECTION, test_document)
        results = mongodb_store.find(TEST_COLLECTION, projections=["name", "age"])
        assert len(results) == 1
        assert "name" in results[0]
        assert "age" in results[0]
        assert "email" not in results[0]

    def test_find_documents_with_skip_limit(self, mongodb_store):
        """Test finding documents with skip and limit parameters."""
        for i in range(5):
            doc = {"name": f"User {i}", "age": 20 + i}
            mongodb_store.insert(TEST_COLLECTION, doc)
        results = mongodb_store.find(TEST_COLLECTION, skip=2, limit=2)
        assert len(results) == 2


class TestUpdateOperations:
    """Test document update operations with and without upsert."""

    def test_update_documents_without_upsert(self, mongodb_store):
        """Test updating existing documents without upsert."""
        test_document = DUMMY_DOCUMENT.copy()
        mongodb_store.insert(TEST_COLLECTION, test_document)
        modified_count = mongodb_store.update(
            TEST_COLLECTION,
            filters={"name": "Test User"},
            update_data=DUMMY_UPDATED_DOCUMENT,
            upsert=False,
        )
        assert modified_count == 1
        results = mongodb_store.find(TEST_COLLECTION, filters={"name": "Test User"})
        assert len(results) == 1
        assert results[0]["age"] == 35
        assert results[0]["status"] == "updated"

    def test_update_documents_with_upsert(self, mongodb_store):
        """Test updating documents with upsert enabled for non-existing document."""
        filters = {"name": "Non Existing User"}
        update_data = {"name": "Non Existing User", "age": 40, "status": "created"}
        modified_count = mongodb_store.update(
            TEST_COLLECTION, filters=filters, update_data=update_data, upsert=True
        )
        # Note: MongoDB returns 0 for modified_count when upserting
        assert modified_count >= 0
        results = mongodb_store.find(
            TEST_COLLECTION, filters={"name": "Non Existing User"}
        )
        assert len(results) == 1
        assert results[0]["age"] == 40
        assert results[0]["status"] == "created"


class TestDeletionOperations:
    """Test document deletion operations."""

    def test_delete_documents(self, mongodb_store):
        """Test deleting documents from a collection."""
        doc1 = DUMMY_DOCUMENT.copy()
        doc2 = DUMMY_DOCUMENT_2.copy()
        doc1["status"] = "to_delete"
        doc2["status"] = "to_delete"
        mongodb_store.insert(TEST_COLLECTION, doc1)
        mongodb_store.insert(TEST_COLLECTION, doc2)
        deleted_count = mongodb_store.delete(TEST_COLLECTION, {"status": "to_delete"})
        assert deleted_count == 2
        results = mongodb_store.find(TEST_COLLECTION, {"status": "to_delete"})
        assert len(results) == 0
