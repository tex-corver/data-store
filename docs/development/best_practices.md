# Best Practices Guide

This guide provides best practices for using the tex-corver-data-store library in production environments.

## Configuration Management

### Environment-Based Configuration

Use environment-specific configurations for different deployment environments:

```python
# config/environments.py
import os
from data_store.nosql_store.configurations import NoSQLConfiguration
from data_store.object_store.configurations import ObjectStoreConfiguration

def get_nosql_config():
    """Get NoSQL configuration based on environment."""
    env = os.getenv("ENVIRONMENT", "development")
    
    if env == "production":
        return NoSQLConfiguration(
            framework="mongodb",
            connection={
                "uri": os.getenv("MONGODB_URI"),
                "ssl": True,
                "connection_timeout": 30
            }
        )
    else:
        return NoSQLConfiguration(
            framework="mongodb",
            connection={
                "host": "localhost",
                "port": 27017,
                "database": "dev_db",
                "ssl": False
            }
        )

def get_object_store_config():
    """Get object store configuration based on environment."""
    env = os.getenv("ENVIRONMENT", "development")
    
    if env == "production":
        return ObjectStoreConfiguration(
            framework="minio",
            root_bucket=os.getenv("PRODUCTION_BUCKET"),
            connection={
                "endpoint": os.getenv("OBJECT_STORE_ENDPOINT"),
                "access_key": os.getenv("OBJECT_STORE_ACCESS_KEY"),
                "secret_key": os.getenv("OBJECT_STORE_SECRET_KEY"),
                "secure": True
            }
        )
    else:
        return ObjectStoreConfiguration(
            framework="minio",
            root_bucket="dev-bucket",
            connection={
                "endpoint": "localhost:9000",
                "access_key": "minioadmin",
                "secret_key": "minioadmin",
                "secure": False
            }
        )
```

### Configuration Validation

Always validate configuration before using it:

```python
from data_store.nosql_store.configurations import NoSQLConfiguration
from pydantic import ValidationError

def validate_nosql_config(config_dict):
    """Validate NoSQL configuration."""
    try:
        config = NoSQLConfiguration(**config_dict)
        return config
    except ValidationError as e:
        print(f"Configuration validation failed: {e}")
        raise

# Usage
config = validate_nosql_config({
    "framework": "mongodb",
    "connection": {
        "host": "localhost",
        "port": 27017,
        "database": "myapp"
    }
})
```

### Secure Configuration Storage

Never store sensitive information in configuration files:

```python
# Use environment variables for sensitive data
import os
from data_store import NoSQLStore, ObjectStore

# Good: Use environment variables
config = {
    "framework": "mongodb",
    "connection": {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "27017")),
        "username": os.getenv("DB_USERNAME"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME", "myapp")
    }
}

# Bad: Hardcoded credentials
config = {
    "framework": "mongodb",
    "connection": {
        "host": "localhost",
        "port": 27017,
        "username": "admin",  # Never hardcode credentials
        "password": "password",  # Never hardcode credentials
        "database": "myapp"
    }
}
```

## Connection Management

### Connection Pooling

Use connection pooling for better performance:

```python
# Configure connection pooling
config = {
    "framework": "mongodb",
    "connection": {
        "host": "localhost",
        "port": 27017,
        "database": "myapp",
        # specific settings for mongoDB, by default is not appeared in configuration model.
        "connection_pool": {
            "max_pool_size": 100,
            "min_pool_size": 0,
            "max_idle_time_ms": 30000,
            "wait_queue_timeout_ms": 1000
        }
    }
}

store = NoSQLStore(config)
```

### Context Managers

Always use context managers for connection management:

```python
# Good: Use context managers
with store.connect() as connection:
    # Multiple operations
    store.insert("users", {"name": "Alice"})
    store.insert("users", {"name": "Bob"})
    users = store.find("users", {"name": {"$in": ["Alice", "Bob"]}})

# Bad: No connection management
store.insert("users", {"name": "Charlie"})  # May create multiple connections
store.insert("users", {"name": "David"})    # Inefficient
```

### Connection Retry Logic

Implement retry logic for transient failures:

```python
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=1.0):
    """Decorator for retrying operations on failure."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(delay * (2 ** attempt))  # Exponential backoff
                    else:
                        raise
        return wrapper
    return decorator

# Usage
@retry_on_failure(max_retries=3, delay=1.0)
def safe_database_operation(store, operation, *args, **kwargs):
    """Perform database operation with retry logic."""
    with store.connect() as connection:
        return operation(*args, **kwargs)
```

## Error Handling

### Comprehensive Error Handling

Implement comprehensive error handling:

```python
import logging
from data_store import NoSQLStore, ObjectStore

logger = logging.getLogger(__name__)

def handle_database_errors(func):
    """Decorator to handle database errors gracefully."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            logger.warning(f"Validation error: {e}")
            raise
        except RuntimeError as e:
            logger.error(f"Database error: {e}")
            # Implement retry logic or fallback
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
    return wrapper

# Usage
@handle_database_errors
def insert_user(store, user_data):
    """Insert user with error handling."""
    return store.insert("users", user_data)
```

### Custom Exceptions

Create custom exceptions for better error handling:

```python
class DataStoreError(Exception):
    """Base exception for data store operations."""
    pass

class ConnectionError(DataStoreError):
    """Exception raised when connection fails."""
    pass

class ValidationError(DataStoreError):
    """Exception raised when data validation fails."""
    pass

class OperationError(DataStoreError):
    """Exception raised when operation fails."""
    pass

# Usage
try:
    store.insert("users", invalid_data)
except ValueError as e:
    raise ValidationError(f"Invalid user data: {e}")
except RuntimeError as e:
    raise OperationError(f"Database operation failed: {e}")
```

### Error Recovery

Implement error recovery strategies:

```python
def recoverable_database_operation(store, operation, *args, **kwargs):
    """Perform database operation with error recovery."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return operation(*args, **kwargs)
        except (ConnectionError, OperationError) as e:
            if attempt == max_retries - 1:
                raise
            # Wait before retry
            time.sleep(2 ** attempt)
            # Try to reconnect
            store.reconnect()
        except Exception as e:
            raise OperationError(f"Unexpected error: {e}")
```

## Performance Optimization

### Batch Operations

Use batch operations for large datasets:

```python
def batch_insert_users(store, users, batch_size=1000):
    """Insert users in batches to improve performance."""
    for i in range(0, len(users), batch_size):
        batch = users[i:i + batch_size]
        result = store.bulk_insert("users", batch)
        print(f"Inserted batch {i//batch_size + 1}: {result} documents")

# Usage
users = [{"name": f"User{i}", "email": f"user{i}@example.com"} for i in range(5000)]
batch_insert_users(store, users)
```

### Caching

Implement caching for frequently accessed data:

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=128)
def get_user_by_email(store, email):
    """Cache user lookups to reduce database queries."""
    users = store.find("users", {"email": email})
    return users[0] if users else None

def get_user_with_cache_key(store, email):
    """Get user with cache key based on email hash."""
    cache_key = hashlib.md5(email.encode()).hexdigest()
    return get_user_by_email(store, email)
```

### Query Optimization

Optimize database queries:

```python
# Good: Use appropriate indexes and projections
users = store.find(
    "users",
    {"status": "active", "age": {"$gte": 18}},
    projections=["name", "email"]  # Only needed fields
)

# Bad: Fetch all fields
users = store.find("users", {"status": "active"})
```

### Lazy Loading

Use lazy loading for large datasets:

```python
def get_large_dataset(store, collection, filters=None):
    """Get large dataset with lazy loading."""
    cursor = store.find_lazy(collection, filters)
    for document in cursor:
        yield document  # Process documents one at a time

# Usage
for user in get_large_dataset(store, "users", {"status": "active"}):
    process_user(user)
```

## Security Considerations

### Authentication and Authorization

Implement proper authentication and authorization:

```python
from data_store import NoSQLStore

# Use secure authentication
config = {
    "framework": "mongodb",
    "host": "localhost",
    "port": 27017,
    "database": "myapp",
    "username": "secure_user",
    "password": "secure_password",
    "auth_source": "admin",  # Authentication database
    "ssl": True
}

store = NoSQLStore(config)
```

### Input Validation

Validate all input data:

```python
def validate_user_data(user_data):
    """Validate user data before insertion."""
    required_fields = ["name", "email"]
    
    for field in required_fields:
        if field not in user_data:
            raise ValueError(f"Missing required field: {field}")
    
    if not isinstance(user_data["name"], str) or len(user_data["name"]) < 2:
        raise ValueError("Name must be at least 2 characters")
    
    if "@" not in user_data["email"]:
        raise ValueError("Invalid email format")
    
    return True

