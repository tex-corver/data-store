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

    # Setup test data
    test_key = "test_presigned_urls/test-file.txt"
    test_content = b"This is a test file for presigned URL testing"

    # Create a temporary file with test content
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(test_content)
        temp_file_path = temp_file.name

    try:
        # Upload test file to the object store
        store.upload_object(file_path=temp_file_path, key=test_key)
        yield store
    finally:
        # Clean up the temporary file from local filesystem
        os.unlink(temp_file_path)
        # Teardown test data
        try:
            store.delete_object(key=test_key)
        except Exception as e:
            # Log the error but don't fail the test
            print(f"Warning: Failed to cleanup test file {test_key}: {e}")


class BasePresignedUrlTest:
    test_key = "test_presigned_urls/test-file.txt"
    test_content = b"This is a test file for presigned URL testing"

    """Base class for presigned URL tests with common setup and teardown."""


class TestPresignedUrlFormat(BasePresignedUrlTest):
    """Test suite for presigned URL format validation."""

    def test_get_presigned_url_default_bucket_format(self, object_store):
        """Test that presigned URLs have the expected format with default bucket.

        Args:
            object_store: ObjectStore instance for testing
        """
        # Arrange
        key = self.test_key

        # Act
        url = object_store.get_presigned_url(key)

        # Assert
        assert isinstance(url, str)
        assert f"http://192.168.0.100:9000/sandbox/{key}" in url

        # Verify the URL contains expected query parameters
        assert "X-Amz-Algorithm" in url
        assert "X-Amz-Credential" in url
        assert "X-Amz-Date" in url
        assert "X-Amz-Expires" in url
        assert "X-Amz-SignedHeaders" in url
        assert "X-Amz-Signature" in url

    def test_get_presigned_url_with_expiry_format(self, object_store):
        """Test that presigned URLs have the expected format with custom expiry.

        Args:
            object_store: ObjectStore instance for testing
        """
        # Arrange
        key = self.test_key
        expires = 7200  # 2 hours

        # Act
        url = object_store.get_presigned_url(key, expires=expires)

        # Assert
        assert isinstance(url, str)
        assert f"http://192.168.0.100:9000/sandbox/{key}" in url

        # Verify the URL contains expected query parameters
        assert "X-Amz-Algorithm" in url
        assert "X-Amz-Credential" in url
        assert "X-Amz-Date" in url
        assert "X-Amz-Expires=7200" in url
        assert "X-Amz-SignedHeaders" in url
        assert "X-Amz-Signature" in url

    def test_presigned_upload_url_format(self, object_store):
        """Test that presigned upload URLs have the expected format.

        Args:
            object_store: ObjectStore instance for testing
        """
        # Arrange
        key = "test_presigned_urls/test-upload-file.txt"

        # Act
        url = object_store.get_presigned_upload_url(key)

        # Assert
        assert url.startswith(f"http://192.168.0.100:9000/sandbox/{key}")
        assert "X-Amz-Algorithm" in url
        assert "X-Amz-Credential" in url
        assert "X-Amz-Date" in url
        assert "X-Amz-Expires" in url
        assert "X-Amz-SignedHeaders" in url
        assert "X-Amz-Signature" in url


class TestPresignedUrlUtilities(BasePresignedUrlTest):
    """Test suite for presigned URL utility functionality."""

    def test_presigned_upload(self, object_store):
        """Test that presigned upload URLs work correctly for file uploads.

        Args:
            object_store: ObjectStore instance for testing
        """
        # Arrange
        key = "test_presigned_urls/test-upload-file.txt"
        test_content = b"This is a test file for presigned upload URL testing"
        url = object_store.get_presigned_upload_url(key)

        # Act
        response = requests.put(url, data=test_content)

        # Assert
        assert response.status_code == 200, (
            f"Failed to upload file using presigned URL: {response.text}"
        )

        # Check if the file exists in the object store
        test_object = object_store.get_object(key)
        assert test_object is not None, (
            "Uploaded file does not exist in the object store"
        )

        test_object_content = test_object.body
        assert test_object_content == test_content, (
            "Content of the uploaded file does not match the original content"
        )

        # Clean up the uploaded file
        object_store.delete_object(key)

    def test_presigned_url_get(self, object_store):
        """Test that presigned URLs can be used to access objects.

        Args:
            object_store: ObjectStore instance for testing
        """
        # Arrange
        key = self.test_key
        url = object_store.get_presigned_url(key)

        # Act
        response = requests.get(url)

        # Assert
        assert response.status_code == 200, (
            f"Failed to access file using presigned URL: {response.text}"
        )

        # Verify the content matches
        assert response.content == object_store.get_object(key).body, (
            "Content accessed via presigned URL does not match original content"
        )
