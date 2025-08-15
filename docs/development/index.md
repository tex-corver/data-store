# Development

This section provides information for developers who want to contribute to the tex-corver-data-store library or extend its functionality.

## Architecture Overview

The tex-corver-data-store library is built around a modular architecture that supports multiple storage backends through a unified interface.

### Core Components

1. **Abstract Base Classes**: Define the interfaces that all storage implementations must follow
2. **Configuration Classes**: Pydantic models for type-safe configuration management
3. **Adapter Pattern**: Concrete implementations for different storage backends
4. **Factory Pattern**: Creates appropriate storage instances based on configuration

### Design Principles

- **Consistency**: All storage backends provide the same basic interface
- **Extensibility**: Easy to add new storage backends without changing existing code
- **Type Safety**: Strong typing throughout the library
- **Validation**: Automatic validation of configuration and data
- **Error Handling**: Consistent error handling across all implementations

### Directory Structure

```
src/data_store/
├── __init__.py                 # Main module exports
├── nosql_store/                # NoSQL database implementations
│   ├── __init__.py
│   ├── abstract.py            # NoSQL abstract base classes
│   ├── configurations.py      # NoSQL configuration models
│   ├── models.py              # NoSQL data models
│   ├── nosql_store.py         # Main NoSQL store implementation
│   └── adapters/              # NoSQL adapter implementations
│       ├── __init__.py
│       └── mongodb_adapter.py
├── object_store/              # Object storage implementations
│   ├── __init__.py
│   ├── abstract.py            # Object store abstract base classes
│   ├── configurations.py      # Object store configuration models
│   ├── models.py              # Object store data models
│   ├── store.py               # Main object store implementation
│   └── adapters/              # Object store adapter implementations
│       ├── __init__.py
│       └── minio_adapter.py
├── sql_store/                 # SQL database implementations
│   ├── __init__.py
│   └── adapters/              # SQL adapter implementations
└── vector_store/              # Vector database implementations
    ├── __init__.py
    └── adapters/              # Vector adapter implementations
```

## Extending the Library

### Adding a New Storage Backend

To add support for a new storage backend, follow these steps:

#### 1. Create Abstract Base Class

```python
# src/data_store/nosql_store/abstract.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class NoSQLStore(ABC):
    """Abstract base class for NoSQL store implementations."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._client = None
    
    @abstractmethod
    def _connect(self, *args, **kwargs) -> Any:
        """Establish connection to storage backend."""
        pass
    
    @abstractmethod
    def _close(self, *args, **kwargs) -> None:
        """Close connection to storage backend."""
        pass
    
    @abstractmethod
    def _insert(self, collection: str, data: Dict[str, Any], *args, **kwargs) -> str:
        """Insert document into collection."""
        pass
    
    @abstractmethod
    def _find(self, collection: str, filters: Optional[Dict[str, Any]] = None, *args, **kwargs) -> List[Dict[str, Any]]:
        """Find documents in collection."""
        pass
    
    @abstractmethod
    def _update(self, collection: str, filters: Dict[str, Any], update: Dict[str, Any], *args, **kwargs) -> int:
        """Update documents in collection."""
        pass
    
    @abstractmethod
    def _delete(self, collection: str, filters: Dict[str, Any], *args, **kwargs) -> int:
        """Delete documents from collection."""
        pass
```

#### 2. Create Configuration Model

```python
# src/data_store/nosql_store/configurations.py
from pydantic import BaseModel, Field
from enum import Enum

class Framework(str, Enum):
    MONGODB = "mongodb"
    COUCHDB = "couchdb"
    DYNAMODB = "dynamodb"
    NEW_BACKEND = "new_backend"

class NoSQLConnection(BaseModel):
    uri: Optional[str] = Field(None, description="Complete connection URI")
    host: Optional[str] = Field(None, description="Database host address")
    port: Optional[int] = Field(None, description="Database port number")
    username: Optional[str] = Field(None, description="Username for authentication")
    password: Optional[str] = Field(None, description="Password for authentication")
    database: Optional[str] = Field(None, description="Default database name")
    ssl: bool = Field(False, description="Enable SSL/TLS encryption")

class NoSQLConfiguration(BaseModel):
    framework: Framework = Field(Framework.MONGODB, description="Database framework")
    connection: NoSQLConnection = Field(..., description="Connection configuration")
```

