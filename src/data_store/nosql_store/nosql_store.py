import contextlib
import logging
from typing import Any

import utils

__all__ = ["NoSQLStore"]
from data_store.nosql_store import abstract, adapters, configurations, models

logger = logging.getLogger(__file__)

DEFAULT_NOSQL_FRAMEWORK = "mongodb"


class NoSQLStore:
    """Main NoSQL store class providing high-level interface for NoSQL operations"""

    config: configurations.NoSQLConfiguration
    component_factory: abstract.NoSQLStoreComponentFactory

    def __init__(self, config: dict[str, Any] | None = None, *args, **kwargs):
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

    @contextlib.contextmanager
    def connect(self, *args, **kwargs):
        """Return a context manager for automatic connection lifecycle management

        Usage:
            with store.connect() as connection:
                # Connection is automatically established
                store.insert("collection", data)
                # Connection is automatically closed on exit

        Returns:
            ConnectionContext: Context manager that handles connection lifecycle
        """
        # return ConnectionContext(self)
        self._connect(*args, **kwargs)
        yield self
        self._close()

    def _connect(self, *args, **kwargs):
        """Establish database connection"""
        return self.client.connect(*args, **kwargs)

    def _close(self, *args, **kwargs):
        """Close database connection"""
        return self.client.close(*args, **kwargs)

    def insert(self, collection: str, data: dict, *args, **kwargs) -> str:
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
        return self.client.insert(collection, data, *args, **kwargs)

    def find(
        self,
        collection: str,
        filters: dict | None = None,
        projections: list[str] | None = None,
        skip: int = 0,
        limit: int = 0,
        *args,
        **kwargs,
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
            collection,
            filters,
            projections,
            skip,
            limit,
            *args,
            **kwargs,
        )

    def update(
        self,
        collection: str,
        filters: dict,
        update_data: dict,
        upsert: bool = False,
        *args,
        **kwargs,
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
            collection,
            filters,
            update_data,
            upsert,
            *args,
            **kwargs,
        )

    def delete(self, collection: str, filters: dict, *args, **kwargs) -> int:
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
        return self.client.delete(collection, filters, *args, **kwargs)

    def bulk_insert(self, collection: str, data: list[dict], *args, **kwargs) -> str:
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
        return self.client.bulk_insert(collection, data, *args, **kwargs)

    def bulk_update(
        self,
        collection: str,
        filters: dict,
        update_data: list[dict] | dict,
        upsert: bool = False,
        *args,
        **kwargs,
    ) -> int:
        """Update multiple documents in a collection

        Args:
            collection (str): Name of the collection to update
            filters (dict): Query filters to select documents
            update_data (list[dict] | dict): List of update operations or new field values
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
            collection,
            filters,
            update_data,
            upsert,
            *args,
            **kwargs,
        )

    def bulk_delete(
        self, collection: str, filters: dict | list, *args, **kwargs
    ) -> int:
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
        return self.client.bulk_delete(collection, filters, *args, **kwargs)

    def _init_component_factory(
        self, *args, **kwargs
    ) -> abstract.NoSQLStoreComponentFactory:
        """Initialize the component factory based on configured framework"""
        framework = self.config.framework or DEFAULT_NOSQL_FRAMEWORK

        # Handle both string and enum types

        if isinstance(framework, configurations.Framework):
            framework_str = framework.value
        else:
            framework_str = str(framework)

        if framework_str not in adapters.adapter_routers:
            raise ValueError(f"Doesn't support framework: {framework_str}")

        return adapters.adapter_routers[framework_str](self.config, *args, **kwargs)
