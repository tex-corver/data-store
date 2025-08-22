# Object Store Interface Documentation

This document provides comprehensive documentation for the `ObjectStore` class, detailing its API, usage patterns, integration considerations, and best practices. It is intended for developers looking to use or extend the object store functionality for file storage and retrieval operations.

## Overview

The `ObjectStore` class offers a high-level interface for object storage operations. It integrates with abstract base classes and adapters to support multiple frameworks (e.g., MinIO, S3) and handles connection management, file operations, bucket management, and error handling. The class provides both high-level convenience methods and low-level access to underlying storage operations.

## Architecture

The object store follows a layered architecture:

- **ObjectStore**: High-level interface providing convenient methods for common operations
- **ObjectStoreClient**: Abstract base class defining the core storage operations interface
- **ObjectStoreComponentFactory**: Factory pattern for creating clients based on configuration
- **Adapters**: Concrete implementations for different storage backends (e.g., MinIO)
- **Models**: Data structures for buckets, objects, and metadata
- **Configurations**: Pydantic models for type-safe configuration

## Configuration and Initialization

The store is initialized with an optional configuration dictionary. If no configuration is provided, it retrieves settings via `utils.get_config()`. Proper configuration is required to establish the underlying storage client.

### Basic Configuration

```python
from data_store.object_store import ObjectStore

# Initialize with default configuration
store = ObjectStore()

# Initialize with explicit configuration
config = {
    "framework": "minio",
    "root_bucket": "my-bucket",
    "connection": {
        "endpoint": "localhost:9000",
        "access_key": "your-access-key",
        "secret_key": "your-secret-key",
        "secure": False
    }
}
store = ObjectStore(config)
```

### Configuration Models

The configuration uses Pydantic models for type safety:

```python
from data_store.object_store.configurations import ObjectStoreConfiguration, Framework

# Using enum for framework
config = ObjectStoreConfiguration(
    framework=Framework.MINIO,
    root_bucket="my-bucket",
    connection=ObjectStoreConnectionConfiguration(
        endpoint="localhost:9000",
        access_key="your-access-key",
        secret_key="your-secret-key",
        secure=False
    )
)
```

### Supported Frameworks

Currently supported frameworks:

- **MINIO**: MinIO object storage server
- **BOTO3**: AWS S3 (framework support in development)

## Connection Management

The `ObjectStore` automatically manages connections through lazy initialization. The client is created on first access and reused for subsequent operations.

```python
# The client is automatically initialized when first needed
store = ObjectStore(config)

# First operation triggers client creation
files = store.list_files()

# Subsequent operations reuse the same client
store.upload_file("local.txt", "remote.txt")
```

## File Operations

### Upload Files

#### Upload File with Path

```python
# Upload a file from local path to object storage
result = store.upload_file(
    file_path="/path/to/local/file.txt",
    key="uploads/file.txt",
    bucket="my-bucket"
)

# Upload to default root bucket
result = store.upload_file(
    file_path="/path/to/local/file.txt",
    key="uploads/file.txt"
)
```

#### Upload Object with Content

```python
# Upload object using the underlying client interface
result = store.upload_object(
    file_path="/path/to/local/file.txt",
    key="uploads/file.txt",
    bucket="my-bucket"
)
```

### Download Files

#### Download File to Path

```python
# Download file to local path
store.download_file(
    key="uploads/file.txt",
    file_path="/path/to/local/downloaded.txt",
    bucket="my-bucket"
)

# Download to default root bucket
store.download_file(
    key="uploads/file.txt",
    file_path="/path/to/local/downloaded.txt"
)
```

#### Download Object Content

```python
# Download object content directly
obj = store.download_object(
    key="uploads/file.txt",
    file_path="/path/to/local/downloaded.txt",
    bucket="my-bucket"
)
```

### Get File Content

