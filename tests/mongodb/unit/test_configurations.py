"""Unit tests for MongoDB configuration models.

These tests validate NoSQLConnection, NoSQLConfiguration, and Framework enum.
"""

import pytest

from data_store.nosql_store.configurations import (
    Framework,
    NoSQLConfiguration,
    NoSQLConnection,
)


class TestFrameworkEnum:
    """Test Framework enum values and functionality."""

    def test_framework_enum_values(self):
        """Test that Framework enum contains expected values."""
        assert Framework.MONGODB.value == "mongodb"
        assert Framework.COUCHDB.value == "couchdb"
        assert Framework.DYNAMODB.value == "dynamodb"

    def test_framework_enum_iteration(self):
        """Test iterating over Framework enum."""
        frameworks = [f.value for f in Framework]
        expected_frameworks = ["mongodb", "couchdb", "dynamodb"]
        assert set(frameworks) == set(expected_frameworks)
        assert len(frameworks) == 3

    def test_framework_enum_string_representation(self):
        """Test string representation of Framework enum."""
        assert str(Framework.MONGODB) == "mongodb"
        assert repr(Framework.MONGODB) == "<Framework.MONGODB: 'mongodb'>"


class TestNoSQLConnection:
    """Test NoSQLConnection model validation and URI building."""

    def test_valid_connection_with_uri(self):
        """Test creating NoSQLConnection with complete URI."""
        uri = "mongodb://user:pass@localhost:27017/testdb"
        connection = NoSQLConnection(uri=uri)
        assert connection.uri == uri
        assert connection.connection_uri == uri

    def test_valid_connection_with_host_only(self):
        """Test creating NoSQLConnection with host only."""
        host = "localhost"
        connection = NoSQLConnection(host=host)
        assert connection.host == host
        assert connection.connection_uri == "mongodb://localhost"

    def test_valid_connection_with_host_and_port(self):
        """Test creating NoSQLConnection with host and port."""
        host = "localhost"
        port = 27017
        connection = NoSQLConnection(host=host, port=port)
        assert connection.host == host
        assert connection.port == port
        assert connection.connection_uri == "mongodb://localhost:27017"

    def test_connection_with_authentication(self):
        """Test creating NoSQLConnection with username and password."""
        host = "localhost"
        username = "admin"
        password = "secret"
        connection = NoSQLConnection(host=host, username=username, password=password)
        expected_uri = "mongodb://admin:secret@localhost"
        assert connection.connection_uri == expected_uri

    def test_connection_with_username_only(self):
        """Test creating NoSQLConnection with username but no password."""
        host = "localhost"
        username = "admin"
        connection = NoSQLConnection(host=host, username=username)
        expected_uri = "mongodb://admin@localhost"
        assert connection.connection_uri == expected_uri

    def test_connection_with_database(self):
        """Test creating NoSQLConnection with database specified."""
        host = "localhost"
        database = "myapp"
        connection = NoSQLConnection(host=host, database=database)
        expected_uri = "mongodb://localhost/myapp"
        assert connection.connection_uri == expected_uri

    def test_connection_with_auth_source(self):
        """Test creating NoSQLConnection with auth_source parameter."""
        host = "localhost"
        auth_source = "admin"
        connection = NoSQLConnection(host=host, auth_source=auth_source)
        expected_uri = "mongodb://localhost?authSource=admin"
        assert connection.connection_uri == expected_uri

    def test_connection_with_ssl_enabled(self):
        """Test creating NoSQLConnection with SSL enabled."""
        host = "localhost"
        ssl = True
        connection = NoSQLConnection(host=host, ssl=ssl)
        expected_uri = "mongodb+srv://localhost"
        assert connection.connection_uri == expected_uri

    def test_connection_with_ssl_disabled(self):
        """Test creating NoSQLConnection with SSL explicitly disabled."""
        host = "localhost"
        ssl = False
        connection = NoSQLConnection(host=host, ssl=ssl)
        expected_uri = "mongodb://localhost"
        assert connection.connection_uri == expected_uri

    def test_connection_with_all_parameters(self):
        """Test creating NoSQLConnection with all parameters."""
        host = "db.example.com"
        port = 27017
        username = "admin"
        password = "secret123"
        database = "production"
        auth_source = "admin"
        ssl = True
        connection = NoSQLConnection(
            host=host,
            port=port,
            username=username,
            password=password,
            database=database,
            auth_source=auth_source,
            ssl=ssl,
        )
        expected_uri = "mongodb+srv://admin:secret123@db.example.com:27017/production?authSource=admin"
        assert connection.connection_uri == expected_uri

    def test_connection_validation_missing_uri_and_host(self):
        """Test validation error when neither URI nor host is provided."""
        with pytest.raises(ValueError, match="Either 'uri' or 'host' must be provided"):
            NoSQLConnection()

    def test_connection_validation_missing_host_for_uri_building(self):
        """Test error when trying to build URI without host."""
        connection = NoSQLConnection(host="localhost")
        connection.host = None
        with pytest.raises(ValueError, match="Host is required to build URI"):
            _ = connection.connection_uri

    def test_connection_uri_takes_precedence(self):
        """Test that provided URI takes precedence over individual components."""
        uri = "mongodb://override:pass@override.com:9999/override"
        host = "localhost"
        port = 27017
        connection = NoSQLConnection(uri=uri, host=host, port=port)
        assert connection.connection_uri == uri
        assert connection.host == host
        assert connection.port == port

    def test_connection_with_multiple_query_parameters(self):
        """Test NoSQLConnection with multiple query parameters."""
        host = "localhost"
        database = "testdb"
        auth_source = "admin"
        connection = NoSQLConnection(
            host=host, database=database, auth_source=auth_source
        )
        expected_uri = "mongodb://localhost/testdb?authSource=admin"
        assert connection.connection_uri == expected_uri

    def test_connection_default_values(self):
        """Test NoSQLConnection default field values."""
        connection = NoSQLConnection(host="localhost")
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
        connection = NoSQLConnection(host="localhost")
        config = NoSQLConfiguration(connection=connection)
        assert config.framework == "mongodb"
        assert config.connection == connection

    def test_configuration_with_framework_enum(self):
        """Test creating NoSQLConfiguration with Framework enum."""
        connection = NoSQLConnection(host="localhost")
        framework = Framework.COUCHDB
        config = NoSQLConfiguration(framework=framework, connection=connection)
        assert config.framework == "couchdb"
        assert config.connection == connection

    def test_configuration_with_framework_string(self):
        """Test creating NoSQLConfiguration with framework as string."""
        connection = NoSQLConnection(host="localhost")
        framework = "dynamodb"
        config = NoSQLConfiguration(framework=framework, connection=connection)
        assert config.framework == "dynamodb"
        assert config.connection == connection

    def test_configuration_with_complete_connection(self):
        """Test creating NoSQLConfiguration with complete connection settings."""
        connection = NoSQLConnection(
            host="db.example.com",
            port=27017,
            username="admin",
            password="secret",
            database="myapp",
            auth_source="admin",
            ssl=True,
        )
        config = NoSQLConfiguration(framework=Framework.MONGODB, connection=connection)
        assert config.framework == "mongodb"
        assert config.connection == connection
        assert config.connection.host == "db.example.com"
        assert config.connection.port == 27017
        assert config.connection.username == "admin"
        assert config.connection.ssl is True

    def test_configuration_serialization(self):
        """Test NoSQLConfiguration model serialization."""
        connection = NoSQLConnection(host="localhost", port=27017, database="testdb")
        config = NoSQLConfiguration(framework=Framework.MONGODB, connection=connection)
        config_dict = config.model_dump()
        assert "framework" in config_dict
        assert "connection" in config_dict
        assert config_dict["framework"] == "mongodb"
        assert config_dict["connection"]["host"] == "localhost"
        assert config_dict["connection"]["port"] == 27017
        assert config_dict["connection"]["database"] == "testdb"

    def test_configuration_from_dict(self):
        """Test creating NoSQLConfiguration from dictionary."""
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
        config = NoSQLConfiguration(**config_dict)
        assert config.framework == "mongodb"
        assert config.connection.host == "localhost"
        assert config.connection.port == 27017
        assert config.connection.username == "admin"
        assert config.connection.password == "secret"
        assert config.connection.database == "myapp"

    def test_configuration_with_uri_connection(self):
        """Test creating NoSQLConfiguration with URI-based connection."""
        uri = "mongodb+srv://user:pass@cluster.mongodb.net/database?authSource=admin"
        connection = NoSQLConnection(uri=uri)
        config = NoSQLConfiguration(framework=Framework.MONGODB, connection=connection)
        assert config.framework == "mongodb"
        assert config.connection.uri == uri
        assert config.connection.connection_uri == uri

    def test_configuration_framework_enum_values(self):
        """Test NoSQLConfiguration with all Framework enum values."""
        connection = NoSQLConnection(host="localhost")
        for framework in Framework:
            config = NoSQLConfiguration(framework=framework, connection=connection)
            assert config.framework == framework
            assert config.connection == connection

    def test_configuration_model_validation(self):
        """Test NoSQLConfiguration model validation propagates to connection."""
        with pytest.raises(ValueError, match="Either 'uri' or 'host' must be provided"):
            NoSQLConfiguration(
                framework=Framework.MONGODB, connection=NoSQLConnection()
            )
