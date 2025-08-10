# Adapters Documentation

This document provides comprehensive documentation for the adapter implementations in the data_store project, detailing the MongoDB and MinIO adapters, adapter patterns, extension points, and best practices for adding new storage backends.

## Overview

The data_store project uses the Adapter pattern to provide consistent interfaces for different storage backends. Adapters implement the abstract base classes to enable support for multiple storage systems while maintaining a unified API.

Key features of the adapter system:

- **Consistent Interface**: All adapters implement the same abstract interfaces
- **Framework Selection**: Adapter router selects appropriate implementation based on configuration
- **Extensibility**: Easy to add new storage backends by implementing abstract interfaces
- **Type Safety**: Strong typing ensures adapter implementations follow expected contracts
- **Error Handling**: Consistent error handling across different storage systems

## Adapter Architecture

### Adapter Router

The adapter router maps framework names to their corresponding factory classes:

```python
# NoSQL Store Adapter Router
from data_store.nosql_store.adapters import adapter_routers

# Object Store Adapter Router
from data_store.object_store.adapters import adaper_routers

# Example mappings
adapter_routers = {
    "mongodb": mongodb_adapter.NoSQLStoreComponentFactory,
    "couchdb": couchdb_adapter.NoSQLStoreComponentFactory,
    "dynamodb": dynamodb_adapter.NoSQLStoreComponentFactory
}

adaper_routers = {
    "minio": minio_adapter.ObjectStoreComponentFactory,
    "boto3": boto3_adapter.ObjectStoreComponentFactory
}
```

### Adapter Registration

To add support for new storage backends:

```python
# Register new adapter
adapter_routers["new_framework"] = NewFrameworkAdapterFactory
adaper_routers["new_storage"] = NewStorageAdapterFactory
```

## MongoDB Adapter

### Overview

The MongoDB adapter provides a complete implementation of the NoSQL store interface for MongoDB databases.

### Class Structure

```python
from data_store.nosql_store import abstract, configurations, models

class NoSQLStore(abstract.NoSQLStore):
    """MongoDB implementation of NoSQL store"""
    
    config: configurations.NoSQLConfiguration
    
    def __init__(
        self,
        config: dict[str, Any] | configurations.NoSQLConfiguration,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(config)
        self._client: pymongo.MongoClient | None = None
        self._database: pymongo.database.Database | None = None
```

### Connection Management

#### Client Initialization

```python
def _init_client(self, *args, **kwargs) -> pymongo.MongoClient:
    """Initialize MongoDB client using connection configuration
    
    Args:
        **kwargs: Additional keyword arguments for pymongo.MongoClient
        
    Returns:
        pymongo.MongoClient: Configured MongoDB client instance
        
    Raises:
        RuntimeError: If connection establishment fails
        ValueError: If connection configuration is invalid
    """
    connection_config = self.config.connection
    connection_uri = connection_config.connection_uri
    connection_timeout = connection_config.connection_timeout

    client = pymongo.MongoClient(
        connection_uri,
        serverSelectionTimeoutMS=connection_timeout * 1000,
        **kwargs,
    )

    # Test the connection
    try:
        client.admin.command("ping")
        logger.info("Successfully connected to MongoDB")
    except pymongo.errors.ConnectionFailure as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise RuntimeError(
            "Failed to connect to MongoDB. Check your connection settings."
            f" Error: {e}"
        ) from e
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

    return client
```

#### Database Access

```python
def _get_database(self, *args, **kwargs) -> pymongo.database.Database:
    """Get database instance
    
    Returns:
        pymongo.database.Database: MongoDB database instance
        
    Raises:
        RuntimeError: If client not initialized
        ValueError: If database name not configured
    """
    if not self._client:
        raise RuntimeError("MongoDB client not initialized. Call connect() first.")

    if self._database is None:
        db_name = self.config.connection.database
        if not db_name:
            raise ValueError("Database name is required in configuration")
        self._database = self._client[db_name]

    return self._database
```

#### Collection Access

```python
@validate_not_none("collection")
def _get_collection(
    self, collection: str, *args, **kwargs
) -> pymongo.collection.Collection:
    """Get collection instance
    
    Args:
        collection (str): Name of the collection
        
    Returns:
        pymongo.collection.Collection: MongoDB collection instance
        
    Raises:
        RuntimeError: If database not initialized
    """
    database = self._get_database()
    return database[collection]
```

### CRUD Operations

#### Insert Operation

```python
@validate_not_none("collection", "data")
def _insert(self, collection: str, data: dict, *args, **kwargs) -> str:
    """Insert a document into a collection
    
    Args:
        collection (str): Name of the collection to insert into
        data (dict): Document data to insert
        *args: Additional positional arguments for pymongo insert_one
        **kwargs: Additional keyword arguments for pymongo insert_one
        
    Returns:
        str: ID of the inserted document
        
    Raises:
        ValueError: If collection name is empty or data is None
        RuntimeError: If database operation fails
    """
    _collection = self._get_collection(collection)
    result = _collection.insert_one(data, *args, **kwargs)
    return str(result.inserted_id)
```

