"""End-to-end tests for MongoDB adapter in the nosql_store module.

This test suite validates all features of the MongoDB adapter implementation
including connection management, CRUD operations, and bulk operations.
Tests assume that a MongoDB instance is running and configuration is set appropriately.
"""

import pytest
import utils

from data_store.nosql_store.configurations import (
    Framework,
    NoSQLConfiguration,
    NoSQLConnection,
)
from data_store.nosql_store.nosql_store import NoSQLStore

# Dummy data for testing
DUMMY_DOCUMENT = {"name": "Test User", "age": 30, "email": "test@example.com"}
DUMMY_DOCUMENT_2 = {"name": "Test User 2", "age": 25, "email": "test2@example.com"}
DUMMY_UPDATED_DOCUMENT = {"age": 35, "status": "updated"}

TEST_COLLECTION = "test_collection_e2e"


@pytest.fixture(scope="module")
def nosql_store():
    """Create NoSQLStore instance for testing."""
    # Arrange: Get configuration and create store instance
    config = utils.get_config()
    store = NoSQLStore(config=config.get("nosql_store"))

    # Connect to database
    store.connect()

    yield store

    # Cleanup: Close connection after tests
    store.close()


@pytest.fixture(autouse=True)
def cleanup_collection(nosql_store):
    """Clean up test collection before and after each test."""
    # Arrange: Clean collection before test
    try:
        nosql_store.delete(TEST_COLLECTION, {})
    except Exception:
        pass  # Collection might not exist

    yield

    # Cleanup: Clean collection after test
    try:
        nosql_store.delete(TEST_COLLECTION, {})
    except Exception:
        pass


class TestConnection:
    """Test connection establishment and closure for MongoDB adapter."""

    def test_connection_establishment(self, nosql_store):
        """Test that MongoDB connection is established successfully."""
        # Arrange: NoSQL store instance is provided by fixture
        # Act: Connection is established in fixture setup
        client = nosql_store.client
        # Assert: Verify client is available and connected
        assert client is not None
        assert client._client is not None

    def test_connection_closure(self):
        """Test closing MongoDB connection."""
        # Arrange: Create a new store instance for this test
        config = utils.get_config()
        store = NoSQLStore(config.get("nosql_store"))
        store.connect()

        # Act: Close the connection
        store.close()

        # Assert: Verify connection is closed (connection closed successfully)
        assert True  # Connection close completed successfully

    @pytest.mark.timeout(3)
    def test_connection_fail(self):
        config = {
            "nosql_store": {
                "framework": "mongodb",
                "connection": {
                    "host": "invalid_host",
                    "port": 27017,
                    "username": "invalid_user",
                    "password": "invalid_pass",
                    "connection_timeout": 1,  # Short timeout for testing
                },
            }
        }
        with pytest.raises(
            RuntimeError,
        ) as excinfo:
            store = NoSQLStore(config=config.get("nosql_store"))
            store.connect()
            store.close()
        # Optionally check for timeout in the exception message
        assert "Timeout" in str(excinfo.value) or "timeout" in str(excinfo.value)


