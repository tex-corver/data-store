from typing import Any

import utils

from data_store.sql_store import abstract, configurations, helper

logger = utils.get_logger()


class SQLStoreClient(abstract.SQLClient):
    config: configurations.SQLConfiguration

    def __init__(
        self, config: dict[str, Any] | configurations.SQLConfiguration
    ) -> None:
        super().__init__(config)

    def _load_data(self) -> Any:
        try:
            import connectorx as cx
        except ImportError as e:
            raise ImportError(
                "The 'connectorx' package is required to use the SQL client. "
                "Please install it with 'pip install connectorx'."
            ) from e
        query = helper.build_sql_query(
            table=self.config.query.table,
            db_type="mysql",
            columns=self.config.query.columns,
            date_column=self.config.query.date_column,
            start_date=self.config.query.start_date,
            end_date=self.config.query.end_date,
            date_format=self.config.query.date_format,
            limit=self.config.query.limit,
        )
        try:
            data = cx.read_sql(
                self.config.connection.uri,
                query,
                return_type="polars",
            )
        except Exception as e:
            logger.error(
                f"Failed to load data from {self.config.connection.uri} using query: {query},Error: {e}"
            )
            raise ValueError(
                f"Failed to load data from {self.config.connection.uri} using query: {query}"
            ) from e
        return data


class SQLComponentFactory(abstract.SQLComponentFactory):
    def __init__(self, config: dict[str, Any] | Any) -> None:
        super().__init__(config)

    def _create_client(self) -> abstract.SQLClient:
        return SQLStoreClient(config=self.config)
