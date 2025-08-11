# Configuration Classes Documentation

This document provides comprehensive documentation for the configuration classes in the data_store project, detailing the Pydantic models, validation rules, connection configuration, and best practices for managing storage configurations.

## Overview

The data_store project uses Pydantic models for configuration management, providing:

- **Type Safety**: Strong typing ensures configuration values are valid
- **Validation**: Automatic validation of configuration parameters
- **Environment Variables**: Support for environment variable configuration
- **Default Values**: Sensible defaults for common parameters
- **URI Building**: Automatic connection URI generation from components

## NoSQL Store Configuration

### Framework Enum

The `Framework` enum defines supported NoSQL database frameworks:

```python
from enum import enum

class Framework(enum.StrEnum):
    MONGODB = "mongodb"
    COUCHDB = "couchdb"
    DYNAMODB = "dynamodb"
```

#### Supported Frameworks

- **MONGODB**: MongoDB database
- **COUCHDB**: Apache CouchDB database
- **DYNAMODB**: Amazon DynamoDB database

### NoSQLConnection Configuration

The `NoSQLConnection` class defines connection parameters for NoSQL databases.

#### Class Definition

```python
import pydantic as pdt
from typing import Optional

class NoSQLConnection(pdt.BaseModel):
    uri: str | None = pdt.Field(
        default=None,
        description="Complete connection URI. If provided, individual connection components will be ignored.",
    )
    host: str | None = pdt.Field(
        default=None,
        description="Database host address. Required if URI is not provided.",
    )
    port: int | None = pdt.Field(
        default=None,
        description="Database port number. Uses default port if not specified.",
    )
    username: str | None = pdt.Field(
        default=None, description="Username for database authentication."
    )
    password: str | None = pdt.Field(
        default=None, description="Password for database authentication."
    )
    database: str | None = pdt.Field(
        default=None, description="Default database name to connect to."
    )
    auth_source: str | None = pdt.Field(
        default=None, description="Authentication database name (MongoDB specific)."
    )
    ssl: bool | None = pdt.Field(
        default=False, description="Enable SSL/TLS connection encryption."
    )
    connection_timeout: int = pdt.Field(
        default=30,
        description="Connection timeout in seconds. Default is 30 seconds.",
    )
```

#### Field Descriptions

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `uri` | `str \| None` | No | `None` | Complete connection URI |
| `host` | `str \| None` | No | `None` | Database host address |
| `port` | `int \| None` | No | `None` | Database port number |
| `username` | `str \| None` | No | `None` | Username for authentication |
| `password` | `str \| None` | No | `None` | Password for authentication |
| `database` | `str \| None` | No | `None` | Default database name |
| `auth_source` | `str \| None` | No | `None` | Authentication database name |
| `ssl` | `bool \| None` | No | `False` | Enable SSL/TLS encryption |
| `connection_timeout` | `int` | No | `30` | Connection timeout in seconds |

#### Validation Rules

The `NoSQLConnection` class includes validation rules:

```python
@pdt.model_validator(mode="after")
def validate_connection(self):
    """Validate that either URI is provided or host/port combination"""
    if not self.uri and not self.host:
        raise ValueError("Either 'uri' or 'host' must be provided")
    return self
```

#### Computed Properties

The class provides a computed property for automatic URI building:

```python
@pdt.computed_field
@property
def connection_uri(self) -> str:
    """Build URI from components if uri is not provided"""
    if self.uri:
        return self.uri

    if not self.host:
        raise ValueError("Host is required to build URI")

    # Build URI from components
    scheme = "mongodb+srv" if self.ssl else "mongodb"

    # Handle authentication
    auth_part = ""
    if self.username:
        if self.password:
            auth_part = f"{self.username}:{self.password}@"
        else:
            auth_part = f"{self.username}@"

    # Handle port
    port_part = f":{self.port}" if self.port else ""

    # Build base URI
    uri = f"{scheme}://{auth_part}{self.host}{port_part}"

    # Add database if provided
    if self.database:
        uri += f"/{self.database}"

    # Add auth source as query parameter if provided
    query_params = []
    if self.auth_source:
        query_params.append(f"authSource={self.auth_source}")

    if query_params:
        uri += "?" + "&".join(query_params)

    return uri
```

#### URI Building Examples

```python
# MongoDB URI with components
connection = NoSQLConnection(
    host="localhost",
    port=27017,
    username="admin",
    password="password",
    database="mydb",
    ssl=False
)
print(connection.connection_uri)
# Output: mongodb://admin:password@localhost:27017/mydb

# MongoDB URI with SSL
connection = NoSQLConnection(
    host="cluster.mongodb.net",
    username="user",
    password="pass",
    database="prod",
    ssl=True
)
print(connection.connection_uri)
# Output: mongodb+srv://user:pass@cluster.mongodb.net/prod

# Using complete URI
connection = NoSQLConnection(
    uri="mongodb://user:pass@localhost:27017/mydb?authSource=admin"
)
print(connection.connection_uri)
# Output: mongodb://user:pass@localhost:27017/mydb?authSource=admin
```

### NoSQLConfiguration

