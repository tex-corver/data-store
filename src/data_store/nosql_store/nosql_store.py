from typing import Any

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

    def __init_component_factory(self) -> abstract.NoSQLComponentFactory:
        """Initialize the component factory based on the configuration."""
        framework = self.config.framework or DEFAULT_NOSQL_FRAMEWORK

        if framework not in adapters.adapter_routers:
            raise ValueError(f"Unsupported NoSQL framework: {framework}")
        return adapters.adapter_routers[framework](self.config)

    def load_data(self, *args, **kwargs) -> Any:
        """Load data from the NoSQL store."""
        return self.client.load_data(*args, **kwargs)