```python
# Get file object with content and metadata
file_obj = store.get_file(
    key="uploads/file.txt",
    bucket="my-bucket"
)

# Access file content
content = file_obj.body.read()
print(f"File size: {len(content)} bytes")
print(f"Last modified: {file_obj.updated_time}")
```

### Delete Files

```python
# Delete file (convenience method)
store.delete_file(
    key="uploads/file.txt",
    bucket="my-bucket"
)

# Delete object with more control
result = store.delete_object(
    key="uploads/file.txt",
    bucket="my-bucket",
    version="version-id"  # Optional version for versioned storage
)
```

## Bucket Operations

### List Buckets

```python
# List all buckets
for bucket in store.list_buckets():
    print(f"Bucket: {bucket.name}, Created: {bucket.created_time}")
```

### Bucket Management

Note: Bucket management operations (create, delete) are typically handled through the underlying client interface:

```python
# Access the underlying client for bucket operations
client = store.client

# Create bucket (example - depends on adapter implementation)
# client.create_bucket("new-bucket")

# Delete bucket (example - depends on adapter implementation)
# client.delete_bucket("old-bucket")
```

## File Listing and Metadata

### List Files with Prefix

```python
# List all files in bucket
for file_metadata in store.list_files(bucket="my-bucket"):
    print(f"File: {file_metadata.key}, Size: {file_metadata.size}, Modified: {file_metadata.updated_time}")

# List files with prefix filter
for file_metadata in store.list_files(prefix="uploads/", bucket="my-bucket"):
    print(f"File: {file_metadata.key}")

# List files in default bucket
for file_metadata in store.list_files(prefix="documents/"):
    print(f"File: {file_metadata.key}")
```

### List Objects with Metadata

```python
# List objects with detailed metadata
for obj_metadata in store.list_objects(prefix="images/", bucket="my-bucket"):
    print(f"Object: {obj_metadata.key}")
    print(f"Size: {obj_metadata.size} bytes")
    print(f"Last modified: {obj_metadata.updated_time}")
```

## Copy Operations

### Copy Objects

```python
# Copy object within same bucket
result = store.copy_object(
    src_object="source-file.txt",
    dst_object="backup/source-file.txt",
    src_bucket="my-bucket",
    dst_bucket="my-bucket"
)

# Copy object between buckets
result = store.copy_object(
    src_object="source-file.txt",
    dst_object="archived/source-file.txt",
    src_bucket="source-bucket",
    dst_bucket="archive-bucket"
)
```

## Version Handling

For storage backends that support versioning:

```python
# Delete specific version
store.delete_object(
    key="versioned-file.txt",
    version="version-id-123",
    bucket="my-bucket"
)

# Access versioned objects (depends on adapter implementation)
# obj = store.get_object(
#     key="versioned-file.txt",
#     version="version-id-123",
#     bucket="my-bucket"
# )
```

## Presigned URLs

Presigned URLs provide temporary, secure access to objects without requiring permanent credentials.

### Generate Download URL

```python
# Generate presigned URL for downloading
download_url = store.get_presigned_url(
    key="private-file.txt",
    bucket="my-bucket",
    expires=3600  # 1 hour expiration
)

print(f"Download URL: {download_url}")
```

### Generate Upload URL

```python
# Generate presigned URL for uploading
upload_url = store.get_presigned_upload_url(
    key="uploads/user-upload.txt",
    bucket="my-bucket",
    expires=1800  # 30 minutes expiration
)

print(f"Upload URL: {upload_url}")
```

### Client-Side Usage

```python
import requests

# Upload using presigned URL
def upload_file_with_presigned_url(upload_url, file_path):
    with open(file_path, 'rb') as f:
        response = requests.put(upload_url, data=f)
    response.raise_for_status()
    return response

# Download using presigned URL
def download_file_with_presigned_url(download_url):
    response = requests.get(download_url)
    response.raise_for_status()
    return response.content

# Example usage
upload_url = store.get_presigned_upload_url("user-upload.txt")
download_url = store.get_presigned_url("user-upload.txt")

# Upload file
upload_file_with_presigned_url(upload_url, "/path/to/local/file.txt")

# Download file
content = download_file_with_presigned_url(download_url)
```

