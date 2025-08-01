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
        """Establish database connection"""
        return self._connect(**config)

    def close(self):
        """Close connection"""
        return self._close()

    def insert(self, collection: str, data: dict) -> str:
        """Insert a document into a collection"""
        return self._insert(collection=collection, data=data)

    def find(
        self,
        collection: str,
        filters: dict | None = None,
        projections: list[str] | None = None,
        skip: int = 0,
        limit: int = 0,
    ) -> list:
        """Find documents in a collection"""
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
        """Update documents in a collection"""
        return self._update(
            collection=collection,
            filters=filters,
            update_data=update_data,
            upsert=upsert,
        )

    def delete(self, collection: str, filters: dict) -> int:
        """Delete documents from a collection"""
        return self._delete(collection=collection, filters=filters)

    def bulk_insert(self, collection: str, data: list[dict]) -> str:
        """Insert multiple documents into a collection"""
        return self._bulk_insert(collection=collection, data=data)

    def bulk_update(
        self,
        collection: str,
        filters: dict,
        update_data: list[dict],
        upsert: bool = False,
    ) -> int:
        """Update multiple documents in a collection"""
        return self._bulk_update(
            collection=collection,
            filters=filters,
            update_data=update_data,
            upsert=upsert,
        )

    def bulk_delete(self, collection: str, filters: dict | list) -> int:
        """Delete multiple documents from a collection"""
        return self._bulk_delete(collection=collection, filters=filters)

    @abc.abstractmethod
    def _connect(self, **config):
        """Abstract method to establish database connection"""
        raise NotImplementedError

    @abc.abstractmethod
    def _close(self):
        """Abstract method to close connection"""
        raise NotImplementedError

    @abc.abstractmethod
    def _insert(self, collection: str, data: dict) -> str:
        """Abstract method to insert a document"""
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
        """Abstract method to find documents"""
        raise NotImplementedError

    @abc.abstractmethod
    def _update(
        self, collection: str, filters: dict, update_data: dict, upsert: bool = False
    ) -> int:
        """Abstract method to update documents"""
        raise NotImplementedError

    @abc.abstractmethod
    def _delete(self, collection: str, filters: dict) -> int:
        """Abstract method to delete documents"""
        raise NotImplementedError

    @abc.abstractmethod
    def _bulk_insert(self, collection: str, data: list[dict]) -> str:
        """Abstract method to bulk insert documents"""
        raise NotImplementedError

    @abc.abstractmethod
    def _bulk_update(
        self,
        collection: str,
        filters: dict,
        update_data: list[dict],
        upsert: bool = False,
    ) -> int:
        """Abstract method to bulk update documents"""
        raise NotImplementedError

    @abc.abstractmethod
    def _bulk_delete(self, collection: str, filters: dict | list) -> int:
        """Abstract method to bulk delete documents"""
        raise NotImplementedError


class NoSQLStoreComponentFactory(abc.ABC):
    def __init__(
        self, config: dict[str, Any] | configurations.NoSQLConfiguration
    ) -> None:
        if isinstance(config, dict):
            config = configurations.NoSQLConfiguration(**config)
        self.config = config

    def create_client(self, *args, **kwargs) -> NoSQLStore:
        client = self._create_client(*args, **kwargs)
        return client

    @abc.abstractmethod
    def _create_client(self, *args, **kwargs) -> NoSQLStore:
        raise NotImplementedError