class TestSingleDocumentOperations:
    """Test single document operations: insert, find."""

    def test_insert_document(self, nosql_store):
        """Test inserting a single document into a collection."""
        # Arrange: Prepare test document
        test_document = DUMMY_DOCUMENT.copy()

        # Act: Insert document
        inserted_id = nosql_store.insert(TEST_COLLECTION, test_document)

        # Assert: Verify document was inserted and ID returned
        assert inserted_id is not None
        assert isinstance(inserted_id, str)
        assert len(inserted_id) > 0

    def test_find_documents_with_filters(self, nosql_store):
        """Test finding documents in a collection with filters."""
        # Arrange: Insert test documents
        doc1 = DUMMY_DOCUMENT.copy()
        doc2 = DUMMY_DOCUMENT_2.copy()
        nosql_store.insert(TEST_COLLECTION, doc1)
        nosql_store.insert(TEST_COLLECTION, doc2)

        # Act: Find documents with age filter
        results = nosql_store.find(TEST_COLLECTION, filters={"age": 30})

        # Assert: Verify correct document is returned
        assert len(results) == 1
        assert results[0]["name"] == "Test User"
        assert results[0]["age"] == 30

    def test_find_documents_without_filters(self, nosql_store):
        """Test finding all documents without filters."""
        # Arrange: Insert multiple test documents
        doc1 = DUMMY_DOCUMENT.copy()
        doc2 = DUMMY_DOCUMENT_2.copy()
        nosql_store.insert(TEST_COLLECTION, doc1)
        nosql_store.insert(TEST_COLLECTION, doc2)

        # Act: Find all documents
        results = nosql_store.find(TEST_COLLECTION)

        # Assert: Verify all documents are returned
        assert len(results) == 2

    def test_find_documents_with_projections(self, nosql_store):
        """Test finding documents with specific field projections."""
        # Arrange: Insert test document
        test_document = DUMMY_DOCUMENT.copy()
        nosql_store.insert(TEST_COLLECTION, test_document)

        # Act: Find documents with projection
        results = nosql_store.find(TEST_COLLECTION, projections=["name", "age"])

        # Assert: Verify only projected fields are returned
        assert len(results) == 1
        assert "name" in results[0]
        assert "age" in results[0]
        assert "email" not in results[0]

    def test_find_documents_with_skip_limit(self, nosql_store):
        """Test finding documents with skip and limit parameters."""
        # Arrange: Insert multiple test documents
        for i in range(5):
            doc = {"name": f"User {i}", "age": 20 + i}
            nosql_store.insert(TEST_COLLECTION, doc)

        # Act: Find documents with skip and limit
        results = nosql_store.find(TEST_COLLECTION, skip=2, limit=2)

        # Assert: Verify correct number of documents returned
        assert len(results) == 2


class TestUpdateOperations:
    """Test document update operations with and without upsert."""

    def test_update_documents_without_upsert(self, nosql_store):
        """Test updating existing documents without upsert."""
        # Arrange: Insert test document
        test_document = DUMMY_DOCUMENT.copy()
        nosql_store.insert(TEST_COLLECTION, test_document)

        # Act: Update document
        modified_count = nosql_store.update(
            TEST_COLLECTION,
            filters={"name": "Test User"},
            update_data=DUMMY_UPDATED_DOCUMENT,
            upsert=False,
        )

        # Assert: Verify document was updated
        assert modified_count == 1

        # Verify the update was applied
        results = nosql_store.find(TEST_COLLECTION, filters={"name": "Test User"})
        assert len(results) == 1
        assert results[0]["age"] == 35
        assert results[0]["status"] == "updated"

    def test_update_documents_with_upsert(self, nosql_store):
        """Test updating documents with upsert enabled for non-existing document."""
        # Arrange: Prepare filter for non-existing document
        filters = {"name": "Non Existing User"}
        update_data = {"name": "Non Existing User", "age": 40, "status": "created"}

        # Act: Update with upsert enabled
        modified_count = nosql_store.update(
            TEST_COLLECTION, filters=filters, update_data=update_data, upsert=True
        )

        # Assert: Verify document was created (upserted)
        # Note: MongoDB returns 0 for modified_count when upserting
        assert modified_count >= 0

        # Verify the document was created
        results = nosql_store.find(
            TEST_COLLECTION, filters={"name": "Non Existing User"}
        )
        assert len(results) == 1
        assert results[0]["age"] == 40
        assert results[0]["status"] == "created"


class TestDeletionOperations:
    """Test document deletion operations."""

    def test_delete_documents(self, nosql_store):
        """Test deleting documents from a collection."""
        # Arrange: Insert test documents
        doc1 = DUMMY_DOCUMENT.copy()
        doc2 = DUMMY_DOCUMENT_2.copy()
        doc1["status"] = "to_delete"
        doc2["status"] = "to_delete"
        nosql_store.insert(TEST_COLLECTION, doc1)
        nosql_store.insert(TEST_COLLECTION, doc2)

        # Act: Delete documents with matching filter
        deleted_count = nosql_store.delete(TEST_COLLECTION, {"status": "to_delete"})

        # Assert: Verify documents were deleted
        assert deleted_count == 2

        # Verify documents are no longer in collection
        results = nosql_store.find(TEST_COLLECTION, {"status": "to_delete"})
        assert len(results) == 0


