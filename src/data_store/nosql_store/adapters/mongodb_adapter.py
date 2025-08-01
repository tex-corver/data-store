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

    def _load_data(
        self,
        database: str,
        collection: str,
        fields: list[str],
        date_field: str | None,
        start_date: str | None,
        end_date: str | None,
        limit: int | None,
        date_format: str = "%Y-%m-%d",
        *args,
        **kwargs,
    ) -> pl.DataFrame:
        # TODO: Handle multiple connection
        try:
            import pymongo  # noqa: PLC0415
        except ImportError as e:
            raise ImportError(
                "The 'pymongo' package is required to use the MongoDB client. "
                "Please install it with 'pip install pymongo'."
            ) from e

        client = pymongo.MongoClient(self.config.connection.uri)
        db = client[database]
        db_collection = db[collection]

        query_filter = {}
        projection = None

        if date_field and (start_date or end_date):
            date_query = {}
            if start_date:
                start_dt = datetime.datetime.strptime(start_date, date_format)
                date_query["$gte"] = start_dt
            if end_date:
                end_dt = datetime.datetime.strptime(end_date, date_format)
                date_query["$lte"] = end_dt
            query_filter[date_field] = date_query

        # projection:
        if fields:
            projection = dict.fromkeys(fields, 1)
            projection["_id"] = 0

        # If user pass extend kargs
        if kwargs:
            query_filter.update(kwargs)

        cursor = db_collection.find(filter=query_filter, projection=projection)
        if limit:
            cursor = cursor.limit(limit)

        return pl.DataFrame(list(cursor))


class NoSQLComponentFactory(abstract.NoSQLComponentFactory):
    def __init__(self, config):
        super().__init__(config=config)

    def _create_client(self) -> abstract.NoSQLClient:
        return NoSQLStoreClient(config=self.config)
