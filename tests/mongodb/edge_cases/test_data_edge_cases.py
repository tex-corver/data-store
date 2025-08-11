"""Edge case tests for MongoDB data handling.

These tests validate behavior with edge cases in data handling.
"""

from re import S
from tkinter import SE
import pytest
from bson import ObjectId

from data_store.nosql_store.nosql_store import NoSQLStore

# Test collection name
TEST_COLLECTION = "test_collection_data_edge_cases"

class TestDataEdgeCases:
    """Test MongoDB data handling edge cases."""

    def test_empty_document_insert(self, mongodb_store):
        """Test inserting an empty document."""
        # Insert an empty document
        with pytest.raises(ValueError, match="data cannot be None"):
            inserted_id = mongodb_store.insert(TEST_COLLECTION, {})

    def test_large_document_insert(self, mongodb_store):
        """Test inserting a large document.

        Note: MongoDB has a 16MB document size limit.
        """
        # Create a large document (but under the 16MB limit)
        large_document = {
            "name": "Large Document",
            "data": "x" * 1000000,  # 1MB string
            "array": list(range(10000)),  # Large array
            "nested": {
                f"key_{i}": f"value_{i}" for i in range(1000)
            },  # Large nested object
        }

        # Insert the large document
        inserted_id = mongodb_store.insert(TEST_COLLECTION, large_document)
        assert inserted_id is not None

        # Verify the document was inserted
        results = mongodb_store.find(TEST_COLLECTION, {"name": "Large Document"})
        assert len(results) == 1
        assert len(results[0]["data"]) == 1000000

    def test_document_with_special_characters(self, mongodb_store):
        """Test inserting documents with special characters."""
        special_doc = {
            "name": "Special Characters Test",
            "unicode": "Unicode: 你好, 🚀, 🇺🇸",
            "symbols": "!@#$%^&*()_+-=[]{}|;':\",./<>?",
            "whitespace": "  \t\n  ",
            "null_char": "\x00",
            "backslash": "\\",
            "quotes": "\"'",
        }

        # Insert document with special characters
        inserted_id = mongodb_store.insert(TEST_COLLECTION, special_doc)
        assert inserted_id is not None

        # Verify the document was inserted correctly
        results = mongodb_store.find(
            TEST_COLLECTION, {"name": "Special Characters Test"}
        )
        assert len(results) == 1
        assert results[0]["unicode"] == special_doc["unicode"]
        assert results[0]["symbols"] == special_doc["symbols"]

    def test_document_with_none_values(self, mongodb_store):
        """Test inserting documents with None values."""
        none_doc = {
            "name": "None Values Test",
            "value1": None,
            "value2": "some value",
            "value3": None,
        }

        # Insert document with None values
        inserted_id = mongodb_store.insert(TEST_COLLECTION, none_doc)
        assert inserted_id is not None

        # Verify the document was inserted
        results = mongodb_store.find(TEST_COLLECTION, {"name": "None Values Test"})
        assert len(results) == 1
        assert results[0]["value1"] is None
        assert results[0]["value2"] == "some value"
        assert results[0]["value3"] is None

    def test_update_with_empty_document(self, mongodb_store):
        """Test updating with an empty document."""
        # Insert a document first
        original_doc = {"name": "Update Test", "value": "original"}
        mongodb_store.insert(TEST_COLLECTION, original_doc)

        # Update with an empty document (should not change anything)
        with pytest.raises(ValueError, match="update_data cannot be None"):
            modified_count = mongodb_store.update(
                TEST_COLLECTION,
                filters={"name": "Update Test"},
                update_data={},
                upsert=False,
            )

    def test_find_with_none_filter(self, mongodb_store):
        """Test finding documents with None filter."""
        # Insert some documents
        doc1 = {"name": "None Filter Test 1", "type": "test"}
        doc2 = {"name": "None Filter Test 2", "type": "test"}
        mongodb_store.insert(TEST_COLLECTION, doc1)
        mongodb_store.insert(TEST_COLLECTION, doc2)

        # Find with None filter (should find all)
        results = mongodb_store.find(TEST_COLLECTION, filters=None)
        assert len(results) >= 2

        # Find with empty dict filter (should also find all)
        results2 = mongodb_store.find(TEST_COLLECTION, filters={})
        assert len(results2) >= 2

    def test_delete_with_empty_filter(self, mongodb_store):
        """Test deleting documents with empty filter.

        WARNING: This will delete ALL documents in the collection.
        In a real application, this should be used with caution.
        """
        # Insert some documents
        for i in range(5):
            doc = {"name": f"Delete Test {i}", "type": "delete_test"}
            mongodb_store.insert(TEST_COLLECTION, doc)

        # Verify documents were inserted
        results = mongodb_store.find(TEST_COLLECTION, {"type": "delete_test"})
        assert len(results) == 5

        # Delete with empty filter (commented out for safety)
        # deleted_count = mongodb_store.delete(TEST_COLLECTION, {})
        # assert deleted_count == 5
