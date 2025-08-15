# Models Documentation

This document provides comprehensive documentation for the data models used in the data_store project, detailing the data structures, serialization patterns, and usage examples for both NoSQL and Object Store models.

## Overview

The data_store project uses several data models to represent storage entities and their metadata. These models provide:

- **Type Safety**: Strong typing for all data structures
- **Immutability**: Frozen dataclasses prevent accidental modification
- **Serialization Support**: Easy conversion to and from JSON
- **Metadata Handling**: Consistent metadata management across storage backends

## Object Store Models

### Bucket Model

The `Bucket` model represents a storage bucket in object storage systems.

#### Class Definition

```python
import dataclasses
from datetime import datetime

@dataclasses.dataclass(frozen=True)
class Bucket:
    """Represents a storage bucket in object storage systems."""
    
    name: str
    created_time: datetime
```

#### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | The name of the bucket |
| `created_time` | `datetime` | When the bucket was created |

#### Usage Examples

```python
from data_store.object_store.models import Bucket
from datetime import datetime

# Create a bucket instance
bucket = Bucket(
    name="my-data-bucket",
    created_time=datetime(2024, 1, 15, 10, 30, 0)
)

# Access fields
print(f"Bucket name: {bucket.name}")
print(f"Created: {bucket.created_time}")

# Note: Since the class is frozen, modification is not allowed
# bucket.name = "new-name"  # This would raise FrozenInstanceError
```

### ObjectMetadata Model

The `ObjectMetadata` model represents metadata about an object in storage.

#### Class Definition

```python
@dataclasses.dataclass(frozen=True)
class ObjectMetadata:
    """Represents metadata about an object in object storage."""
    
    key: str
    updated_time: datetime
    size: int
```

#### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `key` | `str` | The object key (path) in the bucket |
| `updated_time` | `datetime` | When the object was last modified |
| `size` | `int` | Size of the object in bytes |

#### Usage Examples

```python
from data_store.object_store.models import ObjectMetadata
from datetime import datetime

# Create object metadata
metadata = ObjectMetadata(
    key="documents/report.pdf",
    updated_time=datetime(2024, 1, 20, 14, 45, 30),
    size=1024576  # 1MB
)

# Access fields
print(f"Object key: {metadata.key}")
print(f"Size: {metadata.size} bytes")
print(f"Last modified: {metadata.updated_time}")

# Check file type
file_extension = metadata.key.split('.')[-1] if '.' in metadata.key else ''
print(f"File type: {file_extension}")

# Check if file is large
if metadata.size > 10 * 1024 * 1024:  # 10MB
    print("Large file detected")
```

### Object Model

The `Object` model represents the actual content of an object in storage.

#### Class Definition

```python
from typing import IO

@dataclasses.dataclass(frozen=True)
class Object:
    """Represents an object with content and metadata."""
    
    body: IO[bytes]
    updated_time: datetime
```

#### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `body` | `IO[bytes]` | File content as a binary stream |
| `updated_time` | `datetime` | When the object was last modified |

#### Usage Examples

```python
from data_store.object_store.models import Object
from datetime import datetime
import io

# Create an object with content
content = b"Hello, World! This is a test file content."
object_body = io.BytesIO(content)

obj = Object(
    body=object_body,
    updated_time=datetime(2024, 1, 20, 14, 45, 30)
)

# Access content
obj.body.seek(0)  # Reset stream position
content = obj.body.read()
print(f"Content: {content.decode()}")

# Get content size
obj.body.seek(0, 2)  # Seek to end
size = obj.body.tell()
print(f"Size: {size} bytes")

# Reset stream for further reading
obj.body.seek(0)
```

## NoSQL Store Models

### Current State

Currently, the NoSQL store models module (`src/data_store/nosql_store/models.py`) is empty. This section outlines the expected models and their usage patterns based on the abstract interfaces.

### Expected Document Model

Based on the NoSQL store interface, the following document model is expected:

```python
import dataclasses
from datetime import datetime
from typing import Any, Dict, Optional

@dataclasses.dataclass
class Document:
    """Represents a document in NoSQL storage."""
    
    _id: Optional[str] = None
    data: Dict[str, Any] = dataclasses.field(default_factory=dict)
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary for storage."""
        return {
            "_id": self._id,
            **self.data,
            "created_time": self.created_time,
            "updated_time": self.updated_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Document":
        """Create document from dictionary."""
        return cls(
            _id=data.get("_id"),
            data={k: v for k, v in data.items() if k not in ["_id", "created_time", "updated_time"]},
            created_time=data.get("created_time"),
            updated_time=data.get("updated_time")
        )
```

