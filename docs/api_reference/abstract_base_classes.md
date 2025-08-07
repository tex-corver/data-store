# Abstract Base Classes Documentation

This document provides comprehensive documentation for the abstract base classes in the data_store project, detailing the interfaces, design patterns, and implementation guidelines for extending the NoSQL and Object Store functionality.

## Overview

The data_store project uses abstract base classes (ABCs) to define clear interfaces for different storage backends. This approach enables:

- **Consistent APIs**: All storage implementations follow the same interface patterns
- **Extensibility**: New storage backends can be added by implementing the abstract interfaces
- **Testability**: Abstract interfaces make it easier to create mock implementations for testing
- **Type Safety**: Strong typing ensures implementations follow expected contracts

## NoSQL Store Abstract Classes

### NoSQLStore Abstract Base Class

The `NoSQLStore` abstract base class defines the interface for all NoSQL database implementations.

#### Class Definition

```python
from abc import ABC, abstractmethod
from typing import Any, List, Dict, Optional
from data_store.nosql_store import configurations

class NoSQLStore(ABC):
    def __init__(self, config: dict[str, Any] | configurations.NoSQLConfiguration) -> None
```

#### Abstract Methods

All implementations must provide concrete implementations for the following abstract methods:

##### Connection Management

```python
@abstractmethod
def _connect(self, *args, **kwargs):
    """Establish database connection
    
    Returns:
        Connection: Database connection object
        
    Raises:
        RuntimeError: If connection establishment fails
    """
    raise NotImplementedError

@abstractmethod
def _close(self, *args, **kwargs):
    """Close connection
    
    Raises:
        RuntimeError: If connection closure fails
    """
    raise NotImplementedError
```

##### CRUD Operations

```python
@abstractmethod
def _insert(self, collection: str, data: dict, *args, **kwargs) -> str:
    """Insert a document into a collection
    
    Args:
        collection (str): Name of the collection to insert into
        data (dict): Document data to insert
        
    Returns:
        str: ID of the inserted document
        
    Raises:
        ValueError: If collection name is empty or data is None
        RuntimeError: If database operation fails
    """
    raise NotImplementedError

@abstractmethod
def _find(
    self,
    collection: str,
    filters: dict | None = None,
    projections: list[str] | None = None,
    skip: int = 0,
    limit: int = 0,
    *args,
    **kwargs,
) -> list:
    """Find documents in a collection
    
    Args:
        collection (str): Collection name
        filters (dict | None): Query filters, default is None for find all
        projections (list[str] | None): Fields to include in results, default is None
        skip (int): Number of documents to skip, default is 0
        limit (int): Maximum number of documents to return, default is 0 (no limit)
        
    Returns:
        list: List of documents matching the query
        
    Raises:
        ValueError: If collection name is empty
    """
    raise NotImplementedError

@abstractmethod
def _update(
    self,
    collection: str,
    filters: dict,
    update_data: dict,
    upsert: bool = False,
    *args,
    **kwargs,
) -> int:
    """Update documents in a collection
    
    Args:
        collection (str): Name of the collection to update
        filters (dict): Query filters to select documents
        update_data (dict): Update operations or new field values
        upsert (bool): Create document if it doesn't exist, default False
        
    Returns:
        int: Number of documents modified
        
    Raises:
        ValueError: If collection name is empty or filters/update_data are None
        RuntimeError: If database operation fails
    """
    raise NotImplementedError

@abstractmethod
def _delete(self, collection: str, filters: dict, *args, **kwargs) -> int:
    """Delete documents from a collection
    
    Args:
        collection (str): Name of the collection to delete from
        filters (dict): Query filters to select documents
        
    Returns:
        int: Number of documents deleted
        
    Raises:
        ValueError: If collection name is empty or filters are None
        RuntimeError: If database operation fails
    """
    raise NotImplementedError
```

##### Bulk Operations