The `NoSQLConfiguration` class is the main configuration class for NoSQL stores.

#### Class Definition

```python
import pydantic_settings as pdts

class NoSQLConfiguration(pdts.BaseSettings):
    framework: str | Framework = pdt.Field(
        default=Framework.MONGODB,
        description="NoSQL database framework to use (mongodb, couchdb, dynamodb).",
    )
    connection: NoSQLConnection = pdt.Field(
        description="Database connection configuration settings."
    )

    model_config = pdts.SettingsConfigDict(extra="allow", use_enum_values=True)
```

#### Usage Examples

```python
# Basic configuration
config = NoSQLConfiguration(
    framework=Framework.MONGODB,
    connection=NoSQLConnection(
        host="localhost",
        port=27017,
        database="testdb"
    )
)

config = NoSQLConfiguration()  # Loads from environment
```

## Object Store Configuration

### Framework Enum

The `Framework` enum defines supported object storage frameworks:

```python
from enum import enum

class Framework(enum.Enum):
    MINIO = "minio"
    BOTO3 = "boto3"
```

#### Supported Frameworks

- **MINIO**: MinIO object storage server
- **BOTO3**: AWS S3 (framework support in development)

### ObjectStoreConnectionConfiguration

The `ObjectStoreConnectionConfiguration` class defines connection parameters for object storage.

#### Class Definition

```python
import pydantic
from typing import Optional

class ObjectStoreConnectionConfiguration(pydantic.BaseModel):
    endpoint: str
    access_key: str
    secret_key: str
    secure: Optional[bool] = False
```

#### Field Descriptions

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `endpoint` | `str` | Yes | - | Storage endpoint URL |
| `access_key` | `str` | Yes | - | Access key for authentication |
| `secret_key` | `str` | Yes | - | Secret key for authentication |
| `secure` | `bool \| None` | No | `False` | Use HTTPS connection |

#### Usage Examples

```python
# MinIO configuration
connection = ObjectStoreConnectionConfiguration(
    endpoint="localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

# AWS S3 configuration (when boto3 is fully supported)
connection = ObjectStoreConnectionConfiguration(
    endpoint="s3.amazonaws.com",
    access_key="your-access-key",
    secret_key="your-secret-key",
    secure=True
)
```

### ObjectStoreConfiguration

The `ObjectStoreConfiguration` class is the main configuration class for object stores.

#### Class Definition

```python
class ObjectStoreConfiguration(pydantic.BaseModel):
    framework: Optional[str | Framework] = pydantic.Field(default=Framework.MINIO)
    root_bucket: str
    connection: ObjectStoreConnectionConfiguration
```

#### Field Descriptions

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `framework` | `str \| Framework \| None` | No | `Framework.MINIO` | Storage framework to use |
| `root_bucket` | `str` | Yes | - | Default bucket name |
| `connection` | `ObjectStoreConnectionConfiguration` | Yes | - | Connection configuration |

#### Usage Examples

```python
# Basic MinIO configuration
config = ObjectStoreConfiguration(
    framework=Framework.MINIO,
    root_bucket="my-bucket",
    connection=ObjectStoreConnectionConfiguration(
        endpoint="localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )
)

# Using string framework
config = ObjectStoreConfiguration(
    framework="minio",
    root_bucket="data-bucket",
    connection=ObjectStoreConnectionConfiguration(
        endpoint="minio.example.com:9000",
        access_key="your-access-key",
        secret_key="your-secret-key",
        secure=True
    )
)
```

## Configuration Validation

### Automatic Validation

Pydantic models automatically validate configuration values:

```python
from pydantic import ValidationError

try:
    # Valid configuration
    config = NoSQLConfiguration(
        framework="mongodb",
        connection=NoSQLConnection(host="localhost")
    )
    print("Configuration is valid")
except ValidationError as e:
    print(f"Configuration validation failed: {e}")

try:
    # Invalid configuration - missing host when no URI provided
    config = NoSQLConfiguration(
        framework="mongodb",
        connection=NoSQLConnection()
    )
except ValidationError as e:
    print(f"Expected validation error: {e}")
```

### Custom Validation

Custom validation rules can be added to configuration classes:

```python
class CustomNoSQLConnection(NoSQLConnection):
    @pdt.model_validator(mode="after")
    def validate_custom_rules(self):
        # Custom validation logic
        if self.host == "localhost" and self.port == 27017:
            if not self.username:
                raise ValueError("Username is required for localhost connections")
        return self
```

## Connection Configuration Examples

### MongoDB Connection Examples

```python
# Basic MongoDB connection
basic_config = NoSQLConfiguration(
    framework=Framework.MONGODB,
    connection=NoSQLConnection(
        host="localhost",
        port=27017,
        database="myapp"
    )
)

# MongoDB with authentication
auth_config = NoSQLConfiguration(
    framework=Framework.MONGODB,
    connection=NoSQLConnection(
        host="cluster.mongodb.net",
        username="admin",
        password="securepassword",
        database="production",
        auth_source="admin"
    )
)

# MongoDB with SSL
ssl_config = NoSQLConfiguration(
    framework=Framework.MONGODB,
    connection=NoSQLConnection(
        host="secure-cluster.mongodb.net",
        username="user",
        password="password",
        database="secure_db",
        ssl=True,
        connection_timeout=60
    )
)

# Using complete URI
uri_config = NoSQLConfiguration(
    framework=Framework.MONGODB,
    connection=NoSQLConnection(
        uri="mongodb://user:password@cluster.mongodb.net/mydb?authSource=admin"
    )
)
```

