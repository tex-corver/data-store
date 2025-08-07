import pytest
from data_store.object_store import ObjectStore
from data_store.object_store.configurations import ObjectStoreConfiguration, ObjectStoreConnectionConfiguration


class TestPresignedUrls:
    """Test suite for MinIO presigned URL functionality."""

    @pytest.fixture(scope="class")
    def object_store(self):
        """Create an ObjectStore instance with real configuration."""
        store = ObjectStore()
        self.setup_method()
        self.store = store
        yield store
        self.teardown_method()

    def setup_method(self):
        """Setup method to upload a test file before each test."""
        import tempfile
        import os
        
        # Initialize the store and test data
        self.store = ObjectStore()
        self.test_key = "test_presigned_urls/test-file.txt"
        self.test_content = b"This is a test file for presigned URL testing"
        
        # Create a temporary file with test content
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(self.test_content)
            temp_file_path = temp_file.name
        
        try:
            # Upload test file to the object store
            self.store.upload_object(
                file_path=temp_file_path,
                key=self.test_key
            )
        finally:
            # Clean up the temporary file from local filesystem
            os.unlink(temp_file_path)

    def teardown_method(self):
        """Teardown method to delete the test file after each test."""
        if hasattr(self, 'store') and hasattr(self, 'test_key'):
            try:
                # Delete the test file from object store
                self.store.delete_object(key=self.test_key)
            except Exception as e:
                # Log the error but don't fail the test
                print(f"Warning: Failed to cleanup test file {self.test_key}: {e}")

    def test_get_presigned_url_default_bucket(self):
        """Test generating a presigned URL with default bucket."""
        key = self.test_key
        url = self.store.get_presigned_url(key) 
        # Verify the URL is returned
        assert isinstance(url, str)
        assert f"http://192.168.0.100:9000/sandbox/{self.test_key}" in url
        
        # Verify the URL contains expected query parameters
        assert "X-Amz-Algorithm" in url
        assert "X-Amz-Credential" in url
        assert "X-Amz-Date" in url
        assert "X-Amz-Expires" in url
        assert "X-Amz-SignedHeaders" in url
        assert "X-Amz-Signature" in url

    # def test_get_presigned_url_custom_bucket(self, object_store):
    #     """Test generating a presigned URL with custom bucket."""
    #     key = "test-file.txt"
    #     bucket = "custom-bucket"
    #     url = object_store.get_presigned_url(key, bucket)
        
    #     # Verify the URL is returned
    #     assert isinstance(url, str)
    #     assert "https://192.168.0.100:9000/custom-bucket/test-file.txt" in url
        
    #     # Verify the URL contains expected query parameters
    #     assert "X-Amz-Algorithm" in url
    #     assert "X-Amz-Credential" in url
    #     assert "X-Amz-Date" in url
    #     assert "X-Amz-Expires" in url
    #     assert "X-Amz-SignedHeaders" in url
    #     assert "X-Amz-Signature" in url

    def test_get_presigned_url_with_expiry(self, object_store):
        """Test generating a presigned URL with custom expiry time."""
        key = self.test_key
        expires = 7200  # 2 hours
        url = object_store.get_presigned_url(key, expires=expires)
        
        # Verify the URL is returned
        assert isinstance(url, str)
        assert f"http://192.168.0.100:9000/sandbox/{self.test_key}" in url

        # Verify the URL contains expected query parameters
        assert "X-Amz-Algorithm" in url
        assert "X-Amz-Credential" in url
        assert "X-Amz-Date" in url
        assert "X-Amz-Expires=7200" in url
        assert "X-Amz-SignedHeaders" in url
        assert "X-Amz-Signature" in url


    # def test_get_presigned_url_with_args_kwargs(self, object_store):
    #     """Test generating a presigned URL with additional arguments."""
    #     key = "test-file.txt"
    #     url = object_store.get_presigned_url(key, expires=3600, extra_arg="value", another_arg=123)
        
    #     # Verify the URL is returned
    #     assert isinstance(url, str)
    #     assert "https://192.168.0.100:9000/sandbox/test-file.txt" in url
        
    #     # Verify the URL contains expected query parameters
    #     assert "X-Amz-Algorithm" in url
    #     assert "X-Amz-Credential" in url
    #     assert "X-Amz-Date" in url
    #     assert "X-Amz-Expires" in url
    #     assert "X-Amz-SignedHeaders" in url
    #     assert "X-Amz-Signature" in url

    # def test_get_presigned_upload_url_with_args_kwargs(self, object_store):
    #     """Test generating a presigned upload URL with additional arguments."""
    #     key = "upload-file.txt"
    #     url = object_store.get_presigned_upload_url(key, expires=7200, extra_arg="value", another_arg=123)
        
    #     # Verify the URL is returned
    #     assert isinstance(url, str)
    #     assert "https://192.168.0.100:9000/sandbox/upload-file.txt" in url
        
    #     # Verify the URL contains expected query parameters
    #     assert "X-Amz-Algorithm" in url
    #     assert "X-Amz-Credential" in url
    #     assert "X-Amz-Date" in url
    #     assert "X-Amz-Expires" in url
    #     assert "X-Amz-SignedHeaders" in url
    #     assert "X-Amz-Signature" in url


    def test_presigned_upload_url_format(self, object_store):
        """Test that presigned upload URLs have the expected format."""
        key = "test_presigned_urls/test-upload-file.txt"
        url = object_store.get_presigned_upload_url(key)
        
        # Verify URL contains expected components
        assert url.startswith(f"http://192.168.0.100:9000/sandbox/{key}")
        assert "X-Amz-Algorithm" in url
        assert "X-Amz-Credential" in url
        assert "X-Amz-Date" in url
        assert "X-Amz-Expires" in url
        assert "X-Amz-SignedHeaders" in url
        assert "X-Amz-Signature" in url

        # try uploading a file using the presigned URL
        import requests
        test_content = b"This is a test file for presigned upload URL testing"
        response = requests.put(url, data=test_content)
        assert response.status_code == 200, f"Failed to upload file using presigned URL: {response.text}"

        # Check if the file exists in the object store
        test_object = object_store.get_object(key)
        assert test_object is not None, "Uploaded file does not exist in the object store"

        test_object_content = test_object.body
        assert test_object_content == test_content, "Content of the uploaded file does not match the original content"
        # clean up the uploaded file
        object_store.delete_object(key)


    # def test_presigned_url_expiry_parameter(self, object_store):
    #     """Test that expiry parameter is properly passed through."""
    #     key = "test-file.txt"
    #     test_expires = 1800
        
    #     # Test with expiry parameter
    #     url_with_expiry = object_store.get_presigned_url(key, expires=test_expires)
    #     assert "X-Amz-Expires" in url_with_expiry
        
    #     # Test without expiry parameter (should use default)
    #     url_default = object_store.get_presigned_url(key)
    #     assert "X-Amz-Expires" in url_default


    # def test_presigned_url_for_existing_file(self, object_store):
    #     """Test generating a presigned URL for the uploaded test file."""
    #     # Use the file uploaded in setup_method
    #     url = object_store.get_presigned_url(self.test_key)
        
    #     # Verify the URL is returned
    #     assert isinstance(url, str)
    #     assert f"https://192.168.0.100:9000/sandbox/{self.test_key}" in url
        
    #     # Verify the URL contains expected query parameters
    #     assert "X-Amz-Algorithm" in url
    #     assert "X-Amz-Credential" in url
    #     assert "X-Amz-Date" in url
    #     assert "X-Amz-Expires" in url
    #     assert "X-Amz-SignedHeaders" in url
    #     assert "X-Amz-Signature" in url

    # def test_presigned_upload_url_for_new_file(self, object_store):
    #     """Test generating a presigned upload URL for a new file."""
    #     new_key = "test_presigned_urls/upload-test.txt"
    #     url = object_store.get_presigned_upload_url(new_key)
        
    #     # Verify the URL is returned
    #     assert isinstance(url, str)
    #     assert f"https://192.168.0.100:9000/sandbox/{new_key}" in url
        
    #     # Verify the URL contains expected query parameters for PUT method
    #     assert "X-Amz-Algorithm" in url
    #     assert "X-Amz-Credential" in url
    #     assert "X-Amz-Date" in url
    #     assert "X-Amz-Expires" in url
    #     assert "X-Amz-SignedHeaders" in url
    #     assert "X-Amz-Signature" in url

    # def test_presigned_url_with_real_file_custom_bucket(self, object_store):
    #     """Test presigned URL generation with real file in custom bucket."""
    #     # Upload a file to a custom bucket for testing
    #     import tempfile
    #     import os
        
    #     custom_bucket = "test-bucket"
    #     custom_key = "test_presigned_urls/custom-bucket-file.txt"
    #     custom_content = b"Custom bucket test content"
        
    #     # Create temporary file
    #     with tempfile.NamedTemporaryFile(delete=False) as temp_file:
    #         temp_file.write(custom_content)
    #         temp_file_path = temp_file.name
        
    #     try:
    #         # Upload to custom bucket
    #         object_store.upload_object(
    #             file_path=temp_file_path,
    #             key=custom_key,
    #             bucket=custom_bucket
    #         )
            
    #         # Generate presigned URL for the custom bucket file
    #         url = object_store.get_presigned_url(custom_key, bucket=custom_bucket)
            
    #         # Verify the URL
    #         assert isinstance(url, str)
    #         assert f"https://192.168.0.100:9000/{custom_bucket}/{custom_key}" in url
    #         assert "X-Amz-Algorithm" in url
    #         assert "X-Amz-Signature" in url
            
    #         # Clean up the custom bucket file
    #         object_store.delete_object(key=custom_key, bucket=custom_bucket)
            
    #     finally:
    #         # Clean up temporary file
    #         os.unlink(temp_file_path)

    # def test_presigned_url_expiry_with_real_file(self, object_store):
    #     """Test that different expiry times work with real files."""
    #     # Test with the uploaded file from setup_method
    #     short_expiry_url = object_store.get_presigned_url(self.test_key, expires=300)  # 5 minutes
    #     long_expiry_url = object_store.get_presigned_url(self.test_key, expires=7200)  # 2 hours
        
    #     # Both URLs should be valid and different
    #     assert isinstance(short_expiry_url, str)
    #     assert isinstance(long_expiry_url, str)
    #     assert short_expiry_url != long_expiry_url
        
    #     # Both should contain the same base URL but different expiry values
    #     assert f"sandbox/{self.test_key}" in short_expiry_url
    #     assert f"sandbox/{self.test_key}" in long_expiry_url
    #     assert "X-Amz-Expires" in short_expiry_url
    #     assert "X-Amz-Expires" in long_expiry_url