#### 3. Create Adapter Implementation

```python
# src/data_store/nosql_store/adapters/new_backend_adapter.py
from typing import Any, Dict, List, Optional
from data_store.nosql_store.abstract import NoSQLStore
from data_store.nosql_store.configurations import NoSQLConfiguration

class NewBackendStore(NoSQLStore):
    """NewBackend NoSQL store implementation."""
    
    def __init__(self, config: Dict[str, Any] | NoSQLConfiguration):
        super().__init__(config)
        self._database = None
    
    def _connect(self, *args, **kwargs) -> Any:
        """Establish connection to NewBackend."""
        # Implement connection logic
        self._database = self._create_connection()
        return self._database
    
    def _close(self, *args, **kwargs) -> None:
        """Close connection to NewBackend."""
        if self._database:
            self._database.close()
            self._database = None
    
    def _insert(self, collection: str, data: Dict[str, Any], *args, **kwargs) -> str:
        """Insert document into collection."""
        # Implement insert logic
        return self._database.insert(collection, data)
    
    def _find(self, collection: str, filters: Optional[Dict[str, Any]] = None, *args, **kwargs) -> List[Dict[str, Any]]:
        """Find documents in collection."""
        # Implement find logic
        return self._database.find(collection, filters or {})
    
    def _update(self, collection: str, filters: Dict[str, Any], update: Dict[str, Any], *args, **kwargs) -> int:
        """Update documents in collection."""
        # Implement update logic
        return self._database.update(collection, filters, update)
    
    def _delete(self, collection: str, filters: Dict[str, Any], *args, **kwargs) -> int:
        """Delete documents from collection."""
        # Implement delete logic
        return self._database.delete(collection, filters)
    
    def _create_connection(self):
        """Create connection to NewBackend."""
        # Implement connection creation
        pass
```

#### 4. Create Factory Class

```python
# src/data_store/nosql_store/adapters/__init__.py
from data_store.nosql_store.abstract import NoSQLStoreComponentFactory
from data_store.nosql_store.configurations import NoSQLConfiguration
from .new_backend_adapter import NewBackendStore

class NewBackendComponentFactory(NoSQLStoreComponentFactory):
    """Factory for creating NewBackend store instances."""
    
    def _create_client(self, *args, **kwargs) -> NoSQLStore:
        """Create NewBackend store instance."""
        return NewBackendStore(config=self.config, *args, **kwargs)

# Register the adapter
adapter_registry = {
    "new_backend": NewBackendComponentFactory
}
```

#### 5. Update Main Module

```python
# src/data_store/nosql_store/__init__.py
from .abstract import NoSQLStore, NoSQLStoreComponentFactory
from .configurations import NoSQLConfiguration, NoSQLConnection, Framework
from .nosql_store import NoSQLStore as MainNoSQLStore
from .adapters import adapter_registry

__all__ = [
    "NoSQLStore",
    "NoSQLStoreComponentFactory", 
    "NoSQLConfiguration",
    "NoSQLConnection",
    "Framework",
    "MainNoSQLStore",
    "adapter_registry"
]
```

### Adding New Features

When adding new features to existing storage backends:

1. **Update Abstract Base Class**: Add new abstract methods to the base class
2. **Update All Adapters**: Implement the new methods in all existing adapters
3. **Add Tests**: Write comprehensive tests for the new functionality
4. **Update Documentation**: Document the new features and usage examples

## Testing Guidelines

### Unit Testing

Write unit tests for all components:

