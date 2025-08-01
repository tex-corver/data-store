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

    def connect(self, **config):
        """Establish database connection"""
        return self.client.connect(**config)

    def close(self):
        """Close database connection"""
        return self.client.close()

    def insert(self, collection: str, data: dict) -> str:
        """Insert a document into a collection"""
        return self.client.insert(collection=collection, data=data)

    def find(
        self,
        collection: str,
        filters: dict | None = None,
        projections: list[str] | None = None,
        skip: int = 0,
        limit: int = 0,
    ) -> list:
        """Find documents in a collection"""
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
        """Update documents in a collection"""
        return self.client.update(
            collection=collection,
            filters=filters,
            update_data=update_data,
            upsert=upsert,
        )

    def delete(self, collection: str, filters: dict) -> int:
        """Delete documents from a collection"""
        return self.client.delete(collection=collection, filters=filters)

    def bulk_insert(self, collection: str, data: list[dict]) -> str:
        """Insert multiple documents into a collection"""
        return self.client.bulk_insert(collection=collection, data=data)

    def bulk_update(
        self,
        collection: str,
        filters: dict,
        update_data: list[dict],
        upsert: bool = False,
    ) -> int:
        """Update multiple documents in a collection"""
        return self.client.bulk_update(
            collection=collection,
            filters=filters,
            update_data=update_data,
            upsert=upsert,
        )

    def bulk_delete(self, collection: str, filters: dict | list) -> int:
        """Delete multiple documents from a collection"""
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