#### Find Operation

```python
@validate_not_none("collection")
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
        *args: Additional positional arguments for pymongo find
        **kwargs: Additional keyword arguments for pymongo find
        
    Returns:
        list: List of documents matching the query
        
    Raises:
        ValueError: If collection name is empty
    """
    _collection = self._get_collection(collection)

    # Build projection dict from list
    projection_dict = None
    if projections:
        projection_dict = {field: 1 for field in projections}

    cursor = _collection.find(
        filters or {},
        projection_dict,
        skip,
        limit if limit > 0 else 0,
        *args,
        **kwargs,
    )

    # Convert ObjectId to string for JSON serialization
    documents = []
    for doc in cursor:
        if "_id" in doc and isinstance(doc["_id"], bson.ObjectId):
            doc["_id"] = str(doc["_id"])
        documents.append(doc)

    return documents
```

#### Update Operation

```python
@validate_not_none("collection", "filters", "update_data")
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
        *args: Additional positional arguments for pymongo update_one
        **kwargs: Additional keyword arguments for pymongo update_one
        
    Returns:
        int: Number of documents modified
        
    Raises:
        ValueError: If collection name is empty or filters/update_data are None
        RuntimeError: If database operation fails
    """
    _collection = self._get_collection(collection)

    # Wrap update_data in $set if it doesn't contain operators
    if not any(key.startswith("$") for key in update_data.keys()):
        update_data = {"$set": update_data}

    result = _collection.update_one(filters, update_data, upsert, *args, **kwargs)
    return result.modified_count
```

#### Delete Operation

```python
@validate_not_none("collection")
def _delete(self, collection: str, filters: dict, *args, **kwargs) -> int:
    """Delete documents from a collection
    
    Args:
        collection (str): Name of the collection to delete from
        filters (dict): Query filters to select documents
        *args: Additional positional arguments for pymongo delete_one
        **kwargs: Additional keyword arguments for pymongo delete_one
        
    Returns:
        int: Number of documents deleted
        
    Raises:
        ValueError: If collection name is empty or filters are None
        RuntimeError: If database operation fails
    """
    _collection = self._get_collection(collection)
    result = _collection.delete_one(filters, *args, **kwargs)
    return result.deleted_count
```

### Bulk Operations

#### Bulk Insert

```python
@validate_not_none("collection", "data")
def _bulk_insert(self, collection: str, data: list[dict], *args, **kwargs) -> str:
    """Insert multiple documents into a collection
    
    Args:
        collection (str): Name of the collection to insert into
        data (list[dict]): List of documents to insert
        *args: Additional positional arguments for pymongo insert_many
        **kwargs: Additional keyword arguments for pymongo insert_many
        
    Returns:
        str: String representation of count of inserted documents
        
    Raises:
        ValueError: If collection name is empty or data is None
        RuntimeError: If database operation fails
    """
    _collection = self._get_collection(collection)
    result = _collection.insert_many(data, *args, **kwargs)
    return f"{len(result.inserted_ids)}"
```

#### Bulk Update

```python
@validate_not_none("collection", "filters", "update_data")
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
        *args: Additional positional arguments for pymongo update_many
        **kwargs: Additional keyword arguments for pymongo update_many
        
    Returns:
        int: Total number of documents modified
        
    Raises:
        ValueError: If collection name is empty or filters/update_data are None
        RuntimeError: If database operation fails
    """
    _collection = self._get_collection(collection)
    total_modified = 0
    if not isinstance(update_data, list):
        update_data = [update_data]

    # Process each update operation
    for update_doc in update_data:
        # Wrap update_doc in $set if it doesn't contain operators
        if not any(key.startswith("$") for key in update_doc.keys()):
            update_doc = {"$set": update_doc}

        result = _collection.update_many(
            filters, update_doc, upsert, *args, **kwargs
        )
        total_modified += result.modified_count

    return total_modified
```

#### Bulk Delete

```python
@validate_not_none("collection")
def _bulk_delete(
    self, collection: str, filters: dict | list, *args, **kwargs
) -> int:
    """Delete multiple documents from a collection
    
    Args:
        collection (str): Name of the collection to delete from
        filters (dict | list): Query filter(s) to select documents
        *args: Additional positional arguments for delete operations
        **kwargs: Additional keyword arguments for delete operations
        
    Returns:
        int: Total number of documents deleted
        
    Raises:
        ValueError: If collection name is empty or filters are None
        RuntimeError: If database operation fails
    """
    _collection = self._get_collection(collection)
    total_deleted = 0
    
    if isinstance(filters, list):
        # Handle multiple filters
        for filter_doc in filters:
            result = _collection.delete_one(filter_doc, *args, **kwargs)
            total_deleted += result.deleted_count
    else:
        # Handle single filter
        result = _collection.delete_many(filters, *args, **kwargs)
        total_deleted = result.deleted_count
    
    return total_deleted
```

### Validation Decorators

