import logging
from typing import Any

import utils

__all__ = ["NoSQLStore"]
from data_store.nosql_store import abstract, adapters, configurations, models

logger = logging.getLogger(__file__)

DEFAULT_NOSQL_FRAMEWORK = "mongodb"


class ConnectionContext:
    """Context manager for automatic database connection lifecycle management"""

    def __init__(self, client: "NoSQLStore"):
        """Initialize connection context

        Args:
            client (NoSQLStore): The NoSQL store client instance to manage connections for
        """
        self.client = client
        logger.debug("ConnectionContext initialized")

    def __enter__(self):
        """Establish database connection on context entry

        Returns:
            NoSQLStore: The connected client instance

        Raises:
            RuntimeError: If connection establishment fails
        """
        logger.debug("Entering connection context - establishing connection")
        return self.client._connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close database connection on context exit

        Args:
            exc_type: Exception type if exception occurred, None otherwise
            exc_val: Exception value if exception occurred, None otherwise
            exc_tb: Exception traceback if exception occurred, None otherwise

        Returns:
            bool: False to propagate exceptions, True to suppress them
        """
        logger.debug(
            f"Exiting connection context - closing connection (exception: {exc_type})"
        )
        try:
            self.client._close()
        except Exception as close_error:
            logger.error(f"Error closing connection: {close_error}")
            # Don't suppress the original exception if there was one
            if exc_type is None:
                raise close_error
        return False  # Don't suppress exceptions


class NoSQLStore:
    """Main NoSQL store class providing high-level interface for NoSQL operations"""

    config: configurations.NoSQLConfiguration
    component_factory: abstract.NoSQLStoreComponentFactory

    def __init__(self, config: dict[str, Any] | None = None):
        config = config or utils.get_config().get("nosql_store")
        if config is None:
            raise ValueError("Configuration not found")

        self.config = configurations.NoSQLConfiguration(**config)
        self.component_factory = self._init_component_factory()

    @property
    def client(self) -> abstract.NoSQLStore:
        """Lazy initialization of NoSQL client"""
        if not hasattr(self, "_client"):
            self._client = self.component_factory.create_client()
        return self._client

    def connect(self):
        """Return a context manager for automatic connection lifecycle management

        Usage:
            with store.connect() as connection:
                # Connection is automatically established
                store.insert("collection", data)
                # Connection is automatically closed on exit

        Returns:
            ConnectionContext: Context manager that handles connection lifecycle
        """
        return ConnectionContext(self)

    def _connect(self):
        """Establish database connection"""
        return self.client.connect()

    def _close(self):
        """Close database connection"""
        return self.client.close()

    def insert(self, collection: str, data: dict) -> str:
        """Insert a document into a collection

        Args:
            collection (str): Name of the collection to insert into
            data (dict): Document data to insert

        Returns:
            str: ID of the inserted document

        Raises:
            ValueError: If collection name is empty or data is None
            RuntimeError: If database operation fails

        Examples:
            >>> doc_id = store.insert("users", {"name": "John", "age": 30})
        """
        return self.client.insert(collection=collection, data=data)

    def find(
        self,
        collection: str,
        filters: dict | None = None,
        projections: list[str] | None = None,
        skip: int = 0,
        limit: int = 0,
    ) -> list:
        """Find documents in a collection

        Args:
            collection (str): Collection name
            filters (dict | None): Query filters, default is None for find all
            projections (list[str] | None): Fields to include in results, default is None
            skip (int): Number of documents to skip, default is 0
            limit (int): Maximum number of documents to return, default is 0 (no limit)

        Returns:
            list: List of documents matching the query

        Raises:
            ValueError: If collection name is empty

        Examples:
            >>> results = store.find("collection", filters={"field": "value"}, projections=["field1", "field2"], skip=10, limit=5)
            >>> all_results = store.find("collection")  # Find all documents in collection

        """
        return self.client.find(
            collection=collection,
            filters=filters,
            projections=projections,
            skip=skip,
            limit=limit,
        )

    def update(
        self,
        collection: str,
        filters: dict,
        update_data: dict,
        upsert: bool = False,
    ) -> int:
        """Update documents in a collection

        Args:
            collection (str): Name of the collection to update
            filters (dict): Query filters to select documents
            update_data (dict): Update operations or new field values
            upsert (bool): Create document if it doesn't exist, default False

        Returns:
            int: Number of documents modified

        Raises:
            ValueError: If collection name is empty or filters/update_data are None
            RuntimeError: If database operation fails

        Examples:
            >>> updated = store.update("users", {"name": "John"}, {"$set": {"age": 31}})
        """
        return self.client.update(
            collection=collection,
            filters=filters,
            update_data=update_data,
            upsert=upsert,
        )

    def delete(self, collection: str, filters: dict) -> int:
        """Delete documents from a collection

        Args:
            collection (str): Name of the collection to delete from
            filters (dict): Query filters to select documents

        Returns:
            int: Number of documents deleted

        Raises:
            ValueError: If collection name is empty or filters are None
            RuntimeError: If database operation fails

        Examples:
            >>> deleted = store.delete("users", {"name": "John"})
        """
        return self.client.delete(collection=collection, filters=filters)

    def bulk_insert(self, collection: str, data: list[dict]) -> str:
        """Insert multiple documents into a collection

        Args:
            collection (str): Name of the collection to insert into
            data (list[dict]): List of documents to insert

        Returns:
            str: String representation of count of inserted documents

        Raises:
            ValueError: If collection name is empty or data is None
            RuntimeError: If database operation fails

        Examples:
            >>> result = store.bulk_insert("users", [{"name": "John"}, {"name": "Jane"}])
        """
        return self.client.bulk_insert(collection=collection, data=data)

    def bulk_update(
        self,
        collection: str,
        filters: dict,
        update_data: list[dict],
        upsert: bool = False,
    ) -> int:
        """Update multiple documents in a collection

        Args:
            collection (str): Name of the collection to update
            filters (dict): Query filters to select documents
            update_data (list[dict]): List of update operations or new field values
            upsert (bool): Create document if it doesn't exist, default False

        Returns:
            int: Total number of documents modified

        Raises:
            ValueError: If collection name is empty or filters/update_data are None
            RuntimeError: If database operation fails

        Examples:
            >>> updated = store.bulk_update("users", {"active": True}, [{"$set": {"last_login": now}}])
        """
        return self.client.bulk_update(
            collection=collection,
            filters=filters,
            update_data=update_data,
            upsert=upsert,
        )

    def bulk_delete(self, collection: str, filters: dict | list) -> int:
        """Delete multiple documents from a collection

        Args:
            collection (str): Name of the collection to delete from
            filters (dict | list): Query filter(s) to select documents

        Returns:
            int: Total number of documents deleted

        Raises:
            ValueError: If collection name is empty or filters are None
            RuntimeError: If database operation fails

        Examples:
            >>> deleted = store.bulk_delete("users", {"status": "inactive"})
            >>> deleted = store.bulk_delete("users", [{"status": "inactive"}, {"age": {"$lt": 18}}])
        """
        return self.client.bulk_delete(collection=collection, filters=filters)

    def _init_component_factory(self) -> abstract.NoSQLStoreComponentFactory:
        """Initialize the component factory based on configured framework"""
        framework = self.config.framework or DEFAULT_NOSQL_FRAMEWORK

        # Handle both string and enum types

        if isinstance(framework, configurations.Framework):
            framework_str = framework.value
        else:
            framework_str = str(framework)

        if framework_str not in adapters.adapter_router:
            raise ValueError(f"Doesn't support framework: {framework_str}")

        return adapters.adapter_router[framework_str](self.config)
