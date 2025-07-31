import polars as pl

import data_store


class TestObjectStore:
    def test_init(self):
        store = data_store.ObjectStore()


class TestSQLStore:
    def test_init(self):
        store = data_store.SQLStore()
        assert store.config is not None
        data = store.load_data()
        assert data is not None
        assert isinstance(data, pl.DataFrame)
