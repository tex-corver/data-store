# Data store Documentation

## Overview

data-store is a Python library that provides a unified interface for multiple storage backends, including:

- **NoSQL databases** (MongoDB, ~~CouchDB, DynamoDB~~)
- **Object storage** (MinIO, ~~AWS S3~~)
- ~~**SQL databases** (PostgreSQL, MySQL, SQLite)~~
- ~~**Vector databases** (for AI/ML applications)~~

The library uses abstract base classes and adapters to provide a consistent API across different storage systems.

## Installation

Install the library using poetry:

```bash
poetry add git+ssh://git@github.com/tex-corver/data-store.git
```

For development installation:

```bash
git clone https://github.com/tex-corver/data-store.git
cd data-store
poetry install
```

## Quick Start

### NoSQL Store

```python
from data_store import NoSQLStore

# Initialize with configuration
config = {
    "framework": "mongodb",
    "connection": {
        "host": "localhost",
        "port": 27017,
        "username": "your-username",
        "password": "your-password",
        "auth_source": "admin",
        "connection_timeout": 5000,
        "database": "myapp"
    }
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
    }) # or connection.insert(...)
    
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

### Configuration Files

Create a configuration file (e.g., `config.yaml`):

```yaml
data_store:
  nosql:
    framework: mongodb
    connection:
      host: localhost
      port: 27017
      username: your-username
      password: your-password
      auth_source: admin
      connection_timeout: 5000
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

## Codebase Design


## API Reference

The full API reference is generated automatically and can be found in the `api_reference` directory.

```{toctree}
:maxdepth: 2
:caption: Sections

user_guides/index
api_reference/index
development/index