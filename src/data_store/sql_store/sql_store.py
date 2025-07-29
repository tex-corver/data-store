from typing import Any

import utils

from data_store.sql_store import abstract, adapters, configurations

DEFAULT_SQL_FRAMEWORK = "sqlite"


class SQLStore:
    """A class representing a SQL data store."""

    config: configurations.SQLConfiguration
    component_factory: abstract.SQLComponentFactory

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        config = config or utils.get_config().get("data_store", {}).get("sql_store")
        if config is None:
            raise ValueError("Configuration not found")
        self.config = configurations.SQLConfiguration(**config)
        self.component_factory = self.__init_component_factory()

    @property
    def client(self) -> abstract.SQLClient:
        if not hasattr(self, "_client"):
            self._client = self.component_factory.create_client()
        return self._client

    def load_data(self, *args, **kwargs) -> Any:
        """Load data from the SQL store."""
        return self.client.load_data(*args, **kwargs)

    def __init_component_factory(self) -> abstract.SQLComponentFactory:
        """Initialize the component factory based on the configuration."""
        framework = self.config.framework or DEFAULT_SQL_FRAMEWORK

        if framework not in adapters.adapter_routers:
            raise ValueError(f"Unsupported SQL framework: {framework}")
        return adapters.adapter_routers[framework](self.config)