### Expected Query Model

```python
@dataclasses.dataclass
class Query:
    """Represents a query for NoSQL operations."""
    
    collection: str
    filters: Dict[str, Any] = dataclasses.field(default_factory=dict)
    projections: Optional[list[str]] = None
    skip: int = 0
    limit: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert query to dictionary."""
        return {
            "collection": self.collection,
            "filters": self.filters,
            "projections": self.projections,
            "skip": self.skip,
            "limit": self.limit
        }
```

## Model Usage Patterns

### Object Store Usage Patterns

#### File Operations

```python
from data_store.object_store.models import Bucket, ObjectMetadata, Object
from datetime import datetime
import io

class FileOperations:
    """Demonstrates common file operation patterns."""
    
    def __init__(self, store):
        self.store = store
    
    def upload_file_with_metadata(self, file_path: str, key: str, bucket: str = None):
        """Upload file and return metadata."""
        # Upload file
        self.store.upload_file(file_path, key, bucket)
        
        # Get metadata
        metadata = list(self.store.list_files(prefix=key, bucket=bucket))[0]
        return metadata
    
    def download_file_with_info(self, key: str, bucket: str = None):
        """Download file and return object with info."""
        # Get file object
        obj = self.store.get_file(key, bucket)
        
        # Create info dictionary
        info = {
            "content": obj.body.read(),
            "size": len(obj.body.getvalue()),
            "last_modified": obj.updated_time
        }
        
        return info
    
    def list_files_by_type(self, file_extension: str, bucket: str = None):
        """List files by extension."""
        all_files = self.store.list_files(bucket=bucket)
        
        filtered_files = [
            file for file in all_files
            if file.key.endswith(f".{file_extension}")
        ]
        
        return filtered_files
    
    def get_file_size_stats(self, prefix: str = "", bucket: str = None):
        """Get file size statistics."""
        files = self.store.list_files(prefix=prefix, bucket=bucket)
        
        if not files:
            return {"total_files": 0, "total_size": 0, "average_size": 0}
        
        total_size = sum(file.size for file in files)
        average_size = total_size / len(files)
        
        return {
            "total_files": len(files),
            "total_size": total_size,
            "average_size": average_size
        }
```

#### Batch File Operations

```python
from data_store.object_store.models import ObjectMetadata
from typing import List, Dict, Any

class BatchFileOperations:
    """Demonstrates batch file operation patterns."""
    
    def __init__(self, store):
        self.store = store
    
    def batch_upload_files(self, file_mappings: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Upload multiple files and return results."""
        results = []
        
        for mapping in file_mappings:
            try:
                result = self.store.upload_file(
                    file_path=mapping["local_path"],
                    key=mapping["remote_key"],
                    bucket=mapping.get("bucket")
                )
                
                results.append({
                    "success": True,
                    "file": mapping["remote_key"],
                    "result": result
                })
                
            except Exception as e:
                results.append({
                    "success": False,
                    "file": mapping["remote_key"],
                    "error": str(e)
                })
        
        return results
    
    def batch_delete_files(self, file_keys: List[str], bucket: str = None) -> Dict[str, Any]:
        """Delete multiple files and return statistics."""
        results = {
            "total": len(file_keys),
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        for key in file_keys:
            try:
                self.store.delete_file(key, bucket)
                results["successful"] += 1
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "file": key,
                    "error": str(e)
                })
        
        return results
    
    def organize_files_by_date(self, source_prefix: str, bucket: str = None):
        """Organize files by date into folders."""
        from datetime import datetime
        
        # Get all files
        files = self.store.list_files(prefix=source_prefix, bucket=bucket)
        
        organization_plan = {}
        
        for file_meta in files:
            # Extract date from filename or use file modification time
            if "2024" in file_meta.key:
                # Extract date from filename
                date_part = file_meta.key.split("/")[1] if "/" in file_meta.key else "2024-01-01"
            else:
                # Use file modification time
                date_part = file_meta.updated_time.strftime("%Y-%m-%d")
            
            date_folder = f"organized/{date_part}"
            new_key = f"{date_folder}/{file_meta.key}"
            
            organization_plan[file_meta.key] = {
                "new_key": new_key,
                "size": file_meta.size,
                "last_modified": file_meta.updated_time
            }
        
        return organization_plan
```