# Usage
user_data = {"name": "Alice", "email": "alice@example.com"}
validate_user_data(user_data)
store.insert("users", user_data)
```

### Data Encryption

Encrypt sensitive data:

```python
from cryptography.fernet import Fernet

# Generate encryption key
key = Fernet.generate_key()
cipher = Fernet(key)

def encrypt_sensitive_data(data):
    """Encrypt sensitive data before storage."""
    return cipher.encrypt(data.encode()).decode()

def decrypt_sensitive_data(encrypted_data):
    """Decrypt sensitive data after retrieval."""
    return cipher.decrypt(encrypted_data.encode()).decode()

# Usage
user_data = {
    "name": "Alice",
    "email": "alice@example.com",
    "ssn": encrypt_sensitive_data("123-45-6789")  # Encrypt sensitive data
}
```

### Audit Logging

Implement audit logging for security:

```python
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def log_user_action(user_id, action, details):
    """Log user actions for audit purposes."""
    log_entry = {
        "user_id": user_id,
        "action": action,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    logger.info(f"User action: {log_entry}")

# Usage
log_user_action("user123", "login", {"ip": "192.168.1.1", "user_agent": "Chrome"})
```

## Testing Strategies

### Unit Testing

Write comprehensive unit tests:

```python
import pytest
from unittest.mock import Mock, patch
from data_store import NoSQLStore

def test_insert_user():
    """Test user insertion with mocked database."""
    with patch('data_store.nosql_store.nosql_store.NoSQLStoreComponentFactory') as mock_factory:
        mock_client = Mock()
        mock_client.insert.return_value = "user123"
        mock_factory.return_value.create_client.return_value = mock_client
        
        store = NoSQLStore({})
        result = store.insert("users", {"name": "Alice"})
        
        assert result == "user123"
        mock_client.insert.assert_called_once_with("users", {"name": "Alice"})
```

### Integration Testing

Test with actual databases:

```python
def test_mongodb_integration():
    """Test with actual MongoDB database."""
    config = {
        "framework": "mongodb",
        "host": "localhost",
        "port": 27017,
        "database": "test_db"
    }
    
    store = NoSQLStore(config)
    
    try:
        with store.connect() as connection:
            # Test operations
            doc_id = store.insert("test_collection", {"test": "data"})
            assert doc_id is not None
            
            doc = store.find("test_collection", {"_id": doc_id})
            assert len(doc) == 1
            assert doc[0]["test"] == "data"
            
            # Cleanup
            store.delete("test_collection", {"_id": doc_id})
            
    except Exception as e:
        print(f"Integration test failed: {e}")
        raise
```

### Property-Based Testing

Use property-based testing for edge cases:

```python
from hypothesis import given, strategies as st

@given(st.lists(st.dictionaries(keys=st.text(), values=st.text()), min_size=1))
def test_bulk_insert_bulk_find(users):
    """Test that bulk insert and bulk find are consistent."""
    # Insert users
    result = store.bulk_insert("users", users)
    assert result == str(len(users))
    
    # Find all users
    found_users = store.find("users")
    assert len(found_users) == len(users)
    
    # Cleanup
    store.bulk_delete("users", {})
```

### Load Testing

Test performance under load:

```python
import time
import threading
from concurrent.futures import ThreadPoolExecutor

def concurrent_operations(store, num_threads=10, operations_per_thread=100):
    """Test concurrent operations."""
    def worker(thread_id):
        for i in range(operations_per_thread):
            store.insert("test_collection", {
                "thread_id": thread_id,
                "operation_id": i,
                "data": f"Thread {thread_id}, Operation {i}"
            })
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        executor.map(worker, range(num_threads))
    
    end_time = time.time()
    print(f"Completed {num_threads * operations_per_thread} operations in {end_time - start_time:.2f} seconds")
```

## Monitoring and Logging

### Structured Logging

Use structured logging for better monitoring:

```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
    
    def log_operation(self, operation, details, level="INFO"):
        """Log operation with structured data."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "details": details
        }
        
        log_message = json.dumps(log_entry)
        
        if level == "INFO":
            self.logger.info(log_message)
        elif level == "ERROR":
            self.logger.error(log_message)
        elif level == "WARNING":
            self.logger.warning(log_message)

# Usage
logger = StructuredLogger("data_store")
logger.log_operation("insert", {"collection": "users", "document_id": "123"})
```

### Performance Monitoring

Monitor database performance:

```python
import time
from functools import wraps

def monitor_performance(func):
    """Monitor function performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        logger.info(f"Function {func.__name__} executed in {execution_time:.3f} seconds")
        
        return result
    return wrapper

# Usage
@monitor_performance
def insert_user(store, user_data):
    """Insert user with performance monitoring."""
    return store.insert("users", user_data)
```

### Health Checks

Implement health checks for database connectivity:

```python
def check_database_health(store):
    """Check database health."""
    try:
        with store.connect() as connection:
            # Simple health check
            store.find("health_check", {"test": "connection"}, limit=1)
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e), "timestamp": datetime.now().isoformat()}

