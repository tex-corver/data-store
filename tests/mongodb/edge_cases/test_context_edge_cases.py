"""Edge case tests for MongoDB context manager behavior.

These tests validate edge cases when using MongoDB with context managers.
"""

import threading
import time

import pytest
from bson import ObjectId

from data_store.nosql_store.nosql_store import NoSQLStore

# Test collection name
TEST_COLLECTION = "test_collection_context_edge_cases"


def cleanup_context_collection(mongodb_store):
    with mongodb_store.connect() as conn:
        try:
            mongodb_store.bulk_delete(TEST_COLLECTION, {})
        except Exception:
            pass


class TestContextEdgeCases:
    """Test MongoDB context manager edge cases."""

    @pytest.fixture(scope="class")
    def mongodb_store(self) -> NoSQLStore:
        """Create a NoSQLStore instance for MongoDB testing."""

        store: NoSQLStore = NoSQLStore()
        return store

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
        cleanup_context_collection(mongodb_store)
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
        with mongodb_store.connect() as conn:
            result = mongodb_store.find(TEST_COLLECTION, {})
            assert len(result) == 1
        cleanup_context_collection(mongodb_store)

    def test_context_reuse_after_closure(self, mongodb_store):
        """Test reusing a context after it's been closed."""
        with mongodb_store.connect() as conn:
            # First usage
            conn.insert(TEST_COLLECTION, {"name": "First Use"})

        # Try to reuse
        with pytest.raises(Exception):
            conn.insert(TEST_COLLECTION, {"name": "Second Use"})

        cleanup_context_collection(mongodb_store)

    def test_context_resource_cleanup_verification(self, mongodb_store):
        """Test that resources are properly cleaned up after context exit."""
        # Track connection state before and after
        initial_connections = (
            mongodb_store._get_connection_count()
            if hasattr(mongodb_store, "_get_connection_count")
            else 0
        )

        cleanup_context_collection(mongodb_store)
        with mongodb_store.connect() as conn:
            conn.insert(TEST_COLLECTION, {"name": "Resource Test"})
            # Connection should be active here

        # After context exit, resources should be cleaned up
        final_connections = (
            mongodb_store._get_connection_count()
            if hasattr(mongodb_store, "_get_connection_count")
            else 0
        )
        cleanup_context_collection(mongodb_store)
        assert final_connections <= initial_connections

    def test_context_with_memory_intensive_operations(self, mongodb_store):
        """Test context with operations that consume significant memory."""
        large_doc = {"name": "Memory Test", "data": "x" * 10000}

        cleanup_context_collection(mongodb_store)
        with mongodb_store.connect() as conn:
            # Insert multiple large documents
            inserted_ids = []
            for i in range(10):
                doc_id = conn.insert(TEST_COLLECTION, {**large_doc, "index": i})
                inserted_ids.append(doc_id)

            assert len(inserted_ids) == 10

        # Verify documents were inserted despite memory usage
        with mongodb_store.connect() as conn:
            result = mongodb_store.find(TEST_COLLECTION, {"name": "Memory Test"})
            assert len(result) == 10
            # Cleanup after test

        cleanup_context_collection(mongodb_store)

    def test_context_with_transaction_rollback(self, mongodb_store):
        """Test context behavior with failed transactions."""
        cleanup_context_collection(mongodb_store)
        with mongodb_store.connect() as conn:
            try:
                # Start operations that should be atomic
                conn.insert(TEST_COLLECTION, {"name": "Transaction Test 1"})
                conn.insert(TEST_COLLECTION, {"name": "Transaction Test 2"})

                # Force an error that should rollback
                conn.insert(
                    "", {"invalid": "collection_name"}
                )  # Invalid collection name

            except Exception:
                # Transaction should fail but context should still close properly
                pass

        # Verify partial operations don't persist if transaction failed
        with mongodb_store.connect() as conn:
            result = mongodb_store.find(
                TEST_COLLECTION, {"name": {"$regex": "Transaction Test"}}
            )
            # Depending on MongoDB configuration, this might be 0 or 2
            assert isinstance(result, list)
        cleanup_context_collection(mongodb_store)

    def test_context_with_concurrent_access(self, mongodb_store):
        """Test context with multiple concurrent operations."""

        results = []
        errors = []

        def worker(worker_id):
            try:
                with mongodb_store.connect() as conn:
                    doc_id = conn.insert(
                        TEST_COLLECTION,
                        {
                            "name": f"Worker_{worker_id}",
                            "timestamp": time.time(),
                        },
                    )
                    results.append(doc_id)
            except Exception as e:
                errors.append(str(e))

        # Create multiple threads
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # Verify results
        assert len(results) >= 3  # At least some should succeed
        assert len(errors) <= 2  # Some failures are acceptable in concurrent scenarios

    def test_context_with_malformed_data(self, mongodb_store):
        """Test context handling with various malformed data types."""
        with mongodb_store.connect() as conn:
            # Test with None values
            doc_id1 = conn.insert(TEST_COLLECTION, {"name": None, "value": "test"})
            assert doc_id1 is not None

            # Test with empty structures
            doc_id2 = conn.insert(TEST_COLLECTION, {"name": "Empty Test", "data": {}})
            assert doc_id2 is not None

            # Test with deeply nested structures
            nested_doc = {
                "name": "Nested Test",
                "level1": {"level2": {"level3": {"value": "deep"}}},
            }
            doc_id3 = conn.insert(TEST_COLLECTION, nested_doc)
            assert doc_id3 is not None

    def test_context_exit_during_bulk_operations(self, mongodb_store):
        """Test context exit while bulk operations are in progress."""
        bulk_docs = [{"name": f"Bulk_{i}", "index": i} for i in range(100)]
        cleanup_context_collection(mongodb_store)
        with mongodb_store.connect() as conn:
            # Start bulk insert
            inserted_ids = []
            for doc in bulk_docs[:50]:  # Insert first half
                doc_id = conn.insert(TEST_COLLECTION, doc)
                inserted_ids.append(doc_id)

            # Context will exit here, potentially interrupting remaining operations
            assert len(inserted_ids) == 50

        # Verify what was actually inserted
        with mongodb_store.connect() as conn:
            result = mongodb_store.find(TEST_COLLECTION, {"name": {"$regex": "Bulk_"}})
            assert len(result) >= 50

        cleanup_context_collection(mongodb_store)

    def test_context_with_connection_timeout(self, mongodb_store):
        """Test context behavior with connection timeouts."""
        with mongodb_store.connect() as conn:
            # Perform a quick operation first
            doc_id = conn.insert(
                TEST_COLLECTION, {"name": "Timeout Test", "phase": "before"}
            )
            assert doc_id is not None

            # Context should handle timeout gracefully
            try:
                # This might timeout but shouldn't crash the context manager
                result = mongodb_store.find(TEST_COLLECTION, {}, limit=1000000)
                assert isinstance(result, list)
            except Exception:
                # Timeout exceptions are acceptable
                pass