### MinIO Connection Examples

```python
# Basic MinIO connection
minio_config = ObjectStoreConfiguration(
    framework=Framework.MINIO,
    root_bucket="my-data",
    connection=ObjectStoreConnectionConfiguration(
        endpoint="localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )
)

# Secure MinIO connection
secure_minio_config = ObjectStoreConfiguration(
    framework=Framework.MINIO,
    root_bucket="production-data",
    connection=ObjectStoreConnectionConfiguration(
        endpoint="minio.example.com:9000",
        access_key="your-access-key",
        secret_key="your-secret-key",
        secure=True
    )
)

# AWS S3 configuration (when boto3 is supported)
s3_config = ObjectStoreConfiguration(
    framework=Framework.BOTO3,
    root_bucket="my-s3-bucket",
    connection=ObjectStoreConnectionConfiguration(
        endpoint="s3.amazonaws.com",
        access_key="your-aws-access-key",
        secret_key="your-aws-secret-key",
        secure=True
    )
)
```

## Troubleshooting Configuration Issues

### Common Configuration Errors

```python
from pydantic import ValidationError

# Error: Missing required fields
try:
    config = NoSQLConfiguration()
except ValidationError as e:
    print(f"Missing required fields: {e}")

# Error: Invalid framework
try:
    config = NoSQLConfiguration(
        framework="invalid_framework",
        connection=NoSQLConnection(host="localhost")
    )
except ValidationError as e:
    print(f"Invalid framework: {e}")

# Error: Invalid connection parameters
try:
    config = NoSQLConfiguration(
        framework="mongodb",
        connection=NoSQLConnection()  # Missing host and URI
    )
except ValidationError as e:
    print(f"Invalid connection parameters: {e}")
```

### Debug Configuration

```python
import logging
from data_store.nosql_store import NoSQLConfiguration

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

def debug_configuration(config_dict):
    """Debug configuration loading and validation."""
    try:
        config = NoSQLConfiguration(**config_dict)
        print("Configuration loaded successfully:")
        print(f"Framework: {config.framework}")
        print(f"Connection URI: {config.connection.connection_uri}")
        print(f"Database: {config.connection.database}")
        return config
    except ValidationError as e:
        print("Configuration validation errors:")
        for error in e.errors():
            print(f"  {error['loc']}: {error['msg']}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise
```

### Configuration Health Check

```python
from data_store.nosql_store import NoSQLConfiguration
from data_store.object_store import ObjectStoreConfiguration

def check_configuration_health(config):
    """Perform health check on configuration."""
    issues = []
    
    if isinstance(config, NoSQLConfiguration):
        # Check NoSQL configuration
        if not config.connection.host and not config.connection.uri:
            issues.append("Missing host or URI in connection configuration")
        
        if config.connection.connection_timeout <= 0:
            issues.append("Connection timeout must be positive")
        
        if config.connection.ssl and not config.connection.uri:
            issues.append("SSL configuration requires complete URI or explicit host/port")
    
    elif isinstance(config, ObjectStoreConfiguration):
        # Check object store configuration
        if not config.connection.endpoint:
            issues.append("Missing endpoint in connection configuration")
        
        if not config.connection.access_key or not config.connection.secret_key:
            issues.append("Missing access key or secret key in connection configuration")
        
        if not config.root_bucket:
            issues.append("Missing root bucket configuration")
    
    return issues

# Example usage
nosql_config = NoSQLConfiguration(
    framework="mongodb",
    connection=NoSQLConnection(host="localhost")
)

object_config = ObjectStoreConfiguration(
    framework="minio",
    root_bucket="test-bucket",
    connection=ObjectStoreConnectionConfiguration(
        endpoint="localhost:9000",
        access_key="test",
        secret_key="test"
    )
)

print("NoSQL config issues:", check_configuration_health(nosql_config))
print("Object store config issues:", check_configuration_health(object_config))
```

## Conclusion

The configuration classes in the data_store project provide a robust, type-safe way to manage storage configurations. By leveraging Pydantic models, the system ensures that all configuration parameters are validated and properly typed.

Key features include:

- **Automatic Validation**: Pydantic validates all configuration parameters
- **Environment Variable Support**: Easy configuration through environment variables
- **Flexible Connection Configuration**: Support for both component-based and complete URI configurations
- **Type Safety**: Strong typing prevents configuration errors
- **Extensibility**: Easy to add new configuration parameters and validation rules

For more information about using the configured stores, see:
- {doc}`../user_guides/nosql_store` - NoSQL store interface and usage
- {doc}`../user_guides/object_store` - Object store interface and usage
- {doc}`abstract_base_classes` - Abstract interfaces and design patterns
- {doc}`models` - Data models and structures
- {doc}`adapters` - Adapter implementations and extension points