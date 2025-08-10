# NoSQL Store Interface Documentation

This document provides comprehensive documentation for the `NoSQLStore` class, detailing its API, usage patterns, integration considerations, and best practices. It is intended for developers looking to use or extend the NoSQL store functionality.

## Overview

The `NoSQLStore` class offers a high-level interface for NoSQL operations. It integrates with abstract base classes and adapters to support multiple frameworks (e.g., MongoDB) and handles connection management, CRUD operations, bulk operations, and error handling.

## Configuration and Initialization

The store is initialized with an optional configuration dictionary. If no configuration is provided, it retrieves settings via `utils.get_config()`. Proper configuration is required to establish the underlying NoSQL client.

**Example:**
```python
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
store = NoSQLStore(config)
```

## Connection Management

The `connect` method returns a context manager that manages the connection lifecycle automatically.

**Usage:**
```python
with store.connect() as connection:
    # Perform operations while connected
    store.insert("users", {"name": "Alice"})
```
- On entering the context, a connection is established.
- On exit, the connection is automatically closed.

## CRUD Operations

### Insert
- **Method:** `insert(collection: str, data: dict, *args, **kwargs) -> str`
- **Description:** Inserts a document into the specified collection.
- **Returns:** ID of the inserted document.
- **Example:**
```python
doc_id = store.insert("users", {"name": "John", "age": 30})
```

### Find
- **Method:** `find(collection: str, filters: dict | None = None, projections: list[str] | None = None, skip: int = 0, limit: int = 0, *args, **kwargs) -> list`
- **Description:** Retrieves documents matching the query.
- **Parameters:**
  - `filters`: Query criteria (None retrieves all documents).
  - `projections`: Fields to include in the result.
  - `skip`: Number of documents to skip.
  - `limit`: Maximum number of documents to return.
- **Example:**
```python
results = store.find("users", filters={"age": {"$gt": 20}}, projections=["name", "age"])
```

### Update
- **Method:** `update(collection: str, filters: dict, update_data: dict, upsert: bool = False, *args, **kwargs) -> int`
- **Description:** Updates documents matching the filter in a collection.
- **Returns:** Number of documents modified.
- **Example:**
```python
num_updated = store.update("users", {"name": "John"}, {"$set": {"age": 31}})
```

### Delete
- **Method:** `delete(collection: str, filters: dict, *args, **kwargs) -> int`
- **Description:** Deletes documents from the specified collection.
- **Returns:** Number of documents deleted.
- **Example:**
```python
num_deleted = store.delete("users", {"name": "John"})
```

## Bulk Operations

### Bulk Insert
- **Method:** `bulk_insert(collection: str, data: list[dict], *args, **kwargs) -> str`
- **Description:** Inserts multiple documents into a collection.
- **Returns:** String representation of the count of inserted documents.
- **Example:**
```python
result = store.bulk_insert("users", [{"name": "John"}, {"name": "Jane"}])
```

### Bulk Update
- **Method:** `bulk_update(collection: str, filters: dict, update_data: list[dict] | dict, upsert: bool = False, *args, **kwargs) -> int`
- **Description:** Updates multiple documents based on provided filters.
- **Returns:** Total number of documents modified.
- **Example:**
```python
num_updated = store.bulk_update("users", {"active": True}, [{"$set": {"last_login": "now"}}])
```

### Bulk Delete
- **Method:** `bulk_delete(collection: str, filters: dict | list, *args, **kwargs) -> int`
- **Description:** Deletes multiple documents based on the given filter(s).
- **Returns:** Total number of documents deleted.
- **Example:**
```python
num_deleted = store.bulk_delete("users", {"status": "inactive"})
```

## Error Handling

- Methods may raise a `ValueError` if required parameters are missing or invalid.
- A `RuntimeError` is raised for operational failures.
- It is recommended to handle these exceptions to maintain application stability.

## Integration with Base Classes and Adapters

The `NoSQLStore` class:
- Utilizes an abstract factory (`NoSQLStoreComponentFactory`) to create an underlying client.
- Supports multiple frameworks through an adapter router (`adapters.adapter_routers`).
- Ensures proper instantiation and connection based on provided configuration.

## Configuration Setup and Best Practices

- Ensure configuration parameters match the targeted NoSQL framework.
- Use context managers provided by `connect` to manage connection lifecycle.
- Validate input parameters before performing database operations.
- Implement logging to capture runtime errors and diagnostic information.

## Conclusion

The `NoSQLStore` offers a robust interface for NoSQL operations, abstracting complex direct database interactions. This documentation serves as a guide for developers to integrate and use the NoSQL store effectively, with clear examples and best practices.

For more details, consult the adapter and configuration modules documentation.