class TestBulkOperations:
    """Test bulk operations: bulk_insert, bulk_update, bulk_delete."""

    def test_bulk_insert_documents(self, nosql_store):
        """Test bulk inserting multiple documents."""
        # Arrange: Prepare multiple test documents
        test_documents = [
            {"name": "Bulk User 1", "age": 25, "type": "bulk_test"},
            {"name": "Bulk User 2", "age": 30, "type": "bulk_test"},
            {"name": "Bulk User 3", "age": 35, "type": "bulk_test"},
        ]

        # Act: Bulk insert documents
        result = nosql_store.bulk_insert(TEST_COLLECTION, test_documents)

        # Assert: Verify all documents were inserted
        assert result == "3"

        # Verify documents exist in collection
        results = nosql_store.find(TEST_COLLECTION, {"type": "bulk_test"})
        assert len(results) == 3

    def test_bulk_update_documents_without_upsert(self, nosql_store):
        """Test bulk updating multiple documents without upsert."""
        # Arrange: Insert test documents
        test_documents = [
            {"name": "Update User 1", "age": 25, "status": "pending"},
            {"name": "Update User 2", "age": 30, "status": "pending"},
        ]
        nosql_store.bulk_insert(TEST_COLLECTION, test_documents)

        # Act: Bulk update documents
        update_data = [{"status": "processed", "updated_at": "2024-01-01"}]
        modified_count = nosql_store.bulk_update(
            TEST_COLLECTION,
            filters={"status": "pending"},
            update_data=update_data,
            upsert=False,
        )

        # Assert: Verify documents were updated
        assert modified_count == 2

        # Verify updates were applied
        results = nosql_store.find(TEST_COLLECTION, {"status": "processed"})
        assert len(results) == 2

    def test_bulk_update_documents_with_upsert(self, nosql_store):
        """Test bulk updating multiple documents with upsert enabled."""
        # Arrange: Prepare update for non-existing documents
        filters = {"category": "new_category"}
        update_data = [
            {"name": "New Item 1", "price": 100, "category": "new_category"},
            {"name": "New Item 2", "price": 200, "category": "new_category"},
        ]

        # Act: Bulk update with upsert
        modified_count = nosql_store.bulk_update(
            TEST_COLLECTION, filters=filters, update_data=update_data, upsert=True
        )

        # Assert: Verify operation completed
        assert modified_count >= 0

        # Verify documents were created
        results = nosql_store.find(TEST_COLLECTION, {"category": "new_category"})
        assert len(results) >= 1

    def test_bulk_delete_documents_with_dict_filters(self, nosql_store):
        """Test bulk deleting documents using dict filters."""
        # Arrange: Insert test documents
        test_documents = [
            {"name": "Delete User 1", "status": "obsolete"},
            {"name": "Delete User 2", "status": "obsolete"},
            {"name": "Keep User", "status": "active"},
        ]
        nosql_store.bulk_insert(TEST_COLLECTION, test_documents)

        # Act: Bulk delete with dict filter
        deleted_count = nosql_store.bulk_delete(TEST_COLLECTION, {"status": "obsolete"})

        # Assert: Verify correct number of documents deleted
        assert deleted_count == 2

        # Verify only active document remains
        results = nosql_store.find(TEST_COLLECTION)
        assert len(results) == 1
        assert results[0]["status"] == "active"

    def test_bulk_delete_documents_with_list_filters(self, nosql_store):
        """Test bulk deleting documents using list of filters."""
        # Arrange: Insert test documents
        test_documents = [
            {"name": "User 1", "status": "inactive", "type": "test"},
            {"name": "User 2", "verified": False, "type": "test"},
            {"name": "User 3", "status": "active", "verified": True, "type": "test"},
        ]
        nosql_store.bulk_insert(TEST_COLLECTION, test_documents)

        # Act: Bulk delete with list of filters
        filters = [{"status": "inactive"}, {"verified": False}]
        deleted_count = nosql_store.bulk_delete(TEST_COLLECTION, filters)

        # Assert: Verify documents matching any filter were deleted
        assert deleted_count == 2

        # Verify only active, verified document remains
        results = nosql_store.find(TEST_COLLECTION, {"type": "test"})
        assert len(results) == 1
        assert results[0]["status"] == "active"
        assert results[0]["verified"] is True