The MongoDB adapter uses validation decorators to ensure parameter integrity:

```python
def validate_not_none(
    *param_names: str,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to validate that specified parameters are not None
    
    Args:
        *param_names (str): Names of the parameters to validate
        
    Returns:
        Callable: Decorated function that validates the parameters
        
    Raises:
        ValueError: If any of the specified parameters is None
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            for param_name in param_names:
                # Get parameter value from args or kwargs
                param_value = kwargs.get(param_name)
                if not param_value:
                    # Try to get from args if not in kwargs
                    try:
                        param_index = func.__code__.co_varnames.index(param_name)
                        if param_index < len(args):
                            param_value = args[param_index]
                    except (ValueError, IndexError):
                        pass

                if not param_value:
                    raise ValueError(
                        f"{param_name} cannot be None for {func.__name__} operation"
                    )
            return func(*args, **kwargs)

        return wrapper

    return decorator
```

### MongoDB Adapter Factory

```python
class NoSQLStoreComponentFactory(abstract.NoSQLStoreComponentFactory):
    """Factory for creating MongoDB adapter instances"""
    
    def _create_client(self, *args, **kwargs) -> NoSQLStore:
        """Create MongoDB adapter instance
        
        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
            
        Returns:
            NoSQLStore: Configured MongoDB adapter instance
        """
        return NoSQLStore(config=self.config, *args, **kwargs)
```

## MinIO Adapter

### Overview

The MinIO adapter provides a complete implementation of the object store interface for MinIO object storage.

### Class Structure

```python
from data_store.object_store import abstract, configurations, models

class ObjectStoreClient(abstract.ObjectStoreClient):
    """MinIO implementation of object store client"""
    
    def __init__(
        self, config: dict[str, Any] | configurations.ObjectStoreConfiguration
    ) -> None:
        super().__init__(config)
        self._client: minio.Minio | None = None
        self.root_bucket = self.config.root_bucket
```

### Client Initialization

```python
def _init_client(self, *args, **kwargs) -> minio.Minio:
    """Initialize MinIO client using connection configuration
    
    Args:
        **kwargs: Additional keyword arguments for minio.Minio
        
    Returns:
        minio.Minio: Configured MinIO client instance
        
    Raises:
        RuntimeError: If connection establishment fails
        ValueError: If connection configuration is invalid
    """
    connection_config = self.config.connection
    
    # Create MinIO client
    client = minio.Minio(
        endpoint=connection_config.endpoint,
        access_key=connection_config.access_key,
        secret_key=connection_config.secret_key,
        secure=connection_config.secure,
        **kwargs
    )

    # Test the connection
    try:
        # List buckets to test connection
        client.list_buckets()
        logger.info("Successfully connected to MinIO")
    except Exception as e:
        logger.error(f"Failed to connect to MinIO: {e}")
        raise RuntimeError(
            "Failed to connect to MinIO. Check your connection settings."
            f" Error: {e}"
        ) from e

    return client
```

### Core Storage Operations

#### List Buckets

```python
def _list_buckets(self, *args, **kwargs):
    """List all buckets in the storage system
    
    Returns:
        Generator[models.Bucket, None, None]: Generator of bucket objects
    """
    if not self._client:
        self._client = self._init_client()
    
    buckets = self._client.list_buckets()
    for bucket in buckets:
        yield models.Bucket(
            name=bucket.name,
            created_time=bucket.creation_date
        )
```

#### Upload Object

```python
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
        *args: Additional positional arguments
        **kwargs: Additional keyword arguments including metadata, content_type
        
    Raises:
        RuntimeError: If upload operation fails
        FileNotFoundError: If source file doesn't exist
    """
    if not self._client:
        self._client = self._init_client()
    
    # Check if file exists
    import os
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Extract additional arguments
    metadata = kwargs.pop("metadata", {})
    content_type = kwargs.pop("content_type", None)
    
    # Upload file
    try:
        self._client.fput_object(
            bucket_name=bucket,
            object_name=key,
            file_path=file_path,
            metadata=metadata,
            content_type=content_type
        )
        logger.info(f"Successfully uploaded {file_path} to {bucket}/{key}")
    except Exception as e:
        logger.error(f"Failed to upload {file_path}: {e}")
        raise RuntimeError(f"Upload failed: {e}") from e
```

#### Download Object

```python
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
        *args: Additional positional arguments
        **kwargs: Additional keyword arguments
        
    Raises:
        RuntimeError: If download operation fails
        FileNotFoundError: If object doesn't exist
    """
    if not self._client:
        self._client = self._init_client()
    
    # Create directory if it doesn't exist
    import os
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    try:
        self._client.fget_object(
            bucket_name=bucket,
            object_name=key,
            file_path=file_path
        )
        logger.info(f"Successfully downloaded {bucket}/{key} to {file_path}")
    except Exception as e:
        logger.error(f"Failed to download {bucket}/{key}: {e}")
        raise RuntimeError(f"Download failed: {e}") from e
```

#### Get Object

