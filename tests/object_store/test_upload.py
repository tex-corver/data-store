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


class BaseUploadTest:
    """Base class for upload tests with common setup and teardown."""

    test_key = "test_upload/test-file.txt"
    test_upload_key = "test_upload/test-upload-file.txt"
    test_content = b"This is a test file for upload testing"


class TestUploadFile(BaseUploadTest):
    """Test suite for upload_file method functionality."""

    def test_upload_file_success(self, object_store):
        """Test successful file upload using upload_file method.

        Args:
            object_store: ObjectStore instance for testing
        """
        # Arrange
        key = self.test_key
        test_content = self.test_content

        # Create a temporary file with test content
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file_path = temp_file.name

        try:
            # Act
            result = object_store.upload_file(file_path=temp_file_path, key=key)

            # Assert
            assert result is not None

            # Verify the file exists in the object store
            uploaded_object = object_store.get_object(key)
            assert uploaded_object is not None, (
                "Uploaded file does not exist in the object store"
            )

            # Verify the content matches
            assert uploaded_object.body == test_content, (
                "Content of the uploaded file does not match the original content"
            )

        finally:
            # Clean up the temporary file from local filesystem
            os.unlink(temp_file_path)
            # Clean up the uploaded file from object store
            try:
                object_store.delete_object(key)
            except Exception as e:
                print(f"Warning: Failed to cleanup test file {key}: {e}")

    def test_upload_file_with_custom_bucket(self, object_store):
        """Test file upload to a custom bucket using upload_file method.

        Args:
            object_store: ObjectStore instance for testing
        """
        # Arrange
        key = self.test_upload_key
        test_content = self.test_content
        custom_bucket = "test-bucket"

        # Create a temporary file with test content
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file_path = temp_file.name

        try:
            # Act
            result = object_store.upload_file(
                file_path=temp_file_path, key=key, bucket=custom_bucket
            )

            # Assert
            assert result is not None

            # Verify the file exists in the custom bucket
            uploaded_object = object_store.get_object(key, bucket=custom_bucket)
            assert uploaded_object is not None, (
                "Uploaded file does not exist in the custom bucket"
            )

            # Verify the content matches
            assert uploaded_object.body == test_content, (
                "Content of the uploaded file does not match the original content"
            )

        finally:
            # Clean up the temporary file from local filesystem
            os.unlink(temp_file_path)
            # Clean up the uploaded file from object store
            try:
                object_store.delete_object(key, bucket=custom_bucket)
            except Exception as e:
                print(f"Warning: Failed to cleanup test file {key}: {e}")

    def test_upload_file_nonexistent_file(self, object_store):
        """Test upload_file method with non-existent file path.

        Args:
            object_store: ObjectStore instance for testing
        """
        # Arrange
        key = self.test_key
        nonexistent_file_path = "/nonexistent/path/file.txt"

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            object_store.upload_file(file_path=nonexistent_file_path, key=key)


