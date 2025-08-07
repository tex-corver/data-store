# Getting Started with tex-corver-data-store

Welcome to tex-corver-data-store! This guide will help you get up and running with the library quickly.

## Overview

tex-corver-data-store is a Python library that provides a unified interface for multiple storage backends, including:

- **NoSQL databases** (MongoDB, CouchDB, DynamoDB)
- **Object storage** (MinIO, AWS S3)
- **SQL databases** (PostgreSQL, MySQL, SQLite)
- **Vector databases** (for AI/ML applications)

The library uses abstract base classes and adapters to provide a consistent API across different storage systems.

## Installation

Install the library using pip:

```bash
pip install tex-corver-data-store
```

For development installation:

```bash
git clone https://github.com/your-repo/tex-corver-data-store.git
cd tex-corver-data-store
pip install -e .
```

## Quick Start

### NoSQL Store

```python
from data_store import NoSQLStore

# Initialize with configuration
config = {
    "framework": "mongodb",
    "host": "localhost",
    "port": 27017,
    "database": "myapp"
}

# Create store instance
store = NoSQLStore(config)

# Use context manager for connection
with store.connect() as connection:
    # Insert a document
    doc_id = store.insert("users", {
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30
    })
    
    # Find documents
    users = store.find("users", {"age": {"$gt": 25}})
    
    # Update documents
    updated = store.update("users", {"email": "john@example.com"}, 
                          {"$set": {"age": 31}})
    
    # Delete documents
    deleted = store.delete("users", {"email": "john@example.com"})
```

### Object Store

```python
from data_store import ObjectStore

# Initialize with configuration
config = {
    "framework": "minio",
    "root_bucket": "my-app-data",
    "connection": {
        "endpoint": "localhost:9000",
        "access_key": "your-access-key",
        "secret_key": "your-secret-key",
        "secure": False
    }
}

# Create store instance
store = ObjectStore(config)

# Upload a file
result = store.upload_file(
    file_path="/path/to/local/file.txt",
    key="uploads/file.txt"
)

# Download a file
store.download_file(
    key="uploads/file.txt",
    file_path="/path/to/local/download.txt"
)

# List files
for file_meta in store.list_files(prefix="uploads/"):
    print(f"File: {file_meta.key}, Size: {file_meta.size}")
```

## Configuration

The library uses Pydantic models for configuration, providing type safety and validation.

### Environment Variables

You can configure the library using environment variables:

```bash
# NoSQL Store
export NOSQL_STORE_FRAMEWORK=mongodb
export NOSQL_STORE_HOST=localhost
export NOSQL_STORE_PORT=27017
export NOSQL_STORE_DATABASE=myapp

# Object Store
export OBJECT_STORE_FRAMEWORK=minio
export OBJECT_STORE_ROOT_BUCKET=my-app-data
export OBJECT_STORE_ENDPOINT=localhost:9000
export OBJECT_STORE_ACCESS_KEY=your-access-key
export OBJECT_STORE_SECRET_KEY=your-secret-key
```

### Configuration Files

Create a configuration file (e.g., `config.yaml`):

```yaml
data_store:
  nosql:
    framework: mongodb
    host: localhost
    port: 27017
    database: myapp
  
  object_store:
    framework: minio
    root_bucket: my-app-data
    connection:
      endpoint: localhost:9000
      access_key: your-access-key
      secret_key: your-secret-key
      secure: false
```

## Core Concepts

### Abstract Base Classes

The library is built around abstract base classes that define consistent interfaces:

- `NoSQLStore`: Interface for NoSQL database operations
- `ObjectStoreClient`: Interface for object storage operations
- `SQLStore`: Interface for SQL database operations
- `VectorStore`: Interface for vector database operations

### Adapters

Adapters provide concrete implementations for different storage backends:

- **NoSQL**: MongoDB, CouchDB, DynamoDB adapters
- **Object Storage**: MinIO, AWS S3 adapters
- **SQL**: PostgreSQL, MySQL, SQLite adapters
- **Vector**: Various vector database adapters

### Factory Pattern

The library uses the factory pattern to create appropriate clients based on configuration:

```python
# Configuration determines which adapter to use
config = {"framework": "mongodb"}
store = NoSQLStore(config)  # Uses MongoDB adapter
```

## Next Steps

- **User Guides**: Learn about specific features and best practices
- **API Reference**: Detailed documentation of all classes and methods
- **Development**: Information for contributors and extenders

For more detailed information about configuration options, see the {doc}`api_reference/configuration_classes` documentation.