For detailed presigned URL usage patterns, security considerations, and best practices, see {doc}`presigned_urls_usage`.


## Data Models

The object store uses several data models:

### Bucket Model

```python
@dataclasses.dataclass(frozen=True)
class Bucket:
    name: str
    created_time: datetime
```

### ObjectMetadata Model

```python
@dataclasses.dataclass(frozen=True)
class ObjectMetadata:
    key: str
    updated_time: datetime
    size: int
```

### Object Model

```python
@dataclasses.dataclass(frozen=True)
class Object:
    body: IO[bytes]  # File content
    updated_time: datetime
```

## Error Handling Patterns

### Common Exceptions

```python
try:
    # Object operations
    store.upload_file("local.txt", "remote.txt")
except ValueError as e:
    # Configuration or parameter errors
    print(f"Configuration error: {e}")
except RuntimeError as e:
    # Operational errors (connection, permissions, etc.)
    print(f"Operation failed: {e}")
except Exception as e:
    # Other unexpected errors
    print(f"Unexpected error: {e}")
```

### Error Handling Best Practices

1. **Validate Configuration**: Always verify configuration before operations
2. **Handle Connection Errors**: Implement retry logic for transient failures
3. **Check Return Values**: Some operations return status information
4. **Use Context Managers**: For file operations when possible
5. **Log Errors**: Implement comprehensive logging for debugging

### Example: Robust File Upload

```python
import logging
from data_store.object_store import ObjectStore

logger = logging.getLogger(__name__)

def robust_upload(store: ObjectStore, local_path: str, remote_key: str, bucket: str = None, max_retries: int = 3):
    """Upload file with retry logic and error handling."""
    for attempt in range(max_retries):
        try:
            result = store.upload_file(
                file_path=local_path,
                key=remote_key,
                bucket=bucket
            )
            logger.info(f"Successfully uploaded {local_path} to {remote_key}")
            return result
        except Exception as e:
            logger.warning(f"Upload attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                logger.error(f"Upload failed after {max_retries} attempts")
                raise
            # Wait before retry (implement exponential backoff)
```


## Migration and Compatibility

### Version Compatibility

- **Python 3.12+**: Minimum supported Python version
- **Pydantic 2.8+**: Required for configuration models
- **MinIO 7.2.7+**: Current MinIO adapter dependency

### Breaking Changes

When upgrading, check for:

1. **Configuration Changes**: Verify that configuration parameters haven't changed
2. **Method Signatures**: Check for any method signature changes
3. **Return Types**: Ensure return types are compatible with your code

## Troubleshooting

### Common Issues

1. **Connection Errors**
   ```python
   # Check configuration
   print(f"Endpoint: {store.config.connection.endpoint}")
   print(f"Access Key: {store.config.connection.access_key}")
   ```

2. **Permission Errors**
   ```python
   # Verify bucket exists and has proper permissions
   for bucket in store.list_buckets():
       print(f"Available bucket: {bucket.name}")
   ```

3. **File Not Found**
   ```python
   # List files to verify existence
   files = list(store.list_files(prefix="your-prefix/"))
   print(f"Found {len(files)} files")
   ```

### Debug Mode

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Create store with debug info
store = ObjectStore(config)
```

## Conclusion

The `ObjectStore` class provides a robust, feature-rich interface for object storage operations. By abstracting the complexity of different storage backends and providing both high-level convenience methods and low-level access, it enables developers to build scalable file storage applications with minimal friction.

This documentation covers the essential aspects of using the object store, from basic configuration to advanced patterns and best practices. For more specific information about presigned URLs, see {doc}`presigned_urls`.

For additional support and community discussions, refer to the project's GitHub repository and issue tracker.