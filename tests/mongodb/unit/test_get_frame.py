import polars
import pytest

collection = "test_df_collection"


class TestGetFrame:
    def test_get_frame_empty_collection(self, mongodb_store):
        # Test retrieving a frame from an empty collection
        df: polars.DataFrame = mongodb_store.get_frame("non_existent_collection")
        # ic(df)
        assert df.is_empty(), "DataFrame should be empty for a non-existent collection"

    @pytest.mark.collection(collection)
    def test_get_frame_with_data(self, mongodb_store):
        # Insert sample data into the collection
        sample_data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
            {"name": "Charlie", "age": 35},
        ]
        mongodb_store.bulk_insert(collection, sample_data)

        # Retrieve the data as a DataFrame
        df: polars.DataFrame = mongodb_store.get_frame(collection)

        # Validate the DataFrame contents
        assert not df.is_empty(), "DataFrame should not be empty"
        assert len(df) == 3, "DataFrame should contain 3 records"
        assert set(df.columns) == {"_id", "name", "age"}, (
            "DataFrame should have correct columns"
        )
        assert df["name"].to_list() == ["Alice", "Bob", "Charlie"], (
            "Names should match inserted data"
        )
        assert df["age"].to_list() == [30, 25, 35], "Ages should match inserted data"