```python
def _get_object(self, key: str, bucket: str, *args, **kwargs):
    """Get an object from the storage system
    
    Args:
        key (str): Object key name
        bucket (str): Bucket name
        *args: Additional positional arguments
        **kwargs: Additional keyword arguments
        
    Returns:
        Object: Object with content and metadata
        
    Raises:
        RuntimeError: If get operation fails
        FileNotFoundError: If object doesn't exist
    """
    if not self._client:
        self._client = self._init_client()
    
    try:
        response = self._client.get_object(
            bucket_name=bucket,
            object_name=key
        )
        
        # Create Object with content and metadata
        from io import BytesIO
        content = response.read()
        response.close()
        
        return models.Object(
            body=BytesIO(content),
            updated_time=response.last_modified
        )
        
    except Exception as e:
        logger.error(f"Failed to get {bucket}/{key}: {e}")
        raise RuntimeError(f"Get operation failed: {e}") from e
```

#### List Objects

```python
def _list_objects(
    self, bucket: str, prefix: str, *args, **kwargs
):
    """List objects in a bucket with optional prefix filter
    
    Args:
        bucket (str): Bucket name
        prefix (str): Optional prefix to filter objects
        *args: Additional positional arguments
        **kwargs: Additional keyword arguments including recursive
        
    Returns:
        Generator[models.ObjectMetadata, None, None]: Generator of object metadata
    """
    if not self._client:
        self._client = self._init_client()
    
    recursive = kwargs.get("recursive", True)
    
    try:
        objects = self._client.list_objects(
            bucket_name=bucket,
            prefix=prefix,
            recursive=recursive
        )
        
        for obj in objects:
            yield models.ObjectMetadata(
                key=obj.object_name,
                updated_time=obj.last_modified,
                size=obj.size
            )
            
    except Exception as e:
        logger.error(f"Failed to list objects in {bucket}: {e}")
        raise RuntimeError(f"List objects failed: {e}") from e
```

#### Delete Object

```python
def _delete_object(self, key: str, bucket: str, *args, **kwargs):
    """Delete an object from the storage system
    
    Args:
        key (str): Object key name
        bucket (str): Bucket name
        *args: Additional positional arguments
        **kwargs: Additional keyword arguments including version_id
        
    Raises:
        RuntimeError: If delete operation fails
        FileNotFoundError: If object doesn't exist
    """
    if not self._client:
        self._client = self._init_client()
    
    version_id = kwargs.get("version_id")
    
    try:
        if version_id:
            self._client.remove_object(
                bucket_name=bucket,
                object_name=key,
                version_id=version_id
            )
        else:
            self._client.remove_object(
                bucket_name=bucket,
                object_name=key
            )
        
        logger.info(f"Successfully deleted {bucket}/{key}")
        
    except Exception as e:
        logger.error(f"Failed to delete {bucket}/{key}: {e}")
        raise RuntimeError(f"Delete operation failed: {e}") from e
```

#### Copy Object

```python
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
        *args: Additional positional arguments
        **kwargs: Additional keyword arguments including metadata, conditions
        
    Returns:
        Copy operation result
        
    Raises:
        RuntimeError: If copy operation fails
        FileNotFoundError: If source object doesn't exist
    """
    if not self._client:
        self._client = self._init_client()
    
    # Extract additional arguments
    metadata = kwargs.get("metadata", {})
    conditions = kwargs.get("conditions")
    
    try:
        # Get source object for metadata
        source_stat = self._client.stat_object(
            bucket_name=src_bucket,
            object_name=src_object
        )
        
        # Copy object
        result = self._client.copy_object(
            bucket_name=dst_bucket,
            object_name=dst_object,
            source=f"{src_bucket}/{src_object}",
            metadata=metadata,
            conditions=conditions
        )
        
        logger.info(f"Successfully copied {src_bucket}/{src_object} to {dst_bucket}/{dst_object}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to copy {src_bucket}/{src_object}: {e}")
        raise RuntimeError(f"Copy operation failed: {e}") from e
```

### Presigned URL Operations

#### Get Presigned URL

```python
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
        *args: Additional positional arguments
        **kwargs: Additional keyword arguments including response_headers
        
    Returns:
        str: Presigned download URL
    """
    if not self._client:
        self._client = self._init_client()
    
    try:
        response = self._client.get_presigned_url(
            method="GET",
            bucket_name=bucket,
            object_name=key,
            expires=expires,
            **kwargs
        )
        
        logger.info(f"Generated presigned URL for {bucket}/{key}")
        return response
        
    except Exception as e:
        logger.error(f"Failed to generate presigned URL for {bucket}/{key}: {e}")
        raise RuntimeError(f"Presigned URL generation failed: {e}") from e
```

#### Get Presigned Upload URL

