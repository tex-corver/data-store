import pandas as pd
import polars as pl
import pytest

from data_store.nosql_store import models

collection = "test_df_collection"


@pytest.fixture(params=["polars", "pandas"])
def dataframe_type(request):
    """Fixture to parametrize tests with different DataFrame types."""
    return request.param


class TestGetFrame:
    def test_get_frame_empty_collection(self, mongodb_store, dataframe_type):
        # Test retrieving a frame from an empty collection
        data: models.DataFrame = mongodb_store.get_frame(
            "non_existent_collection", data_type=dataframe_type
        )

        # Check that the returned data_type matches
        assert data.data_type == dataframe_type, f"Data type should be {dataframe_type}"

        # Validate DataFrame is empty based on type
        if dataframe_type == "polars":
            assert data.data.is_empty(), (  # type: ignore
                "Polars DataFrame should be empty for a non-existent collection"
            )
        else:  # pandas
            assert data.data.empty, (  # type: ignore
                "Pandas DataFrame should be empty for a non-existent collection"
            )

    @pytest.mark.collection(collection)
    def test_get_frame_with_data(self, mongodb_store, dataframe_type):
        # Insert sample data into the collection
        sample_data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
            {"name": "Charlie", "age": 35},
        ]
        mongodb_store.bulk_insert(collection, sample_data)

        # Retrieve the data as a DataFrame
        data: models.DataFrame = mongodb_store.get_frame(
            collection, data_type=dataframe_type
        )

        # Check that the returned data_type matches
        assert data.data_type == dataframe_type, f"Data type should be {dataframe_type}"

        # Validate the DataFrame contents based on type
        if dataframe_type == "polars":
            polars_df: pl.DataFrame = data.data  # type: ignore
            assert not polars_df.is_empty(), "Polars DataFrame should not be empty"
            assert len(polars_df) == 3, "DataFrame should contain 3 records"
            assert set(polars_df.columns) == {"_id", "name", "age"}, (
                "DataFrame should have correct columns"
            )
            assert polars_df["name"].to_list() == ["Alice", "Bob", "Charlie"], (
                "Names should match inserted data"
            )
            assert polars_df["age"].to_list() == [30, 25, 35], (
                "Ages should match inserted data"
            )
        else:  # pandas
            pandas_df: pd.DataFrame = data.data  # type: ignore
            assert not pandas_df.empty, "Pandas DataFrame should not be empty"
            assert len(pandas_df) == 3, "DataFrame should contain 3 records"
            assert set(pandas_df.columns) == {"_id", "name", "age"}, (
                "DataFrame should have correct columns"
            )
            assert pandas_df["name"].tolist() == ["Alice", "Bob", "Charlie"], (
                "Names should match inserted data"
            )
            assert pandas_df["age"].tolist() == [30, 25, 35], (
                "Ages should match inserted data"
            )