### NoSQL Store Usage Patterns

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

@dataclass
class User:
    """Example user model for NoSQL storage."""
    
    user_id: str
    username: str
    email: str
    created_at: datetime
    profile: Dict[str, Any]
    preferences: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to document format."""
        return {
            "_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at,
            "profile": self.profile,
            "preferences": self.preferences
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """Create user from document."""
        return cls(
            user_id=data["_id"],
            username=data["username"],
            email=data["email"],
            created_at=data["created_at"],
            profile=data.get("profile", {}),
            preferences=data.get("preferences", {})
        )

class UserOperations:
    """Demonstrates user operation patterns."""
    
    def __init__(self, nosql_store):
        self.store = nosql_store
        self.collection = "users"
    
    def create_user(self, user: User) -> str:
        """Create a new user."""
        return self.store.insert(self.collection, user.to_dict())
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        results = self.store.find(
            self.collection,
            filters={"_id": user_id}
        )
        
        if results:
            return User.from_dict(results[0])
        return None
    
    def update_user_profile(self, user_id: str, profile_updates: Dict[str, Any]) -> bool:
        """Update user profile."""
        result = self.store.update(
            self.collection,
            filters={"_id": user_id},
            update_data={"$set": {"profile": profile_updates}}
        )
        return result > 0
    
    def find_users_by_email_domain(self, domain: str) -> List[User]:
        """Find users by email domain."""
        results = self.store.find(
            self.collection,
            filters={"email": {"$regex": f"@{domain}$"}}
        )
        
        return [User.from_dict(doc) for doc in results]
    
    def bulk_create_users(self, users: List[User]) -> str:
        """Create multiple users."""
        user_docs = [user.to_dict() for user in users]
        return self.store.bulk_insert(self.collection, user_docs)
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """Get user statistics."""
        # Total users
        total_users = len(self.store.find(self.collection))
        
        # Users created in last 30 days
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=30)
        
        recent_users = self.store.find(
            self.collection,
            filters={"created_at": {"$gte": cutoff_date}}
        )
        
        # Users by email domain
        all_users = self.store.find(self.collection)
        domain_counts = {}
        
        for user in all_users:
            email = user.get("email", "")
            domain = email.split("@")[-1] if "@" in email else "unknown"
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        return {
            "total_users": total_users,
            "recent_users": len(recent_users),
            "domain_distribution": domain_counts
        }
```

## Model Serialization and Deserialization

### JSON Serialization

```python
import json
from dataclasses import asdict
from datetime import datetime
from typing import Any

class ModelSerializer:
    """Handles serialization and deserialization of models."""
    
    @staticmethod
    def serialize_datetime(obj: Any) -> Any:
        """Custom JSON serializer for datetime objects."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        return obj
    
    @staticmethod
    def to_json(model: Any) -> str:
        """Convert model to JSON string."""
        def default_converter(o):
            if hasattr(o, '__dataclass_fields__'):
                return asdict(o)
            elif isinstance(o, datetime):
                return o.isoformat()
            else:
                raise TypeError(f"Object of type {type(o)} is not JSON serializable")
        
        return json.dumps(model, default=default_converter, indent=2)
    
    @staticmethod
    def from_json(json_str: str, model_class: type) -> Any:
        """Convert JSON string to model instance."""
        data = json.loads(json_str)
        
        if hasattr(model_class, '__dataclass_fields__'):
            # Handle dataclass
            return model_class(**data)
        else:
            # Handle regular class
            return model_class(data)

# Usage examples
from data_store.object_store.models import Bucket, ObjectMetadata

bucket = Bucket(
    name="test-bucket",
    created_time=datetime(2024, 1, 15, 10, 30, 0)
)

# Serialize to JSON
json_str = ModelSerializer.to_json(bucket)
print("Serialized bucket:", json_str)