```python
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
        *args: Additional positional arguments
        **kwargs: Additional keyword arguments including content_type
        
    Returns:
        str: Presigned upload URL
    """
    if not self._client:
        self._client = self._init_client()
    
    try:
        response = self._client.get_presigned_url(
            method="PUT",
            bucket_name=bucket,
            object_name=key,
            expires=expires,
            **kwargs
        )
        
        logger.info(f"Generated presigned upload URL for {bucket}/{key}")
        return response
        
    except Exception as e:
        logger.error(f"Failed to generate presigned upload URL for {bucket}/{key}: {e}")
        raise RuntimeError(f"Presigned upload URL generation failed: {e}") from e
```

### MinIO Adapter Factory

```python
class ObjectStoreComponentFactory(abstract.ObjectStoreComponentFactory):
    """Factory for creating MinIO adapter instances"""
    
    def _create_client(self, *args, **kwargs) -> ObjectStoreClient:
        """Create MinIO adapter instance
        
        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
            
        Returns:
            ObjectStoreClient: Configured MinIO adapter instance
        """
        return ObjectStoreClient(config=self.config, *args, **kwargs)
```

## Adapter Pattern Usage

### Creating Custom Adapters

To add support for new storage backends, follow these steps:

#### 1. Create the Adapter Class

```python
from data_store.nosql_store import abstract, configurations

class CustomNoSQLStore(abstract.NoSQLStore):
    """Custom NoSQL store implementation"""
    
    def __init__(self, config: dict[str, Any] | configurations.NoSQLConfiguration):
        super().__init__(config)
        # Initialize custom connection parameters
        self._connection = None
    
    def _connect(self, *args, **kwargs):
        """Establish connection to custom storage system"""
        # Implement connection logic
        self._connection = self._create_connection()
        return self._connection
    
    def _close(self, *args, **kwargs):
        """Close connection to custom storage system"""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def _insert(self, collection: str, data: dict, *args, **kwargs) -> str:
        """Insert document into custom storage system"""
        # Implement insert logic
        return self._connection.insert(collection, data)
    
    # ... implement all other abstract methods
    
    def _create_connection(self):
        """Create connection to custom storage system"""
        # Implement connection creation
        pass
```

#### 2. Create the Factory Class

```python
from data_store.nosql_store import abstract

class CustomNoSQLStoreComponentFactory(abstract.NoSQLStoreComponentFactory):
    """Factory for creating custom NoSQL store instances"""
    
    def _create_client(self, *args, **kwargs) -> abstract.NoSQLStore:
        """Create custom NoSQL store instance"""
        return CustomNoSQLStore(config=self.config, *args, **kwargs)
```

#### 3. Register the Adapter

```python
from data_store.nosql_store.adapters import adapter_routers

# Register the custom adapter
adapter_routers["custom"] = CustomNoSQLStoreComponentFactory
```

### Object Store Custom Adapter Example

```python
from data_store.object_store import abstract, configurations

class CustomObjectStoreClient(abstract.ObjectStoreClient):
    """Custom object store implementation"""
    
    def __init__(self, config: dict[str, Any] | configurations.ObjectStoreConfiguration):
        super().__init__(config)
        # Initialize custom storage client
        self._storage_client = None
    
    def _init_client(self, *args, **kwargs):
        """Initialize custom storage client"""
        # Implement client initialization
        return self._create_storage_client()
    
    def _list_buckets(self, *args, **kwargs):
        """List buckets in custom storage system"""
        # Implement list buckets logic
        buckets = self._storage_client.list_buckets()
        for bucket in buckets:
            yield models.Bucket(name=bucket["name"], created_time=bucket["created"])
    
    def _upload_object(self, file_path: str, key: str, bucket: str, *args, **kwargs):
        """Upload object to custom storage system"""
        # Implement upload logic
        self._storage_client.upload_file(file_path, key, bucket)
    
    # ... implement all other abstract methods
    
    def _create_storage_client(self):
        """Create custom storage client"""
        # Implement client creation
        pass

class CustomObjectStoreComponentFactory(abstract.ObjectStoreComponentFactory):
    """Factory for creating custom object store instances"""
    
    def _create_client(self, *args, **kwargs) -> abstract.ObjectStoreClient:
        """Create custom object store instance"""
        return CustomObjectStoreClient(config=self.config, *args, **kwargs)

# Register the adapter
from data_store.object_store.adapters import adaper_routers
adaper_routers["custom"] = CustomObjectStoreComponentFactory
```

## Adapter Extension Points

### Custom Connection Handling

```python
class EnhancedMongoDBAdapter(NoSQLStore):
    """Enhanced MongoDB adapter with custom connection handling"""
    
    def __init__(self, config: dict[str, Any] | configurations.NoSQLConfiguration):
        super().__init__(config)
        self._connection_pool = []
        self._max_pool_size = 10
    
    def _get_connection(self):
        """Get connection from pool or create new one"""
        if self._connection_pool:
            return self._connection_pool.pop()
        else:
            return self._create_new_connection()
    
    def _release_connection(self, connection):
        """Release connection back to pool"""
        if len(self._connection_pool) < self._max_pool_size:
            self._connection_pool.append(connection)
        else:
            connection.close()
    
    def _create_new_connection(self):
        """Create new MongoDB connection"""
        return pymongo.MongoClient(
            self.config.connection.connection_uri,
            serverSelectionTimeoutMS=self.config.connection.connection_timeout * 1000
        )
```

