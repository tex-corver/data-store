import pytest

COLLECTION = "test_count_collection"


class TestCount:
    """Test count operation."""

    # @pytest.mark.skip(reason="Skipping count test for now")
    @pytest.mark.collection(COLLECTION)
    def test_count_documents(self, mongodb_store):
        """Test counting documents in a collection."""
        # Insert dummy documents
        mongodb_store.insert(COLLECTION, {"type": "count_test"})
        mongodb_store.insert(COLLECTION, {"type": "count_test"})
        mongodb_store.insert(COLLECTION, {"type": "other_test"})

        # Count documents with type 'count_test'
        count = mongodb_store.count(COLLECTION, {"type": "count_test"})
        assert count == 2

        # Count documents with type 'other_test'
        count = mongodb_store.count(COLLECTION, {"type": "other_test"})
        assert count == 1

        # Count all documents
        count = mongodb_store.count(COLLECTION, {})
        assert count == 3