# Deserialize from JSON
deserialized_bucket = ModelSerializer.from_json(json_str, Bucket)
print("Deserialized bucket:", deserialized_bucket)
```

### Custom Serialization

```python
from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class CustomDocument:
    """Example document with custom serialization needs."""
    
    id: str
    content: Any
    metadata: Dict[str, Any]
    tags: list[str]
    
    def to_mongo(self) -> Dict[str, Any]:
        """Convert to MongoDB document format."""
        return {
            "_id": self.id,
            "content": self.content,
            "metadata": self.metadata,
            "tags": self.tags,
            "created_at": datetime.now()
        }
    
    @classmethod
    def from_mongo(cls, doc: Dict[str, Any]) -> "CustomDocument":
        """Create from MongoDB document."""
        return cls(
            id=str(doc["_id"]),
            content=doc["content"],
            metadata=doc.get("metadata", {}),
            tags=doc.get("tags", [])
        )
    
    def to_elasticsearch(self) -> Dict[str, Any]:
        """Convert to Elasticsearch document format."""
        return {
            "id": self.id,
            "content_text": str(self.content),
            "metadata": self.metadata,
            "tags": self.tags,
            "indexed_at": datetime.now()
        }
```

## Model Validation

### Pydantic Integration

```python
from pydantic import BaseModel, validator, EmailStr
from datetime import datetime
from typing import List, Optional

class UserProfile(BaseModel):
    """User profile with validation."""
    
    username: str = ...  # Required
    email: EmailStr  # Validated email
    age: Optional[int] = None
    interests: List[str] = []
    
    @validator('age')
    def validate_age(cls, v):
        if v is not None and (v < 0 or v > 150):
            raise ValueError('Age must be between 0 and 150')
        return v
    
    @validator('interests')
    def validate_interests(cls, v):
        if len(v) > 10:
            raise ValueError('Maximum 10 interests allowed')
        return v

