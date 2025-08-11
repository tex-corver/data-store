# Object store Development Guide
This section provides detailed information for developers working on the object store functionality of the data-store library.

## Integration with Abstract Base Classes and Adapters

The `ObjectStore` class integrates with several abstract components:

### ObjectStoreClient

The abstract base class defines the core interface that all storage adapters must implement:

```python
from data_store.object_store.abstract import ObjectStoreClient

# All clients implement the same interface
class MyCustomClient(ObjectStoreClient):
    def _list_buckets(self, *args, **kwargs):
        # Implementation
        pass
    
    def _upload_object(self, file_path, key, bucket, *args, **kwargs):
        # Implementation
        pass
    
    # ... other required methods
```

### ObjectStoreComponentFactory

The factory pattern creates appropriate clients based on configuration:

```python
from data_store.object_store.abstract import ObjectStoreComponentFactory

class MyComponentFactory(ObjectStoreComponentFactory):
    def _create_client(self, *args, **kwargs) -> ObjectStoreClient:
        return MyCustomClient(config=self.config)
```

### Adapter Router

The system uses an adapter router to select the appropriate implementation:

```python
# Configuration determines which adapter to use
config = {
    "framework": "minio",  # This routes to MinIO adapter
    "root_bucket": "my-bucket",
    "connection": {...}
}

store = ObjectStore(config)
# Uses MinIOComponentFactory internally
```
## Usage Patterns and Best Practices

### 1. Configuration Management

```python
# Use environment variables for sensitive data
import os
from data_store.object_store import ObjectStore

config = {
    "framework": "minio",
    "root_bucket": os.getenv("OBJECT_STORE_BUCKET"),
    "connection": {
        "endpoint": os.getenv("OBJECT_STORE_ENDPOINT"),
        "access_key": os.getenv("OBJECT_STORE_ACCESS_KEY"),
        "secret_key": os.getenv("OBJECT_STORE_SECRET_KEY"),
        "secure": os.getenv("OBJECT_STORE_SECURE", "False").lower() == "true"
    }
}

store = ObjectStore(config)
```

### 2. Batch Operations

```python
def batch_upload_files(store: ObjectStore, file_mappings: list[dict]):
    """Upload multiple files efficiently."""
    results = []
    for mapping in file_mappings:
        try:
            result = store.upload_file(
                file_path=mapping["local_path"],
                key=mapping["remote_key"],
                bucket=mapping.get("bucket")
            )
            results.append({"success": True, "result": result})
        except Exception as e:
            results.append({"success": False, "error": str(e)})
    return results
```

### 3. File Organization

```python
# Use consistent naming conventions
def organize_files(store: ObjectStore, base_path: str):
    """Organize files by date and type."""
    import datetime
    
    today = datetime.date.today()
    prefix = f"archive/{today.year}/{today.month:02d}/{today.day:02d}/"
    
    # List files and organize them
    for file_meta in store.list_files(prefix="unorganized/"):
        # Move file to organized location
        new_key = prefix + file_meta.key
        store.copy_object(
            src_object=file_meta.key,
            dst_object=new_key,
            src_bucket="my-bucket",
            dst_bucket="my-bucket"
        )
```

### 4. Cleanup Operations

```python
def cleanup_old_files(store: ObjectStore, prefix: str, days_old: int = 30):
    """Remove files older than specified days."""
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.now() - timedelta(days=days_old)
    
    for file_meta in store.list_files(prefix=prefix):
        if file_meta.updated_time < cutoff_date:
            try:
                store.delete_object(
                    key=file_meta.key,
                    bucket="my-bucket"
                )
                print(f"Deleted {file_meta.key}")
            except Exception as e:
                print(f"Failed to delete {file_meta.key}: {e}")
```

### 5. Monitoring and Logging