```python
@abstractmethod
def _bulk_insert(self, collection: str, data: list[dict], *args, **kwargs) -> str:
    """Insert multiple documents into a collection
    
    Args:
        collection (str): Name of the collection to insert into
        data (list[dict]): List of documents to insert
        
    Returns:
        str: String representation of count of inserted documents
        
    Raises:
        ValueError: If collection name is empty or data is None
        RuntimeError: If database operation fails
    """
    raise NotImplementedError

@abstractmethod
def _bulk_update(
    self,
    collection: str,
    filters: dict,
    update_data: list[dict] | dict,
    upsert: bool = False,
    *args,
    **kwargs,
) -> int:
    """Update multiple documents in a collection
    
    Args:
        collection (str): Name of the collection to update
        filters (dict): Query filters to select documents
        update_data (list[dict]): List of update operations or new field values
        upsert (bool): Create document if it doesn't exist, default False
        
    Returns:
        int: Total number of documents modified
        
    Raises:
        ValueError: If collection name is empty or filters/update_data are None
        RuntimeError: If database operation fails
    """
    raise NotImplementedError

@abstractmethod
def _bulk_delete(
    self, collection: str, filters: dict | list, *args, **kwargs
) -> int:
    """Delete multiple documents from a collection
    
    Args:
        collection (str): Name of the collection to delete from
        filters (dict | list): Query filter(s) to select documents
        
    Returns:
        int: Total number of documents deleted
        
    Raises:
        ValueError: If collection name is empty or filters are None
        RuntimeError: If database operation fails
    """
    raise NotImplementedError
```

#### Concrete Methods

The abstract base class provides several concrete methods that wrap the abstract methods:

```python
def connect(self, *args, **config):
    """Establish database connection
    
    Args:
        **config: Additional connection configuration parameters
        
    Returns:
        Connection: Database connection object
        
    Raises:
        RuntimeError: If connection establishment fails
    """
    return self._connect(*args, **config)

def insert(self, collection: str, data: dict, *args, **kwargs) -> str:
    """Insert a document into a collection
    
    Args:
        collection (str): Name of the collection to insert into
        data (dict): Document data to insert
        
    Returns:
        str: ID of the inserted document
        
    Raises:
        ValueError: If collection name is empty or data is None
        RuntimeError: If database operation fails
    """
    return self._insert(collection=collection, data=data, *args, **kwargs)
```

### NoSQLStoreComponentFactory Abstract Base Class

The `NoSQLStoreComponentFactory` abstract base class defines the interface for creating NoSQL store clients.

#### Class Definition

```python
class NoSQLStoreComponentFactory(ABC):
    def __init__(
        self,
        config: dict[str, Any] | configurations.NoSQLConfiguration,
        *args,
        **kwargs,
    ) -> None
```

#### Abstract Methods

```python
@abstractmethod
def _create_client(self, *args, **kwargs) -> NoSQLStore:
    """Abstract method to create a NoSQL store client instance
    
    Args:
        *args: Variable length argument list
        **kwargs: Arbitrary keyword arguments
        
    Returns:
        NoSQLStore: Configured NoSQL store client instance
        
    Raises:
        RuntimeError: If client creation fails
    """
    raise NotImplementedError
```

#### Concrete Methods

```python
def create_client(self, *args, **kwargs) -> NoSQLStore:
    """Create a NoSQL store client instance
    
    Args:
        *args: Variable length argument list
        **kwargs: Arbitrary keyword arguments
        
    Returns:
        NoSQLStore: Configured NoSQL store client instance
        
    Raises:
        RuntimeError: If client creation fails
    """
    client = self._create_client(*args, **kwargs)
    return client
```

## Object Store Abstract Classes

### ObjectStoreClient Abstract Base Class

The `ObjectStoreClient` abstract base class defines the interface for all object storage implementations.

#### Class Definition

```python
from abc import ABC, abstractmethod
from typing import Any, Generator, Optional
from data_store.object_store import configurations, models

class ObjectStoreClient(ABC):
    def __init__(
        self, config: dict[str, Any] | configurations.ObjectStoreConfiguration
    ) -> None
```

#### Abstract Methods

All implementations must provide concrete implementations for the following abstract methods:

##### Core Storage Operations