```python
# tests/nosql_store/unit/test_new_backend_adapter.py
import pytest
from unittest.mock import Mock, patch
from data_store.nosql_store.adapters.new_backend_adapter import NewBackendStore

class TestNewBackendStore:
    """Test cases for NewBackend store adapter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "framework": "new_backend",
            "connection": {
                "host": "localhost",
                "port": 5432,
                "database": "test_db"
            }
        }
        self.store = NewBackendStore(self.config)
    
    @patch('data_store.nosql_store.adapters.new_backend_adapter.NewBackendStore._create_connection')
    def test_connection_establishment(self, mock_create_connection):
        """Test connection establishment."""
        mock_connection = Mock()
        mock_create_connection.return_value = mock_connection
        
        connection = self.store._connect()
        
        assert connection == mock_connection
        mock_create_connection.assert_called_once()
    
    @patch('data_store.nosql_store.adapters.new_backend_adapter.NewBackendStore._create_connection')
    def test_insert_operation(self, mock_create_connection):
        """Test insert operation."""
        mock_connection = Mock()
        mock_connection.insert.return_value = "doc123"
        mock_create_connection.return_value = mock_connection
        
        self.store._client = mock_connection
        
        result = self.store._insert("test_collection", {"test": "data"})
        
        assert result == "doc123"
        mock_connection.insert.assert_called_once_with("test_collection", {"test": "data"})
```

### Integration Testing

Test with actual storage backends:

```python
# tests/nosql_store/integration/test_new_backend_integration.py
import pytest
from data_store.nosql_store import NoSQLStore

class TestNewBackendIntegration:
    """Integration tests for NewBackend adapter."""
    
    @pytest.fixture
    def store(self):
        """Create test store instance."""
        config = {
            "framework": "new_backend",
            "connection": {
                "host": "localhost",
                "port": 5432,
                "database": "test_db"
            }
        }
        return NoSQLStore(config)
    
    def test_crud_operations(self, store):
        """Test CRUD operations with actual database."""
        with store.connect() as connection:
            # Test insert
            doc_id = store.insert("test_collection", {"name": "test", "value": 123})
            assert doc_id is not None
            
            # Test find
            results = store.find("test_collection", {"name": "test"})
            assert len(results) == 1
            assert results[0]["value"] == 123
            
            # Test update
            updated = store.update("test_collection", {"name": "test"}, {"$set": {"value": 456}})
            assert updated == 1
            
            # Test delete
            deleted = store.delete("test_collection", {"name": "test"})
            assert deleted == 1
```

### End-to-End Testing

Test complete workflows:

```python
# tests/e2e/test_new_backend_workflow.py
import pytest
from data_store import NoSQLStore, ObjectStore

class TestNewBackendWorkflow:
    """End-to-end tests for NewBackend workflows."""
    
    def test_user_management_workflow(self):
        """Test complete user management workflow."""
        # Initialize stores
        nosql_config = {
            "framework": "new_backend",
            "connection": {
                "host": "localhost",
                "port": 5432,
                "database": "user_db"
            }
        }
        
        object_config = {
            "framework": "minio",
            "root_bucket": "user-data",
            "connection": {
                "endpoint": "localhost:9000",
                "access_key": "minioadmin",
                "secret_key": "minioadmin",
                "secure": False
            }
        }
        
        nosql_store = NoSQLStore(nosql_config)
        object_store = ObjectStore(object_config)
        
        # Create user
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "profile": {
                "name": "Test User",
                "age": 30
            }
        }
        
        with nosql_store.connect() as connection:
            user_id = nosql_store.insert("users", user_data)
            assert user_id is not None
            
            # Upload user avatar
            avatar_result = object_store.upload_file(
                file_path="/tmp/avatar.jpg",
                key=f"avatars/{user_id}.jpg"
            )
            assert avatar_result is not None
            
            # Update user with avatar reference
            updated = nosql_store.update(
                "users",
                {"_id": user_id},
                {"$set": {"avatar": f"avatars/{user_id}.jpg"}}
            )
            assert updated == 1
            
            # Verify user data
            user = nosql_store.find("users", {"_id": user_id})
            assert len(user) == 1
            assert user[0]["avatar"] == f"avatars/{user_id}.jpg"
```

## Contributing Guidelines

### Development Setup

