import abc
import logging
from typing import Any

import utils

from data_store.nosql_store import configurations, models

logger = logging.getLogger(__file__)


class NoSQLStore(abc.ABC):
    def __init__(
        self, config: dict[str, Any] | configurations.NoSQLConfiguration
    ) -> None:
        if isinstance(config, dict):
            config = configurations.NoSQLConfiguration(**config)
        self.config = config

    def connect(self, **config):
        """Establish database connection

        Args:
            **config: Additional connection configuration parameters

        Returns:
            Connection: Database connection object

        Raises:
            RuntimeError: If connection establishment fails
        """
        return self._connect(**config)

    def close(self):
        """Close connection

        Raises:
            RuntimeError: If connection closure fails
        """
        return self._close()

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
        """
        return self._insert(collection=collection, data=data)

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
        return self._find(
            collection=collection,
            filters=filters,
            projections=projections,
            skip=skip,
            limit=limit,
        )

    def update(
        self, collection: str, filters: dict, update_data: dict, upsert: bool = False
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
        """
        return self._update(
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
        """
        return self._delete(collection=collection, filters=filters)

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
        """
        return self._bulk_insert(collection=collection, data=data)

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
        """
        return self._bulk_update(
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
        """
        return self._bulk_delete(collection=collection, filters=filters)

    @abc.abstractmethod
    def _connect(self):
        """Abstract method to establish database connection

        Returns:
            Connection: Database connection object

        Raises:
            RuntimeError: If connection establishment fails
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _close(self):
        """Abstract method to close connection

        Raises:
            RuntimeError: If connection closure fails
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _insert(self, collection: str, data: dict) -> str:
        """Abstract method to insert a document

        Args:
            collection (str): Name of the collection to insert into
            data (dict): Document data to insert

        Returns:
            str: ID of the inserted document

        Raises:
            ValueError: If collection name is empty or data is None
            RuntimeError: If database operation fails
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _find(
        self,
        collection: str,
        filters: dict | None = None,
        projections: list[str] | None = None,
        skip: int = 0,
        limit: int = 0,
    ) -> list:
        """Abstract method to find documents

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
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _update(
        self, collection: str, filters: dict, update_data: dict, upsert: bool = False
    ) -> int:
        """Abstract method to update documents

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
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _delete(self, collection: str, filters: dict) -> int:
        """Abstract method to delete documents

        Args:
            collection (str): Name of the collection to delete from
            filters (dict): Query filters to select documents

        Returns:
            int: Number of documents deleted

        Raises:
            ValueError: If collection name is empty or filters are None
            RuntimeError: If database operation fails
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _bulk_insert(self, collection: str, data: list[dict]) -> str:
        """Abstract method to bulk insert documents

        Args:
            collection (str): Name of the collection to insert into
            data (list[dict]): List of documents to insert

        Returns:
            str: String representation of count of inserted documents

        Raises:
            ValueError: If collection name is empty or data is None
            RuntimeError: If database operation fails
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _bulk_update(
        self,
        collection: str,
        filters: dict,
        update_data: list[dict],
        upsert: bool = False,
    ) -> int:
        """Abstract method to bulk update documents

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
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _bulk_delete(self, collection: str, filters: dict | list) -> int:
        """Abstract method to bulk delete documents

        Args:
            collection (str): Name of the collection to delete from
            filters (dict | list): Query filter(s) to select documents

        Returns:
            int: Total number of documents deleted

        Raises:
            ValueError: If collection name is empty or filters are None
            RuntimeError: If database operation fails
        """
        raise NotImplementedError


class NoSQLStoreComponentFactory(abc.ABC):
    def __init__(
        self, config: dict[str, Any] | configurations.NoSQLConfiguration
    ) -> None:
        if isinstance(config, dict):
            config = configurations.NoSQLConfiguration(**config)
        self.config = config

    def create_client(self, *args, **kwargs) -> NoSQLStore:
        """Create a NoSQL store client instance

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Returns:
            NoSQLStore: Configured NoSQL store client instance

        Raises:
            RuntimeError: If client creation fails
        """
        client = self._create_client(*args, **kwargs)
        return client

    @abc.abstractmethod
    def _create_client(self, *args, **kwargs) -> NoSQLStore:
        """Abstract method to create a NoSQL store client instance

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Returns:
            NoSQLStore: Configured NoSQL store client instance

        Raises:
            RuntimeError: If client creation fails
        """
        raise NotImplementedError
