from typing import Any

import polars as pl
import utils

from data_store.nosql_store import abstract, adapters, configurations

DEFAULT_NOSQL_FRAMEWORK = "mongodb"


__all__ = ["NoSQLStore"]


class NoSQLStore:
    """A class representing a NoSQL data store."""

    config: configurations.NoSQLConfiguration
    component_factory: abstract.NoSQLComponentFactory

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        config = config or utils.get_config().get("data_store", {}).get("nosql_store")
        if config is None:
            raise ValueError("Configuration not found")
        self.config = configurations.NoSQLConfiguration(**config)
        self.component_factory = self.__init_component_factory()

    @property
    def client(self) -> abstract.NoSQLClient:
        if not hasattr(self, "_client"):
            self._client = self.component_factory.create_client()
        return self._client

    def load_data(
        self,
        database: str,
        collection: str,
        fields: list[str] | None = None,
        date_field: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int | None = None,
        date_format: str = "%Y-%m-%d",
        *args,
        **kwargs,
    ) -> pl.DataFrame:
        """Load data from the NoSQL store.

        Args:
            database (str): Name of the database.
            collection (str): Name of the collection.
            fields (list[str]): List of field names to include in the output.
            date_field (str, optional): Field storing date values.
            start_date (str, optional): Start date for filtering.
            end_date (str, optional): End date for filtering.
            limit (int, optional): Maximum number of documents to return.
            date_format (str, optional): Date format to use for date filtering. Defaults to "%Y-%m-%d".
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Any: The result from the data store client's load_data method.
        """
        return self.client.load_data(
            database=database,
            collection=collection,
            fields=fields,
            date_field=date_field,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            date_format=date_format,
            *args,
            **kwargs,
        )

    def __init_component_factory(self) -> abstract.NoSQLComponentFactory:
        """Initialize the component factory based on the configuration."""
        framework = self.config.framework or DEFAULT_NOSQL_FRAMEWORK

        if framework not in adapters.adapter_routers:
            raise ValueError(f"Unsupported NoSQL framework: {framework}")
        return adapters.adapter_routers[framework](self.config)