```python
@abstractmethod
def _list_buckets(self, *args, **kwargs):
    """List all buckets in the storage system
    
    Returns:
        Generator[models.Bucket, None, None]: Generator of bucket objects
    """
    raise NotImplementedError

@abstractmethod
def _upload_object(
    self,
    file_path: str,
    key: str,
    bucket: str,
    *args,
    **kwargs,
):
    """Upload an object to the storage system
    
    Args:
        file_path (str): Path to the file to upload
        key (str): Object key name
        bucket (str): Bucket name
        
    Raises:
        RuntimeError: If upload operation fails
    """
    raise NotImplementedError

@abstractmethod
def _download_object(
    self,
    key: str,
    file_path: str,
    bucket: str,
    *args,
    **kwargs,
):
    """Download an object from the storage system
    
    Args:
        key (str): Object key name
        file_path (str): Path to save the downloaded file
        bucket (str): Bucket name
        
    Raises:
        RuntimeError: If download operation fails
    """
    raise NotImplementedError

@abstractmethod
def _get_object(self, key: str, bucket: str, *args, **kwargs):
    """Get an object from the storage system
    
    Args:
        key (str): Object key name
        bucket (str): Bucket name
        
    Returns:
        Object: Object with content and metadata
        
    Raises:
        RuntimeError: If get operation fails
    """
    raise NotImplementedError

@abstractmethod
def _list_objects(
    self, bucket: str, prefix: str, *args, **kwargs
):
    """List objects in a bucket with optional prefix filter
    
    Args:
        bucket (str): Bucket name
        prefix (str): Optional prefix to filter objects
        
    Returns:
        Generator[models.Object, None, None]: Generator of object metadata
    """
    raise NotImplementedError

@abstractmethod
def _delete_object(self, key: str, bucket: str, *args, **kwargs):
    """Delete an object from the storage system
    
    Args:
        key (str): Object key name
        bucket (str): Bucket name
        
    Raises:
        RuntimeError: If delete operation fails
    """
    raise NotImplementedError

@abstractmethod
def _copy_object(
    self,
    src_object: str,
    dst_object: str,
    src_bucket: str,
    dst_bucket: str,
    *args,
    **kwargs,
):
    """Copy an object within or between buckets
    
    Args:
        src_object (str): Source object key name
        dst_object (str): Destination object key name
        src_bucket (str): Source bucket name
        dst_bucket (str): Destination bucket name
        
    Returns:
        Copy operation result
        
    Raises:
        RuntimeError: If copy operation fails
    """
    raise NotImplementedError
```

##### Presigned URL Operations

```python
@abstractmethod
def _get_presigned_url(
    self,
    key: str,
    bucket: str,
    expires: int = None,
    *args,
    **kwargs,
) -> str:
    """Generate a presigned URL for downloading objects (GET method).
    
    Args:
        key (str): Object key name
        bucket (str): Bucket name
        expires (int, optional): Expiration time in seconds. Defaults to None
        
    Returns:
        str: Presigned download URL
    """
    raise NotImplementedError

@abstractmethod
def _get_presigned_upload_url(
    self,
    key: str,
    bucket: str,
    expires: int = None,
    *args,
    **kwargs,
) -> str:
    """Generate a presigned URL for uploading objects (PUT method).
    
    Args:
        key (str): Object key name
        bucket (str): Bucket name
        expires (int, optional): Expiration time in seconds. Defaults to None
        
    Returns:
        str: Presigned upload URL
    """
    raise NotImplementedError
```

#### Concrete Methods

The abstract base class provides several concrete methods that wrap the abstract methods:

```python
def upload_file(
    self,
    file_path: str,
    key: str,
    bucket: str = None,
    *args,
    **kwargs,
):
    """Upload a file to object storage
    
    Args:
        file_path (str): Path to the file to upload
        key (str): Object key name
        bucket (str, optional): Bucket name. Defaults to root_bucket
    """
    bucket = bucket or self.root_bucket
    self._upload_object(
        file_path=file_path,
        key=key,
        bucket=bucket,
        *args,
        **kwargs,
    )

def download_file(
    self,
    key: str,
    file_path: str,
    bucket: str = None,
    *args,
    **kwargs,
):
    """Download a file from object storage
    
    Args:
        key (str): Object key name
        file_path (str): Path to save the downloaded file
        bucket (str, optional): Bucket name. Defaults to root_bucket
    """
    if bucket is None:
        bucket = self.root_bucket
    self._download_object(
        key=key,
        file_path=file_path,
        bucket=bucket,
        *args,
        **kwargs,
    )
```