```python
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def log_object_store_operations(func):
    """Decorator to log object store operations."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        operation_name = func.__name__
        logger.info(f"Starting {operation_name}")
        
        try:
            result = func(*args, **kwargs)
            logger.info(f"Completed {operation_name} successfully")
            return result
        except Exception as e:
            logger.error(f"Failed {operation_name}: {e}")
            raise
    
    return wrapper

# Usage example
@store = ObjectStore()

@log_object_store_operations
def upload_with_logging(local_path, remote_key, bucket=None):
    return store.upload_file(local_path, remote_key, bucket)
```

## Performance Considerations

### 1. Connection Reuse

The `ObjectStore` reuses connections automatically, but for high-throughput applications:

```python
# Create a single instance for the application lifetime
app_store = ObjectStore(config)

# Use it throughout your application
def upload_handler(request):
    return app_store.upload_file(request.file_path, request.remote_key)
```

### 2. Batch Operations

```python
# Use generator-based operations for memory efficiency
def process_large_file_list(store: ObjectStore, prefix: str):
    """Process files without loading all into memory."""
    for file_meta in store.list_files(prefix=prefix):
        # Process each file individually
        process_file(file_meta)
```

### 3. Caching

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_file_metadata(store: ObjectStore, key: str, bucket: str = None):
    """Cache file metadata to reduce API calls."""
    return store.list_files(prefix=key, bucket=bucket)
```

## Testing

### Unit Testing

```python
import pytest
from unittest.mock import Mock, patch
from data_store.object_store import ObjectStore

def test_upload_file():
    # Mock the underlying client
    with patch('data_store.object_store.store.ObjectStoreComponentFactory') as mock_factory:
        mock_client = Mock()
        mock_factory.return_value.create_client.return_value = mock_client
        
        store = ObjectStore()
        store.upload_file("test.txt", "remote.txt")
        
        # Verify the client method was called
        mock_client.upload_object.assert_called_once()
```

### Integration Testing

```python
def test_integration_upload_download():
    """Test complete upload/download cycle."""
    config = {
        "framework": "minio",
        "root_bucket": "test-bucket",
        "connection": {
            "endpoint": "localhost:9000",
            "access_key": "test-access-key",
            "secret_key": "test-secret-key",
            "secure": False
        }
    }
    
    store = ObjectStore(config)
    
    # Test file
    test_content = b"Hello, World!"
    test_file = "/tmp/test_upload.txt"
    
    # Create test file
    with open(test_file, "wb") as f:
        f.write(test_content)
    
    try:
        # Upload file
        result = store.upload_file(test_file, "test_upload.txt")
        assert result is not None
        
        # Download file
        downloaded_file = "/tmp/test_download.txt"
        store.download_file("test_upload.txt", downloaded_file)
        
        # Verify content
        with open(downloaded_file, "rb") as f:
            downloaded_content = f.read()
        
        assert downloaded_content == test_content
        
    finally:
        # Cleanup
        import os
        if os.path.exists(test_file):
            os.remove(test_file)
        if os.path.exists(downloaded_file):
            os.remove(downloaded_file)
```

## Advanced Topics

### Custom Adapters

To add support for new storage backends:

```python
from data_store.object_store.abstract import ObjectStoreClient, ObjectStoreComponentFactory

class CustomStorageClient(ObjectStoreClient):
    def _list_buckets(self, *args, **kwargs):
        # Implementation for listing buckets
        pass
    
    def _upload_object(self, file_path, key, bucket, *args, **kwargs):
        # Implementation for uploading objects
        pass
    
    # ... implement all required abstract methods

class CustomStorageComponentFactory(ObjectStoreComponentFactory):
    def _create_client(self, *args, **kwargs) -> ObjectStoreClient:
        return CustomStorageClient(config=self.config)

# Register the adapter
from data_store.object_store import adapters
adapters.adaper_routers["custom"] = CustomStorageComponentFactory
```

### Configuration Validation

```python
from pydantic import ValidationError
from data_store.object_store.configurations import ObjectStoreConfiguration

def validate_config(config_dict):
    """Validate configuration before creating ObjectStore."""
    try:
        config = ObjectStoreConfiguration(**config_dict)
        return config
    except ValidationError as e:
        print(f"Configuration validation failed: {e}")
        raise
```