class UserDocument:
    """User document with validation."""
    
    def __init__(self, profile: UserProfile):
        self.profile = profile
        self.created_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert to dictionary with validation."""
        return {
            "username": self.profile.username,
            "email": self.profile.email,
            "age": self.profile.age,
            "interests": self.profile.interests,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "UserDocument":
        """Create from dictionary with validation."""
        profile = UserProfile(**data)
        return cls(profile)

# Usage
try:
    profile = UserProfile(
        username="john_doe",
        email="john@example.com",
        age=25,
        interests=["coding", "reading", "gaming"]
    )
    
    user_doc = UserDocument(profile)
    print("Valid user document created")
    
except Exception as e:
    print(f"Validation error: {e}")
```

## Model Performance Considerations

### Memory Management

```python
import gc
from data_store.object_store.models import Object
from typing import Iterator

class MemoryEfficientFileProcessor:
    """Processes large files with memory efficiency."""
    
    def __init__(self, store):
        self.store = store
    
    def process_large_files(self, file_keys: list[str], bucket: str = None) -> Iterator[dict]:
        """Process large files one at a time to manage memory."""
        for key in file_keys:
            try:
                # Get file object
                obj = self.store.get_file(key, bucket)
                
                # Process file in chunks if needed
                yield {
                    "key": key,
                    "size": len(obj.body.getvalue()),
                    "content": obj.body.getvalue(),
                    "processed": True
                }
                
                # Explicit cleanup
                obj.body.close()
                del obj
                
                # Suggest garbage collection
                gc.collect()
                
            except Exception as e:
                yield {
                    "key": key,
                    "error": str(e),
                    "processed": False
                }
    
    def batch_process_files(self, file_keys: list[str], batch_size: int = 10, bucket: str = None):
        """Process files in batches."""
        for i in range(0, len(file_keys), batch_size):
            batch = file_keys[i:i + batch_size]
            
            results = list(self.process_large_files(batch, bucket))
            
            # Process batch results
            for result in results:
                if result["processed"]:
                    print(f"Processed {result['key']}: {result['size']} bytes")
                else:
                    print(f"Failed to process {result['key']}: {result['error']}")
            
            # Clear batch from memory
            del batch, results
            gc.collect()
```

### Caching Strategies

```python
from functools import lru_cache
from data_store.object_store.models import ObjectMetadata
from typing import List

class CachedFileOperations:
    """File operations with caching."""
    
    def __init__(self, store):
        self.store = store
    
    @lru_cache(maxsize=128)
    def get_file_metadata(self, key: str, bucket: str = None) -> ObjectMetadata:
        """Get file metadata with caching."""
        files = list(self.store.list_files(prefix=key, bucket=bucket))
        if files:
            return files[0]
        raise FileNotFoundError(f"File {key} not found")
    
    def get_multiple_file_metadata(self, keys: List[str], bucket: str = None) -> List[ObjectMetadata]:
        """Get metadata for multiple files with caching."""
        results = []
        
        for key in keys:
            try:
                metadata = self.get_file_metadata(key, bucket)
                results.append(metadata)
            except FileNotFoundError:
                results.append(None)
        
        return results
    
    def clear_cache(self):
        """Clear the metadata cache."""
        self.get_file_metadata.cache_clear()
```

## Model Testing

### Unit Testing Models

```python
import unittest
from data_store.object_store.models import Bucket, ObjectMetadata, Object
from datetime import datetime
import io

class TestObjectStoreModels(unittest.TestCase):
    """Test cases for object store models."""
    
    def test_bucket_model(self):
        """Test Bucket model creation and access."""
        bucket = Bucket(
            name="test-bucket",
            created_time=datetime(2024, 1, 15, 10, 30, 0)
        )
        
        self.assertEqual(bucket.name, "test-bucket")
        self.assertEqual(bucket.created_time, datetime(2024, 1, 15, 10, 30, 0))
        
        # Test immutability
        with self.assertRaises(Exception):
            bucket.name = "new-name"
    
    def test_object_metadata_model(self):
        """Test ObjectMetadata model."""
        metadata = ObjectMetadata(
            key="test/file.txt",
            updated_time=datetime(2024, 1, 20, 14, 45, 30),
            size=1024
        )
        
        self.assertEqual(metadata.key, "test/file.txt")
        self.assertEqual(metadata.size, 1024)
        self.assertTrue(metadata.key.endswith(".txt"))
    
    def test_object_model(self):
        """Test Object model."""
        content = b"Test content"
        body = io.BytesIO(content)
        
        obj = Object(
            body=body,
            updated_time=datetime(2024, 1, 20, 14, 45, 30)
        )
        
        obj.body.seek(0)
        self.assertEqual(obj.body.read(), content)
        obj.body.seek(0)
        self.assertEqual(len(obj.body.read()), len(content))

if __name__ == "__main__":
    unittest.main()
```

### Integration Testing with Models

```python
import pytest
from data_store.object_store import ObjectStore
from data_store.object_store.models import ObjectMetadata

class TestModelIntegration:
    """Integration tests for models with actual storage."""
    
    @pytest.fixture
    def object_store(self):
        """Create test object store."""
        config = {
            "framework": "minio",
            "root_bucket": "test-bucket",
            "connection": {
                "endpoint": "localhost:9000",
                "access_key": "minioadmin",
                "secret_key": "minioadmin",
                "secure": False
            }
        }
        return ObjectStore(config)
    
    def test_upload_and_retrieve_metadata(self, object_store):
        """Test upload and retrieve file metadata."""
        # Create test file
        test_content = b"Hello, World!"
        test_file = "/tmp/test_file.txt"
        
        with open(test_file, "wb") as f:
            f.write(test_content)
        
        try:
            # Upload file
            object_store.upload_file(test_file, "test/upload.txt")
            
            # Get metadata
            metadata = list(object_store.list_files(prefix="test/upload.txt"))[0]
            
            # Verify metadata
            assert isinstance(metadata, ObjectMetadata)
            assert metadata.key == "test/upload.txt"
            assert metadata.size == len(test_content)
            
        finally:
            # Cleanup
            import os
            if os.path.exists(test_file):
                os.remove(test_file)
            
            try:
                object_store.delete_file("test/upload.txt")
            except:
                pass
```

## Conclusion

The models in the data_store project provide a robust foundation for representing storage entities and their metadata. Key features include:

- **Type Safety**: Strong typing prevents many common errors
- **Immutability**: Frozen dataclasses ensure data integrity
- **Serialization Support**: Easy conversion to and from various formats
- **Extensibility**: Easy to add new fields and validation rules
- **Performance**: Memory-efficient handling of large objects

For more information about using these models with the storage systems, see:
- {doc}`../user_guides/nosql_store` - NoSQL store interface and usage
- {doc}`../user_guides/object_store` - Object store interface and usage
- {doc}`abstract_base_classes` - Abstract interfaces and design patterns
- {doc}`configuration_classes` - Configuration models and validation
- {doc}`adapters` - Adapter implementations and extension points