### ObjectStoreComponentFactory Abstract Base Class

The `ObjectStoreComponentFactory` abstract base class defines the interface for creating object store clients.

#### Class Definition

```python
class ObjectStoreComponentFactory(ABC):
    def __init__(
        self, config: dict[str, Any] | configurations.ObjectStoreConfiguration
    ) -> None
```

#### Abstract Methods

```python
@abstractmethod
def _create_client(self, *args, **kwargs) -> ObjectStoreClient:
    """Abstract method to create an object store client instance
    
    Args:
        *args: Variable length argument list
        **kwargs: Arbitrary keyword arguments
        
    Returns:
        ObjectStoreClient: Configured object store client instance
    """
    raise NotImplementedError
```

#### Concrete Methods

```python
def create_client(self, *args, **kwargs) -> ObjectStoreClient:
    """Create an object store client instance
    
    Args:
        *args: Variable length argument list
        **kwargs: Arbitrary keyword arguments
        
    Returns:
        ObjectStoreClient: Configured object store client instance
    """
    client = self._create_client(*args, **kwargs)
    return client
```

## Factory Pattern Implementation

### Adapter Router

The system uses an adapter router to select the appropriate factory implementation based on configuration:

```python
# NoSQL Store Adapter Router
from data_store.nosql_store.adapters import adapter_router

# Object Store Adapter Router  
from data_store.object_store.adapters import adaper_routers

# Usage
config = {"framework": "mongodb"}
factory_class = adapter_router[config["framework"]]
factory = factory_class(config)
client = factory.create_client()
```

### Factory Registration

To add support for new storage backends, register them in the adapter router:

```python
# NoSQL Store Example
from data_store.nosql_store import abstract

class CustomNoSQLStore(abstract.NoSQLStore):
    # Implementation of all abstract methods
    pass

class CustomNoSQLStoreComponentFactory(abstract.NoSQLStoreComponentFactory):
    def _create_client(self, *args, **kwargs) -> NoSQLStore:
        return CustomNoSQLStore(config=self.config)

# Register the adapter
from data_store.nosql_store.adapters import adapter_router
adapter_router["custom"] = CustomNoSQLStoreComponentFactory

# Object Store Example
from data_store.object_store import abstract

class CustomObjectStoreClient(abstract.ObjectStoreClient):
    # Implementation of all abstract methods
    pass

class CustomObjectStoreComponentFactory(abstract.ObjectStoreComponentFactory):
    def _create_client(self, *args, **kwargs) -> ObjectStoreClient:
        return CustomObjectStoreClient(config=self.config)

# Register the adapter
from data_store.object_store.adapters import adaper_routers
adaper_routers["custom"] = CustomObjectStoreComponentFactory
```

## Design Patterns and Architecture

### Abstract Factory Pattern

The system uses the Abstract Factory pattern to:

1. **Define Families of Objects**: Create related objects (client + factory) for specific storage backends
2. **Decouple Client Code**: Client code works with abstract interfaces, not concrete implementations
3. **Ensure Consistency**: Factory methods ensure that created objects are compatible

### Strategy Pattern

The adapter router implements the Strategy pattern:

1. **Context**: The main store classes (NoSQLStore, ObjectStore)
2. **Strategy**: Different storage backend implementations
3. **Context Interface**: Abstract base classes define the contract

### Template Method Pattern

The abstract base classes use the Template Method pattern:

1. **Template Methods**: Concrete methods that define the algorithm
2. **Primitive Operations**: Abstract methods that subclasses must implement
3. **Hook Methods**: Optional methods for customization

## Implementation Guidelines

### Creating New NoSQL Store Implementation

