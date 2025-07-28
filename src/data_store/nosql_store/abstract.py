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

    def load_data(self) -> pl.DataFrame:
        """Load data from the NoSQL database."""
        return self._load_data()

    @abc.abstractmethod
    def _load_data(self) -> pl.DataFrame:
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
