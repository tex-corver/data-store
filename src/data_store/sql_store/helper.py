import datetime
from typing import Literal


def format_date(date_value: str, date_format: str) -> str:
    """Formats a date value according to the specified date format."""
    if isinstance(date_value, datetime.datetime):
        return date_value.strftime(date_format)
    if isinstance(date_value, str):
        parsed_date = datetime.datetime.strptime(date_value, date_format).date()
        return parsed_date.strftime(date_format)
    return date_value


def build_sql_query(
    table,
    db_type: Literal["mysql", "sqlite", "postgres"] = "sqlite",
    columns: list[str] | None = None,
    date_column: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    date_format: str = "%Y-%m-%d",
    limit: int | None = None,
) -> str:
    """Builds a SQL query string based on the provided parameters.

    Args:
        table (str): The table to query from.
        db_type (DataLocationType): The type of database.
        columns (list[str] | None): Optional list of columns to select.
            If None, all columns are selected.
        date_column (str | None): Optional date column to filter data by date.
        start_date (str | None): Optional start date to filter data.
            Only used if date_column is set.
        end_date (str | None): Optional end date to filter data.
            Only used if date_column is set.
        date_format (str): Date format to use for date filtering. Defaults to '%Y-%m-%d'.
        limit (int | None): Optional limit on the number of rows to return from the query.
            If None, no limit is applied.
    """
    try:
        import pypika  # noqa: PLC0415
    except ImportError as e:
        raise ImportError(
            "The 'pypika' package is required to use the SQL client. "
            "Please install it with 'pip install nodelib[sql]'."
        ) from e

    match db_type:
        case "mysql":
            query_cls = pypika.MySQLQuery
        case "sqlite":
            query_cls = pypika.SQLLiteQuery
        case "postgres":
            query_cls = pypika.PostgreSQLQuery
        case _:
            query_cls = pypika.Query

    query = query_cls.from_(table).select(*columns if columns else "*")
    if date_column:
        if start_date:
            formatted_start = format_date(start_date, date_format)
            query = query.where(pypika.Field(date_column) >= formatted_start)
        if end_date:
            formatted_end = format_date(end_date, date_format)
            query = query.where(pypika.Field(date_column) <= formatted_end)
    if limit:
        query = query.limit(limit)
    return str(query)
