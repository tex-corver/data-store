import datetime
from typing import Any

import polars as pl

from data_store.nosql_store import abstract, configurations


class NoSQLStoreClient(abstract.NoSQLClient):
    config: configurations.NoSQLConfiguration

    def __init__(
        self, config: dict[str, Any] | configurations.NoSQLConfiguration
    ) -> None:
        super().__init__(config)

    def _load_data(self) -> pl.DataFrame:
        # TODO: Handle multiple connection
        try:
            import pymongo  # noqa: PLC0415
        except ImportError as e:
            raise ImportError(
                "The 'pymongo' package is required to use the MongoDB client. "
                "Please install it with 'pip install pymongo'."
            ) from e

        connection_config = self.config.connection
        query_config = self.config.query

        client = pymongo.MongoClient(connection_config.uri)
        db = client[connection_config.database]
        collection = db[connection_config.collection]

        query_filter = {}
        projection = None

        if query_config.date_field and (
            query_config.start_date or query_config.end_date
        ):
            date_query = {}
            if query_config.start_date:
                start_dt = datetime.datetime.strptime(
                    query_config.start_date, query_config.date_format
                )
                date_query["$gte"] = start_dt
            if query_config.end_date:
                end_dt = datetime.datetime.strptime(
                    query_config.end_date, query_config.date_format
                )
                date_query["$lte"] = end_dt
            query_filter[query_config.date_field] = date_query

        # projection:
        if query_config.fields:
            projection = dict.fromkeys(query_config.fields, 1)
            projection["_id"] = 0

        cursor = collection.find(filter=query_filter, projection=projection)
        if query_config.limit:
            cursor = cursor.limit(query_config.limit)

        return pl.DataFrame(list(cursor))


class NoSQLComponentFactory(abstract.NoSQLComponentFactory):
    def __init__(self, config):
        super().__init__(config=config)

    def _create_client(self) -> abstract.NoSQLClient:
        return NoSQLStoreClient(config=self.config)