1. **Fork the Repository**: Create a fork of the main repository
2. **Clone Your Fork**: Clone your fork locally
3. **Create Virtual Environment**: 
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install Dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   ```
5. **Install Pre-commit Hooks**:
   ```bash
   pre-commit install
   ```

### Code Style and Standards

- **PEP 8**: Follow Python style guidelines
- **Type Hints**: Use type hints for all function signatures
- **Docstrings**: Use Google-style docstrings
- **Black**: Use Black for code formatting
- **isort**: Use isort for import sorting

### Pull Request Process

1. **Create Feature Branch**: Create a branch from `develop`
2. **Make Changes**: Implement your changes
3. **Write Tests**: Add comprehensive tests
4. **Update Documentation**: Update relevant documentation
5. **Run Tests**: Ensure all tests pass
6. **Run Linters**: Ensure code passes linting
7. **Create Pull Request**: Submit PR to `develop` branch

### Code Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests are comprehensive and pass
- [ ] Documentation is updated
- [ ] No breaking changes (unless documented)
- [ ] Performance impact considered
- [ ] Security implications reviewed

## Code Style and Standards

### Python Style Guide

- **Line Length**: Maximum 88 characters (Black default)
- **Imports**: Use `isort` for import sorting
- **Type Hints**: Use type hints for all function signatures
- **Docstrings**: Use Google-style docstrings

### Example Code Style

```python
from typing import Any, Dict, List, Optional
from data_store.nosql_store.abstract import NoSQLStore

class MyAdapter(NoSQLStore):
    """MyAdapter implementation for NoSQL store.
    
    This adapter provides implementation for the MyBackend NoSQL database.
    It supports all basic CRUD operations and connection management.
    
    Args:
        config: Configuration dictionary for the adapter
        **kwargs: Additional keyword arguments
    
    Attributes:
        config (Dict[str, Any]): Configuration dictionary
        _client: Database client instance
    """
    
    def __init__(self, config: Dict[str, Any], **kwargs: Any) -> None:
        """Initialize the MyAdapter.
        
        Args:
            config: Configuration dictionary
            **kwargs: Additional keyword arguments
        """
        super().__init__(config, **kwargs)
        self._client: Optional[Any] = None
    
    def _connect(self, *args: Any, **kwargs: Any) -> Any:
        """Establish connection to MyBackend.
        
        Returns:
            Database client instance
            
        Raises:
            ConnectionError: If connection fails
        """
        try:
            self._client = self._create_connection()
            return self._client
        except Exception as e:
            raise ConnectionError(f"Failed to connect to MyBackend: {e}") from e
    
    def _insert(self, collection: str, data: Dict[str, Any], *args: Any, **kwargs: Any) -> str:
        """Insert document into collection.
        
        Args:
            collection: Collection name
            data: Document data to insert
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
            
        Returns:
            Inserted document ID
            
        Raises:
            ValueError: If data is invalid
            RuntimeError: If insert operation fails
        """
        if not data:
            raise ValueError("Data cannot be empty")
        
        try:
            return self._client.insert(collection, data)
        except Exception as e:
            raise RuntimeError(f"Insert operation failed: {e}") from e
```

### Testing Standards

- **Test Coverage**: Maintain minimum 80% test coverage
- **Test Naming**: Use descriptive test names
- **Test Organization**: Organize tests by module and feature
- **Mocking**: Use mocking for external dependencies

## Release Process

### Version Management

- **Semantic Versioning**: Follow semantic versioning (MAJOR.MINOR.PATCH)
- **Changelog**: Update CHANGELOG.md for each release
- **Version Tags**: Use Git tags for releases

### Release Checklist

1. **Update Version**: Update version in `pyproject.toml`
2. **Update Changelog**: Add release notes to `CHANGELOG.md`
3. **Run Tests**: Ensure all tests pass
4. **Build Documentation**: Build and verify documentation
5. **Create Release Tag**: Create Git tag for release
6. **Publish Package**: Publish to PyPI
7. **Create Release**: Create GitHub release

### Documentation Updates

For each release:

- Update API documentation for new features
- Update user guides with new functionality
- Update installation instructions if needed
- Update version compatibility information

## Next Steps

- **User Guides**: Learn how to use the library with practical examples
- **Best Practices**: Guidelines for production use
- **API Reference**: Detailed API documentation

For getting started information, see the {doc}`../index` guide.

```{toctree}
:maxdepth: 1
:caption: Development

best_practices
nosql_store
object_store