class TestUploadObject(BaseUploadTest):
    """Test suite for upload_object method functionality."""

    def test_upload_object_success(self, object_store):
        """Test successful object upload using upload_object method.

        Args:
            object_store: ObjectStore instance for testing
        """
        # Arrange
        key = self.test_key
        test_content = self.test_content

        # Act
        result = object_store.upload_object(file_object=test_content, key=key)

        # Assert
        assert result is not None

        # Verify the object exists in the object store
        uploaded_object = object_store.get_object(key)
        assert uploaded_object is not None, (
            "Uploaded object does not exist in the object store"
        )

        # Verify the content matches
        assert uploaded_object.body == test_content, (
            "Content of the uploaded object does not match the original content"
        )

        # Clean up the uploaded object
        try:
            object_store.delete_object(key)
        except Exception as e:
            print(f"Warning: Failed to cleanup test object {key}: {e}")

    @pytest.mark.skip(reason="Custom bucket is not configured in the test environment")
    def test_upload_object_with_custom_bucket(self, object_store):
        """Test object upload to a custom bucket using upload_object method.

        Args:
            object_store: ObjectStore instance for testing
        """
        # Arrange
        key = self.test_upload_key
        test_content = self.test_content
        custom_bucket = "test-bucket"

        # Act
        result = object_store.upload_object(
            file_object=test_content, key=key, bucket=custom_bucket
        )

        # Assert
        assert result is not None

        # Verify the object exists in the custom bucket
        uploaded_object = object_store.get_object(key, bucket=custom_bucket)
        assert uploaded_object is not None, (
            "Uploaded object does not exist in the custom bucket"
        )

        # Verify the content matches
        assert uploaded_object.body == test_content, (
            "Content of the uploaded object does not match the original content"
        )

        # Clean up the uploaded object
        try:
            object_store.delete_object(key, bucket=custom_bucket)
        except Exception as e:
            print(f"Warning: Failed to cleanup test object {key}: {e}")

    def test_upload_object_empty_content(self, object_store):
        """Test upload_object method with empty content.

        Args:
            object_store: ObjectStore instance for testing
        """
        # Arrange
        key = self.test_key
        empty_content = b""

        # Act
        result = object_store.upload_object(file_object=empty_content, key=key)

        # Assert
        assert result is not None

        # Verify the object exists in the object store
        uploaded_object = object_store.get_object(key)
        assert uploaded_object is not None, (
            "Uploaded empty object does not exist in the object store"
        )

        # Verify the content is empty
        assert uploaded_object.body == empty_content, (
            "Content of the uploaded empty object does not match"
        )

        # Clean up the uploaded object
        try:
            object_store.delete_object(key)
        except Exception as e:
            print(f"Warning: Failed to cleanup test object {key}: {e}")

    def test_upload_object_large_content(self, object_store):
        """Test upload_object method with large content.

        Args:
            object_store: ObjectStore instance for testing
        """
        # Arrange
        key = self.test_upload_key
        # Create large content (1MB)
        large_content = b"X" * (1024 * 1024)

        # Act
        result = object_store.upload_object(file_object=large_content, key=key)

        # Assert
        assert result is not None

        # Verify the object exists in the object store
        uploaded_object = object_store.get_object(key)
        assert uploaded_object is not None, (
            "Uploaded large object does not exist in the object store"
        )

        # Verify the content matches
        assert uploaded_object.body == large_content, (
            "Content of the uploaded large object does not match the original content"
        )

        # Clean up the uploaded object
        try:
            object_store.delete_object(key)
        except Exception as e:
            print(f"Warning: Failed to cleanup test object {key}: {e}")


class TestUploadUtilities(BaseUploadTest):
    """Test suite for upload utility functionality."""

    def test_upload_file_and_verify_with_presigned_url(self, object_store):
        """Test upload_file and verify using presigned URL access.

        Args:
            object_store: ObjectStore instance for testing
        """
        # Arrange
        key = self.test_key
        test_content = self.test_content

        # Create a temporary file with test content
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file_path = temp_file.name

        try:
            # Act - Upload file
            upload_result = object_store.upload_file(file_path=temp_file_path, key=key)

            # Get presigned URL and verify access
            presigned_url = object_store.get_presigned_url(key)
            response = requests.get(presigned_url)

            # Assert
            assert upload_result is not None
            assert response.status_code == 200, (
                f"Failed to access uploaded file via presigned URL: {response.text}"
            )
            assert response.content == test_content, (
                "Content accessed via presigned URL does not match uploaded content"
            )

        finally:
            # Clean up the temporary file from local filesystem
            os.unlink(temp_file_path)
            # Clean up the uploaded file from object store
            try:
                object_store.delete_object(key)
            except Exception as e:
                print(f"Warning: Failed to cleanup test file {key}: {e}")

    def test_upload_object_and_verify_with_presigned_url(self, object_store):
        """Test upload_object and verify using presigned URL access.

        Args:
            object_store: ObjectStore instance for testing
        """
        # Arrange
        key = self.test_upload_key
        test_content = self.test_content

        # Act - Upload object
        upload_result = object_store.upload_object(file_object=test_content, key=key)

        # Get presigned URL and verify access
        presigned_url = object_store.get_presigned_url(key)
        response = requests.get(presigned_url)

        # Assert
        assert upload_result is not None
        assert response.status_code == 200, (
            f"Failed to access uploaded object via presigned URL: {response.text}"
        )
        assert response.content == test_content, (
            "Content accessed via presigned URL does not match uploaded content"
        )

        # Clean up the uploaded object
        try:
            object_store.delete_object(key)
        except Exception as e:
            print(f"Warning: Failed to cleanup test object {key}: {e}")