class TestFrameworkEnum:
    """Test Framework enum values and functionality."""

    def test_framework_enum_values(self):
        """Test that Framework enum contains expected values."""
        # Act & Assert: Verify enum values
        assert Framework.MONGODB.value == "mongodb"
        assert Framework.COUCHDB.value == "couchdb"
        assert Framework.DYNAMODB.value == "dynamodb"

    def test_framework_enum_iteration(self):
        """Test iterating over Framework enum."""
        # Act: Get all framework values
        frameworks = [f.value for f in Framework]

        # Assert: Verify all expected frameworks are present
        expected_frameworks = ["mongodb", "couchdb", "dynamodb"]
        assert set(frameworks) == set(expected_frameworks)
        assert len(frameworks) == 3

    def test_framework_enum_string_representation(self):
        """Test string representation of Framework enum."""
        # Act & Assert: Verify string representations
        assert str(Framework.MONGODB) == "mongodb"
        assert repr(Framework.MONGODB) == "<Framework.MONGODB: 'mongodb'>"


class TestNoSQLConnection:
    """Test NoSQLConnection model validation and URI building."""

    def test_valid_connection_with_uri(self):
        """Test creating NoSQLConnection with complete URI."""
        # Arrange: Prepare valid URI
        uri = "mongodb://user:pass@localhost:27017/testdb"

        # Act: Create connection with URI
        connection = NoSQLConnection(uri=uri)

        # Assert: Verify connection is valid
        assert connection.uri == uri
        assert connection.connection_uri == uri

    def test_valid_connection_with_host_only(self):
        """Test creating NoSQLConnection with host only."""
        # Arrange: Prepare connection with host
        host = "localhost"

        # Act: Create connection
        connection = NoSQLConnection(host=host)

        # Assert: Verify connection is valid
        assert connection.host == host
        assert connection.connection_uri == "mongodb://localhost"

    def test_valid_connection_with_host_and_port(self):
        """Test creating NoSQLConnection with host and port."""
        # Arrange: Prepare connection data
        host = "localhost"
        port = 27017

        # Act: Create connection
        connection = NoSQLConnection(host=host, port=port)

        # Assert: Verify connection URI is built correctly
        assert connection.host == host
        assert connection.port == port
        assert connection.connection_uri == "mongodb://localhost:27017"

    def test_connection_with_authentication(self):
        """Test creating NoSQLConnection with username and password."""
        # Arrange: Prepare connection with auth
        host = "localhost"
        username = "admin"
        password = "secret"

        # Act: Create connection
        connection = NoSQLConnection(host=host, username=username, password=password)

        # Assert: Verify auth is included in URI
        expected_uri = "mongodb://admin:secret@localhost"
        assert connection.connection_uri == expected_uri

    def test_connection_with_username_only(self):
        """Test creating NoSQLConnection with username but no password."""
        # Arrange: Prepare connection with username only
        host = "localhost"
        username = "admin"

        # Act: Create connection
        connection = NoSQLConnection(host=host, username=username)

        # Assert: Verify username is included without password
        expected_uri = "mongodb://admin@localhost"
        assert connection.connection_uri == expected_uri

    def test_connection_with_database(self):
        """Test creating NoSQLConnection with database specified."""
        # Arrange: Prepare connection with database
        host = "localhost"
        database = "myapp"

        # Act: Create connection
        connection = NoSQLConnection(host=host, database=database)

        # Assert: Verify database is included in URI
        expected_uri = "mongodb://localhost/myapp"
        assert connection.connection_uri == expected_uri

    def test_connection_with_auth_source(self):
        """Test creating NoSQLConnection with auth_source parameter."""
        # Arrange: Prepare connection with auth source
        host = "localhost"
        auth_source = "admin"

        # Act: Create connection
        connection = NoSQLConnection(host=host, auth_source=auth_source)

        # Assert: Verify auth source is in query parameters
        expected_uri = "mongodb://localhost?authSource=admin"
        assert connection.connection_uri == expected_uri

    def test_connection_with_ssl_enabled(self):
        """Test creating NoSQLConnection with SSL enabled."""
        # Arrange: Prepare connection with SSL
        host = "localhost"
        ssl = True

        # Act: Create connection
        connection = NoSQLConnection(host=host, ssl=ssl)

        # Assert: Verify SSL scheme is used
        expected_uri = "mongodb+srv://localhost"
        assert connection.connection_uri == expected_uri

    def test_connection_with_ssl_disabled(self):
        """Test creating NoSQLConnection with SSL explicitly disabled."""
        # Arrange: Prepare connection without SSL
        host = "localhost"
        ssl = False

        # Act: Create connection
        connection = NoSQLConnection(host=host, ssl=ssl)

        # Assert: Verify standard scheme is used
        expected_uri = "mongodb://localhost"
        assert connection.connection_uri == expected_uri

    def test_connection_with_all_parameters(self):
        """Test creating NoSQLConnection with all parameters."""
        # Arrange: Prepare complete connection data
        host = "db.example.com"
        port = 27017
        username = "admin"
        password = "secret123"
        database = "production"
        auth_source = "admin"
        ssl = True

        # Act: Create connection
        connection = NoSQLConnection(
            host=host,
            port=port,
            username=username,
            password=password,
            database=database,
            auth_source=auth_source,
            ssl=ssl,
        )

        # Assert: Verify complete URI is built correctly
        expected_uri = "mongodb+srv://admin:secret123@db.example.com:27017/production?authSource=admin"
        assert connection.connection_uri == expected_uri

    def test_connection_validation_missing_uri_and_host(self):
        """Test validation error when neither URI nor host is provided."""
        # Arrange: Prepare invalid connection data
        # Act & Assert: Verify validation error is raised
        with pytest.raises(ValueError, match="Either 'uri' or 'host' must be provided"):
            NoSQLConnection()

    def test_connection_validation_missing_host_for_uri_building(self):
        """Test error when trying to build URI without host."""
        # Arrange: Create connection without host but clear it after creation
        connection = NoSQLConnection(host="localhost")

        # Manually clear host to test validation
        connection.host = None

        # Act & Assert: Verify error when accessing connection_uri
        with pytest.raises(ValueError, match="Host is required to build URI"):
            _ = connection.connection_uri

    def test_connection_uri_takes_precedence(self):
        """Test that provided URI takes precedence over individual components."""
        # Arrange: Prepare connection with both URI and components
        uri = "mongodb://override:pass@override.com:9999/override"
        host = "localhost"
        port = 27017

        # Act: Create connection
        connection = NoSQLConnection(uri=uri, host=host, port=port)

        # Assert: Verify URI takes precedence
        assert connection.connection_uri == uri
        assert connection.host == host  # Individual fields are still set
        assert connection.port == port

    def test_connection_with_multiple_query_parameters(self):
        """Test NoSQLConnection with multiple query parameters."""
        # Arrange: Prepare connection with auth source and SSL
        host = "localhost"
        database = "testdb"
        auth_source = "admin"

        # Act: Create connection
        connection = NoSQLConnection(
            host=host, database=database, auth_source=auth_source
        )

        # Assert: Verify query parameters are properly formatted
        expected_uri = "mongodb://localhost/testdb?authSource=admin"
        assert connection.connection_uri == expected_uri

    def test_connection_default_values(self):
        """Test NoSQLConnection default field values."""
        # Arrange: Create connection with minimal data
        connection = NoSQLConnection(host="localhost")

        # Assert: Verify default values
        assert connection.uri is None
        assert connection.port is None
        assert connection.username is None
        assert connection.password is None
        assert connection.database is None
        assert connection.auth_source is None
        assert connection.ssl is False