1. **Inherit from NoSQLStore**: Extend the abstract base class
2. **Implement All Abstract Methods**: Provide concrete implementations for all abstract methods
3. **Handle Connection Management**: Implement proper connection lifecycle
4. **Error Handling**: Raise appropriate exceptions for error conditions
5. **Type Safety**: Use proper type hints as specified in the interface

```python
from data_store.nosql_store import abstract, configurations

class MyCustomNoSQLStore(abstract.NoSQLStore):
    def __init__(self, config: dict[str, Any] | configurations.NoSQLConfiguration):
        super().__init__(config)
        # Initialize custom connection parameters
        
    def _connect(self, *args, **kwargs):
        # Implement connection logic
        pass
        
    def _insert(self, collection: str, data: dict, *args, **kwargs) -> str:
        # Implement insert logic
        pass
        
    # ... implement all other abstract methods
```

### Creating New Object Store Implementation

1. **Inherit from ObjectStoreClient**: Extend the abstract base class
2. **Implement All Abstract Methods**: Provide concrete implementations for all abstract methods
3. **Handle File Operations**: Implement proper file upload/download logic
4. **Error Handling**: Raise appropriate exceptions for error conditions
5. **Type Safety**: Use proper type hints as specified in the interface

```python
from data_store.object_store import abstract, configurations, models

class MyCustomObjectStoreClient(abstract.ObjectStoreClient):
    def __init__(self, config: dict[str, Any] | configurations.ObjectStoreConfiguration):
        super().__init__(config)
        # Initialize custom connection parameters
        
    def _upload_object(self, file_path: str, key: str, bucket: str, *args, **kwargs):
        # Implement upload logic
        pass
        
    def _download_object(self, key: str, file_path: str, bucket: str, *args, **kwargs):
        # Implement download logic
        pass
        
    # ... implement all other abstract methods
```

### Creating Custom Factory

1. **Inherit from ComponentFactory**: Extend the appropriate factory base class
2. **Implement _create_client**: Return an instance of your custom client
3. **Register the Factory**: Add it to the appropriate adapter router

```python
from data_store.nosql_store import abstract

class MyCustomNoSQLStoreComponentFactory(abstract.NoSQLStoreComponentFactory):
    def _create_client(self, *args, **kwargs) -> abstract.NoSQLStore:
        return MyCustomNoSQLStore(config=self.config)
```

## Best Practices

### Error Handling

1. **Use Specific Exceptions**: Raise appropriate exception types for different error conditions
2. **Provide Clear Messages**: Include descriptive error messages for debugging
3. **Handle Connection Errors**: Implement retry logic for transient connection failures
4. **Validate Input**: Validate parameters before performing operations

### Performance Considerations

1. **Connection Pooling**: Reuse connections when possible
2. **Lazy Initialization**: Initialize connections only when needed
3. **Batch Operations**: Implement efficient bulk operations for large datasets
4. **Memory Management**: Properly close connections and release resources

### Testing

1. **Unit Testing**: Test each abstract method implementation
2. **Integration Testing**: Test with actual storage backends
3. **Mock Testing**: Use mock implementations for testing client code
4. **Error Scenarios**: Test error handling and edge cases

### Documentation

1. **Type Hints**: Use comprehensive type hints for all methods
2. **Docstrings**: Provide detailed docstrings for all public methods
3. **Examples**: Include usage examples in docstrings
4. **Parameter Validation**: Document parameter validation rules

## Conclusion

The abstract base classes in the data_store project provide a robust foundation for implementing storage backends. By following the defined interfaces and design patterns, developers can create consistent, maintainable, and extensible storage implementations.

The abstract layer ensures that all storage backends provide the same core functionality while allowing for implementation-specific optimizations and features. This approach enables the data_store project to support multiple storage backends with a consistent API.

For more information about specific implementations, see the documentation for:
- {doc}`../user_guides/nosql_store` - NoSQL store interface and usage
- {doc}`../user_guides/object_store` - Object store interface and usage
- {doc}`configuration_classes` - Configuration models and validation
- {doc}`models` - Data models and structures
- {doc}`adapters` - Adapter implementations and extension points