### Custom Error Handling

```python
class RobustMinIOAdapter(ObjectStoreClient):
    """MinIO adapter with custom error handling and retries"""
    
    def __init__(self, config: dict[str, Any] | configurations.ObjectStoreConfiguration):
        super().__init__(config)
        self._max_retries = 3
        self._retry_delay = 1.0
    
    def _upload_object_with_retry(self, file_path: str, key: str, bucket: str, *args, **kwargs):
        """Upload object with retry logic"""
        import time
        from pathlib import Path
        
        for attempt in range(self._max_retries):
            try:
                # Check if file exists
                if not Path(file_path).exists():
                    raise FileNotFoundError(f"File not found: {file_path}")
                
                # Upload file
                self._upload_object(file_path, key, bucket, *args, **kwargs)
                return
                
            except Exception as e:
                if attempt == self._max_retries - 1:
                    raise RuntimeError(f"Upload failed after {self._max_retries} attempts: {e}")
                
                # Wait before retry
                time.sleep(self._retry_delay * (2 ** attempt))  # Exponential backoff
```

### Custom Logging and Monitoring

```python
import logging
from functools import wraps

class MonitoredMongoDBAdapter(NoSQLStore):
    """MongoDB adapter with custom logging and monitoring"""
    
    def __init__(self, config: dict[str, Any] | configurations.NoSQLConfiguration):
        super().__init__(config)
        self._logger = logging.getLogger(__name__)
        self._operation_times = {}
    
    def _log_operation_time(self, operation_name: str, start_time: float, end_time: float):
        """Log operation execution time"""
        duration = end_time - start_time
        self._operation_times[operation_name] = self._operation_times.get(operation_name, []) + [duration]
        
        self._logger.info(
            f"Operation {operation_name} completed in {duration:.3f}s "
            f"(avg: {sum(self._operation_times[operation_name])/len(self._operation_times[operation_name]):.3f}s)"
        )
    
    def _monitor_operation(self, operation_name: str):
        """Decorator to monitor operation execution time"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                import time
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    end_time = time.time()
                    self._log_operation_time(operation_name, start_time, end_time)
            return wrapper
        return decorator
    
    @_monitor_operation("insert")
    def _insert(self, collection: str, data: dict, *args, **kwargs) -> str:
        """Insert with monitoring"""
        return super()._insert(collection, data, *args, **kwargs)
    
    @_monitor_operation("find")
    def _find(self, collection: str, filters: dict | None = None, *args, **kwargs) -> list:
        """Find with monitoring"""
        return super()._find(collection, filters, *args, **kwargs)
```

## Adapter Testing

### Unit Testing Adapters

```python
import unittest
from unittest.mock import Mock, patch, MagicMock
from data_store.nosql_store.adapters.mongodb_adapter import NoSQLStore
from data_store.object_store.adapters.minio_adapter import ObjectStoreClient

class TestMongoDBAdapter(unittest.TestCase):
    """Test cases for MongoDB adapter"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            "framework": "mongodb",
            "connection": {
                "host": "localhost",
                "port": 27017,
                "database": "test_db"
            }
        }
        self.adapter = NoSQLStore(self.config)
    
    @patch('pymongo.MongoClient')
    def test_connection_establishment(self, mock_mongo_client):
        """Test connection establishment"""
        # Mock MongoDB client
        mock_client = Mock()
        mock_client.admin.command.return_value = None
        mock_mongo_client.return_value = mock_client
        
        # Test connection
        connection = self.adapter._connect()
        
        # Verify connection was established
        self.assertEqual(connection, mock_client)
        mock_mongo_client.assert_called_once()
    
    @patch('pymongo.MongoClient')
    def test_insert_operation(self, mock_mongo_client):
        """Test insert operation"""
        # Mock MongoDB client and collection
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.insert_one.return_value = Mock(inserted_id="test_id")
        mock_client.__getitem__.return_value = mock_collection
        mock_mongo_client.return_value = mock_client
        
        # Set up adapter with mocked client
        self.adapter._client = mock_client
        
        # Test insert
        result = self.adapter._insert("test_collection", {"test": "data"})
        
        # Verify result
        self.assertEqual(result, "test_id")
        mock_collection.insert_one.assert_called_once_with({"test": "data"})

class TestMinIOAdapter(unittest.TestCase):
    """Test cases for MinIO adapter"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            "framework": "minio",
            "root_bucket": "test-bucket",
            "connection": {
                "endpoint": "localhost:9000",
                "access_key": "minioadmin",
                "secret_key": "minioadmin",
                "secure": False
            }
        }
        self.adapter = ObjectStoreClient(self.config)
    
    @patch('minio.Minio')
    def test_client_initialization(self, mock_minio_client):
        """Test MinIO client initialization"""
        # Mock MinIO client
        mock_client = Mock()
        mock_client.list_buckets.return_value = []
        mock_minio_client.return_value = mock_client
        
        # Test client initialization
        client = self.adapter._init_client()
        
        # Verify client was initialized
        self.assertEqual(client, mock_client)
        mock_minio_client.assert_called_once()
    
    @patch('minio.Minio')
    def test_upload_operation(self, mock_minio_client):
        """Test upload operation"""
        # Mock MinIO client
        mock_client = Mock()
        mock_client.fput_object.return_value = None
        mock_minio_client.return_value = mock_client
        
        # Set up adapter with mocked client
        self.adapter._client = mock_client
        
        # Test upload
        self.adapter._upload_object("/tmp/test.txt", "test.txt", "test-bucket")
        
        # Verify upload was called
        mock_client.fput_object.assert_called_once_with(
            bucket_name="test-bucket",
            object_name="test.txt",
            file_path="/tmp/test.txt",
            metadata={},
            content_type=None
        )
```

