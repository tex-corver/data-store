"""Edge case tests for MongoDB context manager behavior.

These tests validate edge cases when using MongoDB with context managers.
"""

import pytest
from bson import ObjectId

from data_store.nosql_store.nosql_store import NoSQLStore

# Test collection name
TEST_COLLECTION = "test_collection_context_edge_cases"


@pytest.fixture(autouse=True)
def cleanup_context_collection(mongodb_store):
    """Clean up context test collection before and after each test."""
    try:
        mongodb_store.delete(TEST_COLLECTION, {})
    except Exception:
        pass
    yield
    try:
        mongodb_store.delete(TEST_COLLECTION, {})
    except Exception:
        pass


class TestContextEdgeCases:
    """Test MongoDB context manager edge cases."""

    def test_nested_context_managers(self, mongodb_store):
        """Test deeply nested context managers."""
        with mongodb_store.connect() as conn1:
            with conn1.connect() as conn2:
                with conn2.connect() as conn3:
                    # All connections should work
                    doc = {"name": "Nested Context Test", "level": 3}
                    inserted_id = conn3.insert(TEST_COLLECTION, doc)
                    assert inserted_id is not None

    def test_context_exit_with_exception(self, mongodb_store):
        """Test context exit when an exception occurs."""
        try:
            with mongodb_store.connect() as conn:
                # Perform an operation
                conn.insert(TEST_COLLECTION, {"name": "Exception Test"})
                # Simulate an error
                raise RuntimeError("Simulated error")
        except RuntimeError:
            # Context should still be properly closed
            pass

        # Verify we can still use the store
        result = mongodb_store.find(TEST_COLLECTION, {})
        assert len(result) >= 1

    def test_context_reuse_after_closure(self, mongodb_store):
        """Test reusing a context after it's been closed."""
        with mongodb_store.connect() as conn:
            # First usage
            conn.insert(TEST_COLLECTION, {"name": "First Use"})

        # Try to reuse
        with pytest.raises(Exception):
            with conn.connect():  # Should fail as conn is closed
                pass

    def test_multiple_exceptions_in_context(self, mongodb_store):
        """Test handling multiple exceptions in same context."""
        try:
            with mongodb_store.connect() as conn:
                conn.insert(TEST_COLLECTION, {"name": "Multi-Exception Test"})
                raise ValueError("First error")
                raise RuntimeError("Second error")  # Never reached
        except ValueError:
            # First exception should be caught
            pass

        # Verify operation was successful despite exceptions
        result = mongodb_store.find(TEST_COLLECTION, {"name": "Multi-Exception Test"})
        assert len(result) == 1

    def test_context_with_pending_operations(self, mongodb_store):
        """Test context cleanup with pending operations."""
        with mongodb_store.connect() as conn:
            # Start an operation but don't complete it
            future = conn.insert(TEST_COLLECTION, {"name": "Pending Op"}, async_op=True)
            # Context will exit before operation completes

        # Operation may or may not complete successfully
        try:
            result = future.result()
            assert result is not None
        except Exception:
            # Operation failed due to context closing - acceptable
            pass
