import os
import tempfile

import pytest
import requests

from data_store.object_store import ObjectStore


@pytest.fixture
def object_store():
    """Create an ObjectStore instance with real configuration.

    Yields:
        ObjectStore: Configured ObjectStore instance for testing
    """
    store = ObjectStore()
    yield store


class BaseDownloadTest:
    """Base class for download tests with common setup and teardown."""

    test_key = "test_download/test-file.txt"
    test_download_key = "test_download/test-download-file.txt"
    test_content = b"This is a test file for download testing"


class TestFGetObject(BaseDownloadTest):
    """Test suite for fget_object method functionality."""

    def test_fget_object_success(self, object_store):
        """Test successful file download using fget_object method.

        Args:
            object_store: ObjectStore instance for testing
        """
        # Arrange
        key = self.test_key
        test_content = self.test_content

        # First upload test content
        object_store.upload_object(data=test_content, key=key)

        # Create a temporary file path for download
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name

        try:
            # Act
            result = object_store.fget_object(key=key, file_path=temp_file_path)

            # Assert
            assert result is not None

            # Verify the file was downloaded correctly
            with open(temp_file_path, "rb") as downloaded_file:
                downloaded_content = downloaded_file.read()
            assert downloaded_content == test_content, (
                "Content of the downloaded file does not match the original content"
            )

        finally:
            # Clean up the temporary file from local filesystem
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            # Clean up the uploaded object from object store
            try:
                object_store.delete_object(key)
            except Exception as e:
                print(f"Warning: Failed to cleanup test object {key}: {e}")

    def test_fget_object_nonexistent_key(self, object_store):
        """Test fget_object method with non-existent object key.

        Args:
            object_store: ObjectStore instance for testing
        """
        # Arrange
        key = "nonexistent-key.txt"
        temp_file_path = "/tmp/nonexistent-download.txt"

        # Act & Assert
        with pytest.raises(Exception):  # Should raise S3Error or similar
            object_store.fget_object(key=key, file_path=temp_file_path)


class TestGetObject(BaseDownloadTest):
    """Test suite for get_object method functionality."""

    def test_get_object_success(self, object_store):
        """Test successful object download using get_object method.

        Args:
            object_store: ObjectStore instance for testing
        """
        # Arrange
        key = self.test_key
        test_content = self.test_content

        # First upload test content
        object_store.upload_object(data=test_content, key=key)

        try:
            # Act
            result = object_store.get_object(key=key)

            # Assert
            assert result is not None
            # MinIO returns a minio.datatypes.Object which has a stream
            # Access the underlying stream data
            content = result.body
            assert content == test_content, (
                "Content of the downloaded object does not match the original content"
            )

        finally:
            # Clean up the uploaded object from object store
            try:
                object_store.delete_object(key)
            except Exception as e:
                print(f"Warning: Failed to cleanup test object {key}: {e}")

    def test_get_object_nonexistent_key(self, object_store):
        """Test get_object method with non-existent object key.

        Args:
            object_store: ObjectStore instance for testing
        """
        # Arrange
        key = "nonexistent-key.txt"

        # Act & Assert
        with pytest.raises(Exception):  # Should raise S3Error or similar
            object_store.get_object(key=key)

    def test_get_object_large_content(self, object_store):
        """Test get_object method with large content.

        Args:
            object_store: ObjectStore instance for testing
        """
        # Arrange
        key = self.test_download_key
        # Create large content (1MB)
        large_content = b"X" * (1024 * 1024)

        # First upload large content
        object_store.upload_object(data=large_content, key=key)

        try:
            # Act
            result = object_store.get_object(key=key)

            # Assert
            assert result is not None
            # MinIO returns a minio.datatypes.Object which has a stream
            # Access the underlying stream data
            content = result.body
            assert content == large_content, (
                "Content of the downloaded large object does not match the original content"
            )

        finally:
            # Clean up the uploaded object from object store
            try:
                object_store.delete_object(key)
            except Exception as e:
                print(f"Warning: Failed to cleanup test object {key}: {e}")


class TestDownloadUtilities(BaseDownloadTest):
    """Test suite for download utility functionality."""

    def test_upload_and_download_roundtrip(self, object_store):
        """Test upload object and download using fget_object method.

        Args:
            object_store: ObjectStore instance for testing
        """
        # Arrange
        key = self.test_key
        test_content = self.test_content

        # Upload test content
        upload_result = object_store.upload_object(data=test_content, key=key)

        # Create a temporary file path for download
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name

        try:
            # Act - Download file
            download_result = object_store.fget_object(
                key=key, file_path=temp_file_path
            )

            # Assert
            assert upload_result is not None
            assert download_result is not None

            # Verify the downloaded file content
            with open(temp_file_path, "rb") as downloaded_file:
                downloaded_content = downloaded_file.read()
            assert downloaded_content == test_content, (
                "Downloaded content does not match uploaded content"
            )

        finally:
            # Clean up the temporary file from local filesystem
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            # Clean up the uploaded object from object store
            try:
                object_store.delete_object(key)
            except Exception as e:
                print(f"Warning: Failed to cleanup test object {key}: {e}")

    def test_get_object_and_verify_with_presigned_url(self, object_store):
        """Test get_object and verify using presigned URL access.

        Args:
            object_store: ObjectStore instance for testing
        """
        # Arrange
        key = self.test_download_key
        test_content = self.test_content

        # Upload test content
        upload_result = object_store.upload_object(data=test_content, key=key)

        try:
            # Act - Get object
            object_result = object_store.get_object(key=key)

            # Get presigned URL and verify access
            presigned_url = object_store.get_presigned_url(key)
            response = requests.get(presigned_url)

            # Assert
            assert upload_result is not None
            assert object_result is not None
            # MinIO returns a minio.datatypes.Object which has a stream
            # Access the underlying stream data
            content = object_result.body
            assert content == test_content, (
                "Object content does not match uploaded content"
            )
            assert response.status_code == 200, (
                f"Failed to access object via presigned URL: {response.text}"
            )
            assert response.content == test_content, (
                "Content accessed via presigned URL does not match uploaded content"
            )

        finally:
            # Clean up the uploaded object from object store
            try:
                object_store.delete_object(key)
            except Exception as e:
                print(f"Warning: Failed to cleanup test object {key}: {e}")