### Integration Testing

```python
import pytest
import tempfile
import os
from data_store.nosql_store.adapters.mongodb_adapter import NoSQLStore
from data_store.object_store.adapters.minio_adapter import ObjectStoreClient

class TestAdapterIntegration:
    """Integration tests for adapters"""
    
    @pytest.fixture
    def mongodb_adapter(self):
        """Create test MongoDB adapter"""
        config = {
            "framework": "mongodb",
            "connection": {
                "host": "localhost",
                "port": 27017,
                "database": "test_integration"
            }
        }
        return NoSQLStore(config)
    
    @pytest.fixture
    def minio_adapter(self):
        """Create test MinIO adapter"""
        config = {
            "framework": "minio",
            "root_bucket": "test-integration",
            "connection": {
                "endpoint": "localhost:9000",
                "access_key": "minioadmin",
                "secret_key": "minioadmin",
                "secure": False
            }
        }
        return ObjectStoreClient(config)
    
    def test_mongodb_crud_operations(self, mongodb_adapter):
        """Test MongoDB CRUD operations"""
        with mongodb_adapter.connect() as connection:
            # Test insert
            doc_id = mongodb_adapter.insert("test_collection", {"name": "test", "value": 123})
            self.assertIsNotNone(doc_id)
            
            # Test find
            results = mongodb_adapter.find("test_collection", filters={"name": "test"})
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["name"], "test")
            
            # Test update
            updated = mongodb_adapter.update("test_collection", {"name": "test"}, {"$set": {"value": 456}})
            self.assertEqual(updated, 1)
            
            # Test delete
            deleted = mongodb_adapter.delete("test_collection", {"name": "test"})
            self.assertEqual(deleted, 1)
    
    def test_minio_file_operations(self, minio_adapter):
        """Test MinIO file operations"""
        # Create test file
        test_content = b"Hello, World!"
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file_path = temp_file.name
        
        try:
            # Test upload
            minio_adapter._upload_object(temp_file_path, "test-upload.txt", "test-integration")
            
            # Test list objects
            objects = list(minio_adapter._list_objects("test-integration", ""))
            self.assertTrue(len(objects) > 0)
            
            # Test download
            download_path = "/tmp/test-download.txt"
            minio_adapter._download_object("test-upload.txt", download_path, "test-integration")
            
            # Verify downloaded content
            with open(download_path, "rb") as f:
                downloaded_content = f.read()
            self.assertEqual(downloaded_content, test_content)
            
            # Test delete
            minio_adapter._delete_object("test-upload.txt", "test-integration")
            
        finally:
            # Cleanup
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            if os.path.exists("/tmp/test-download.txt"):
                os.remove("/tmp/test-download.txt")
```

## Adapter Best Practices

### 1. Connection Management

```python
class BestPracticeMongoDBAdapter(NoSQLStore):
    """MongoDB adapter with best practices for connection management"""
    
    def __init__(self, config: dict[str, Any] | configurations.NoSQLConfiguration):
        super().__init__(config)
        self._client = None
        self._database = None
        self._connection_timeout = 30  # seconds
    
    def _connect(self, *args, **kwargs):
        """Establish connection with timeout and retry logic"""
        import time
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self._client = self._init_client(*args, **kwargs)
                return self._client
            except Exception as e:
                if attempt == max_retries - 1:
                    raise RuntimeError(f"Failed to connect after {max_retries} attempts: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def _close(self, *args, **kwargs):
        """Close connection gracefully"""
        if self._client:
            try:
                self._client.close()
            except Exception as e:
                self._logger.warning(f"Error closing connection: {e}")
            finally:
                self._client = None
                self._database = None
```

### 2. Error Handling