# Usage
health = check_database_health(store)
print(f"Database health: {health}")
```

## Deployment Considerations

### Configuration Management

Use proper configuration management for different environments:

```python
# config/deployment.py
import os
from data_store.nosql_store.configurations import NoSQLConfiguration
from data_store.object_store.configurations import ObjectStoreConfiguration

class DeploymentConfig:
    def __init__(self, environment="development"):
        self.environment = environment
        self.nosql_config = self._get_nosql_config()
        self.object_store_config = self._get_object_store_config()
    
    def _get_nosql_config(self):
        """Get NoSQL configuration for the environment."""
        if self.environment == "production":
            return NoSQLConfiguration(
                framework="mongodb",
                connection={
                    "uri": os.getenv("MONGODB_URI"),
                    "ssl": True,
                    "connection_timeout": 30
                }
            )
        else:
            return NoSQLConfiguration(
                framework="mongodb",
                connection={
                    "host": "localhost",
                    "port": 27017,
                    "database": "dev_db",
                    "ssl": False
                }
            )
    
    def _get_object_store_config(self):
        """Get object store configuration for the environment."""
        if self.environment == "production":
            return ObjectStoreConfiguration(
                framework="minio",
                root_bucket=os.getenv("PRODUCTION_BUCKET"),
                connection={
                    "endpoint": os.getenv("OBJECT_STORE_ENDPOINT"),
                    "access_key": os.getenv("OBJECT_STORE_ACCESS_KEY"),
                    "secret_key": os.getenv("OBJECT_STORE_SECRET_KEY"),
                    "secure": True
                }
            )
        else:
            return ObjectStoreConfiguration(
                framework="minio",
                root_bucket="dev-bucket",
                connection={
                    "endpoint": "localhost:9000",
                    "access_key": "minioadmin",
                    "secret_key": "minioadmin",
                    "secure": False
                }
            )

# Usage
config = DeploymentConfig(environment=os.getenv("ENVIRONMENT", "development"))
```

### Containerization

Use Docker for consistent deployment:

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY docs/ ./docs/

ENV PYTHONPATH=/app/src

CMD ["python", "-m", "pytest", "tests/"]
```

### Kubernetes Deployment

Deploy with Kubernetes for scalability:

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: data-store-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: data-store-app
  template:
    metadata:
      labels:
        app: data-store-app
    spec:
      containers:
      - name: data-store-app
        image: data-store-app:latest
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: MONGODB_URI
          valueFrom:
            secretKeyRef:
              name: mongodb-secret
              key: uri
        - name: OBJECT_STORE_ENDPOINT
          valueFrom:
            secretKeyRef:
              name: object-store-secret
              key: endpoint
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### CI/CD Pipeline

Implement CI/CD for automated testing and deployment:

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10]
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=src
    
    - name: Build documentation
      run: |
        cd docs
        make html
    
    - name: Deploy to production
      if: github.ref == 'refs/heads/main'
      run: |
        # Deployment script
        ./deploy.sh
```

## Conclusion

Following these best practices will help you build robust, secure, and performant applications using the tex-corver-data-store library. Remember to:

1. **Validate all input data** before storage
2. **Use proper error handling** and logging
3. **Implement security measures** like authentication and encryption
4. **Monitor performance** and health metrics
5. **Test thoroughly** at unit, integration, and load levels
6. **Use proper configuration management** for different environments

For more detailed information about specific features, see the other guides in this documentation.