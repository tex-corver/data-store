import abc
from typing import Any

import polars as pl

from data_store.sql_store import configurations


class SQLClient(abc.ABC):
    def __init__(
        self, config: dict[str, Any] | configurations.SQLConfiguration
    ) -> None:
        if isinstance(config, dict):
            config = configurations.SQLConfiguration(**config)
        self.config = config

    def load_data(self, *args, **kwargs) -> pl.DataFrame:
        """Load data from the SQL database."""
        return self._load_data(*args, **kwargs)

    @abc.abstractmethod
    def _load_data(self, *args, **kwargs) -> pl.DataFrame:
        """Abstract method to load data from the SQL database."""
        raise NotImplementedError


class SQLComponentFactory(abc.ABC):
    def __init__(
        self, config: dict[str, Any] | configurations.SQLConfiguration
    ) -> None:
        if isinstance(config, dict):
            config = configurations.SQLConfiguration(**config)
        self.config = config

    def create_client(self, *args, **kwargs) -> SQLClient:
        """Create a SQL client instance."""
        client = self._create_client(*args, **kwargs)
        return client

    @abc.abstractmethod
    def _create_client(self, *args, **kwargs) -> SQLClient:
        """Abstract method to create a SQL client instance."""
        raise NotImplementedError