```python
class BestPracticeMinIOAdapter(ObjectStoreClient):
    """MinIO adapter with comprehensive error handling"""
    
    def _handle_storage_errors(self, operation: str, error: Exception):
        """Handle storage-specific errors with appropriate messages"""
        error_mapping = {
            "NoSuchBucket": "The specified bucket does not exist",
            "NoSuchKey": "The specified object does not exist",
            "AccessDenied": "Access denied - check your credentials",
            "ConnectionError": "Failed to connect to storage service",
            "Timeout": "Operation timed out - try again later"
        }
        
        error_message = str(error)
        for error_type, message in error_mapping.items():
            if error_type in error_message:
                raise RuntimeError(f"{operation} failed: {message}") from error
        
        # Generic error handling
        raise RuntimeError(f"{operation} failed: {error_message}") from error
    
    def _upload_object(self, file_path: str, key: str, bucket: str, *args, **kwargs):
        """Upload object with comprehensive error handling"""
        try:
            # Validate inputs
            if not file_path or not key or not bucket:
                raise ValueError("file_path, key, and bucket are required")
            
            # Check file exists
            import os
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Check file is readable
            if not os.access(file_path, os.R_OK):
                raise PermissionError(f"File not readable: {file_path}")
            
            # Perform upload
            super()._upload_object(file_path, key, bucket, *args, **kwargs)
            
        except Exception as e:
            self._handle_storage_errors("Upload", e)
```

### 3. Performance Optimization

```python
class OptimizedMongoDBAdapter(NoSQLStore):
    """MongoDB adapter with performance optimizations"""
    
    def __init__(self, config: dict[str, Any] | configurations.NoSQLConfiguration):
        super().__init__(config)
        self._query_cache = {}
        self._cache_ttl = 300  # 5 minutes
    
    def _find_with_cache(self, collection: str, filters: dict | None = None, *args, **kwargs):
        """Find operation with caching"""
        cache_key = f"{collection}:{hash(str(filters))}:{hash(str(args))}:{hash(str(kwargs))}"
        
        # Check cache
        if cache_key in self._query_cache:
            cached_result, timestamp = self._query_cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                return cached_result
        
        # Perform query
        result = super()._find(collection, filters, *args, **kwargs)
        
        # Cache result
        self._query_cache[cache_key] = (result, time.time())
        
        # Limit cache size
        if len(self._query_cache) > 1000:
            oldest_key = min(self._query_cache.keys(), 
                           key=lambda k: self._query_cache[k][1])
            del self._query_cache[oldest_key]
        
        return result
    
    def _bulk_insert_optimized(self, collection: str, data: list[dict], *args, **kwargs) -> str:
        """Optimized bulk insert with batch processing"""
        batch_size = 1000
        total_inserted = 0
        
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            result = super()._bulk_insert(collection, batch, *args, **kwargs)
            total_inserted += int(result)
        
        return str(total_inserted)
```

### 4. Security Considerations

```python
class SecureMongoDBAdapter(NoSQLStore):
    """MongoDB adapter with security enhancements"""
    
    def __init__(self, config: dict[str, Any] | configurations.NoSQLConfiguration):
        super().__init__(config)
        self._allowed_collections = {"users", "products", "orders"}
        self._max_document_size = 16 * 1024 * 1024  # 16MB
    
    def _validate_collection_access(self, collection: str):
        """Validate access to collection"""
        if collection not in self._allowed_collections:
            raise PermissionError(f"Access to collection '{collection}' is not allowed")
    
    def _validate_document_size(self, data: dict):
        """Validate document size"""
        import json
        document_size = len(json.dumps(data).encode('utf-8'))
        if document_size > self._max_document_size:
            raise ValueError(f"Document size ({document_size} bytes) exceeds maximum allowed size ({self._max_document_size} bytes)")
    
    def _insert(self, collection: str, data: dict, *args, **kwargs) -> str:
        """Insert with security validation"""
        self._validate_collection_access(collection)
        self._validate_document_size(data)
        
        # Sanitize data if needed
        sanitized_data = self._sanitize_data(data)
        
        return super()._insert(collection, sanitized_data, *args, **kwargs)
    
    def _sanitize_data(self, data: dict) -> dict:
        """Sanitize input data"""
        # Remove potentially dangerous fields
        dangerous_fields = ["__proto__", "constructor", "prototype"]
        sanitized = data.copy()
        
        for field in dangerous_fields:
            sanitized.pop(field, None)
        
        return sanitized
```

## Conclusion

The adapter system in the data_store project provides a robust foundation for supporting multiple storage backends. Key features include:

- **Consistent Interfaces**: All adapters implement the same abstract interfaces
- **Easy Extension**: Simple process to add new storage backends
- **Type Safety**: Strong typing ensures adapter implementations follow expected contracts
- **Error Handling**: Consistent error handling across different storage systems
- **Performance Optimization**: Built-in support for connection pooling, caching, and batch operations

The MongoDB and MinIO adapters serve as reference implementations that demonstrate best practices for adapter development. By following the patterns and guidelines outlined in this documentation, developers can create high-quality adapters for additional storage backends.

For more information about using the storage systems, see:
- {doc}`../user_guides/nosql_store` - NoSQL store interface and usage
- {doc}`../user_guides/object_store` - Object store interface and usage
- {doc}`abstract_base_classes` - Abstract interfaces and design patterns
- {doc}`configuration_classes` - Configuration models and validation
- {doc}`models` - Data models and structures