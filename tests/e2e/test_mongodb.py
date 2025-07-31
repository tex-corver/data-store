import polars as pl

import data_store


class TestNoSQLStoreClient:
    def test_init(self):
        store = data_store.NoSQLStore()
        assert store.config is not None
        data = store.load_data(
            database="test_simple_node",
            collection="products",
            fields=["name", "description", "price", "created_at"],
            date_field="created_at",
            start_date="2025-01-01",
            date_format="%Y-%m-%d",
            limit=10,
        )
        assert data is not None
        assert isinstance(data, pl.DataFrame)
