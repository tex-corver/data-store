import abc
from typing import Any

import polars as pl

from data_store.nosql_store import configurations


class NoSQLClient(abc.ABC):
    def __init__(
        self, config: dict[str, Any] | configurations.NoSQLConfiguration
    ) -> None:
        if isinstance(config, dict):
            config = configurations.NoSQLConfiguration(**config)
        self.config = config

    def load_data(
        self,
        database: str,
        collection: str,
        fields: list[str] | None,
        date_field: str | None,
        start_date: str | None,
        end_date: str | None,
        limit: int | None,
        date_format: str = "%Y-%m-%d",
        *args,
        **kwargs,
    ) -> pl.DataFrame:
        """Load data from the NoSQL database."""
        return self._load_data(
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

    @abc.abstractmethod
    def _load_data(
        self,
        database: str,
        collection: str,
        fields: list[str] | None,
        date_field: str | None,
        start_date: str | None,
        end_date: str | None,
        limit: int | None,
        date_format: str = "%Y-%m-%d",
        *args,
        **kwargs,
    ) -> pl.DataFrame:
        """Abstract method to load data from the NoSQL database."""
        raise NotImplementedError


class NoSQLComponentFactory(abc.ABC):
    def __init__(
        self, config: dict[str, Any] | configurations.NoSQLConfiguration
    ) -> None:
        if isinstance(config, dict):
            config = configurations.NoSQLConfiguration(**config)
        self.config = config

    def create_client(self, *args, **kwargs) -> NoSQLClient:
        """Create a NoSQL client instance."""
        client = self._create_client(*args, **kwargs)
        return client

    def _create_client(self, *args, **kwargs) -> NoSQLClient:
        """Abstract method to create a NoSQL client instance."""
        raise NotImplementedError