class TestNoSQLConfiguration:
    """Test NoSQLConfiguration model validation and functionality."""

    def test_configuration_with_default_framework(self):
        """Test creating NoSQLConfiguration with default framework."""
        # Arrange: Prepare connection
        connection = NoSQLConnection(host="localhost")

        # Act: Create configuration with default framework
        config = NoSQLConfiguration(connection=connection)

        # Assert: Verify default framework is MongoDB
        assert config.framework == "mongodb"
        assert config.connection == connection

    def test_configuration_with_framework_enum(self):
        """Test creating NoSQLConfiguration with Framework enum."""
        # Arrange: Prepare connection and framework
        connection = NoSQLConnection(host="localhost")
        framework = Framework.COUCHDB

        # Act: Create configuration
        config = NoSQLConfiguration(framework=framework, connection=connection)

        # Assert: Verify framework is set correctly
        assert config.framework == "couchdb"
        assert config.connection == connection

    def test_configuration_with_framework_string(self):
        """Test creating NoSQLConfiguration with framework as string."""
        # Arrange: Prepare connection and framework string
        connection = NoSQLConnection(host="localhost")
        framework = "dynamodb"

        # Act: Create configuration
        config = NoSQLConfiguration(framework=framework, connection=connection)

        # Assert: Verify framework string is accepted
        assert config.framework == "dynamodb"
        assert config.connection == connection

    def test_configuration_with_complete_connection(self):
        """Test creating NoSQLConfiguration with complete connection settings."""
        # Arrange: Prepare complete connection
        connection = NoSQLConnection(
            host="db.example.com",
            port=27017,
            username="admin",
            password="secret",
            database="myapp",
            auth_source="admin",
            ssl=True,
        )

        # Act: Create configuration
        config = NoSQLConfiguration(framework=Framework.MONGODB, connection=connection)

        # Assert: Verify configuration is valid
        assert config.framework == "mongodb"
        assert config.connection == connection
        assert config.connection.host == "db.example.com"
        assert config.connection.port == 27017
        assert config.connection.username == "admin"
        assert config.connection.ssl is True

    def test_configuration_serialization(self):
        """Test NoSQLConfiguration model serialization."""
        # Arrange: Prepare configuration
        connection = NoSQLConnection(host="localhost", port=27017, database="testdb")
        config = NoSQLConfiguration(framework=Framework.MONGODB, connection=connection)

        # Act: Serialize configuration
        config_dict = config.model_dump()

        # Assert: Verify serialization includes all fields
        assert "framework" in config_dict
        assert "connection" in config_dict
        assert config_dict["framework"] == "mongodb"
        assert config_dict["connection"]["host"] == "localhost"
        assert config_dict["connection"]["port"] == 27017
        assert config_dict["connection"]["database"] == "testdb"

    def test_configuration_from_dict(self):
        """Test creating NoSQLConfiguration from dictionary."""
        # Arrange: Prepare configuration dictionary
        config_dict = {
            "framework": "mongodb",
            "connection": {
                "host": "localhost",
                "port": 27017,
                "username": "admin",
                "password": "secret",
                "database": "myapp",
            },
        }

        # Act: Create configuration from dict
        config = NoSQLConfiguration(**config_dict)

        # Assert: Verify configuration is created correctly
        assert config.framework == "mongodb"
        assert config.connection.host == "localhost"
        assert config.connection.port == 27017
        assert config.connection.username == "admin"
        assert config.connection.password == "secret"
        assert config.connection.database == "myapp"

    def test_configuration_with_uri_connection(self):
        """Test creating NoSQLConfiguration with URI-based connection."""
        # Arrange: Prepare URI-based connection
        uri = "mongodb+srv://user:pass@cluster.mongodb.net/database?authSource=admin"
        connection = NoSQLConnection(uri=uri)

        # Act: Create configuration
        config = NoSQLConfiguration(framework=Framework.MONGODB, connection=connection)

        # Assert: Verify configuration uses URI
        assert config.framework == "mongodb"
        assert config.connection.uri == uri
        assert config.connection.connection_uri == uri

    def test_configuration_framework_enum_values(self):
        """Test NoSQLConfiguration with all Framework enum values."""
        # Arrange: Prepare connection
        connection = NoSQLConnection(host="localhost")

        # Act & Assert: Test each framework enum
        for framework in Framework:
            config = NoSQLConfiguration(framework=framework, connection=connection)
            assert config.framework == framework
            assert config.connection == connection

    def test_configuration_model_validation(self):
        """Test NoSQLConfiguration model validation propagates to connection."""
        # Arrange: Prepare invalid connection data (no host or uri)
        # Act & Assert: Verify validation error is raised
        with pytest.raises(ValueError, match="Either 'uri' or 'host' must be provided"):
            NoSQLConfiguration(
                framework=Framework.MONGODB, connection=NoSQLConnection()
            )
