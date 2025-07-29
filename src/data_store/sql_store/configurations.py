import enum

import pydantic as pdt
import pydantic_settings as pdts


class Framework(enum.StrEnum):
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    SQLITE = "sqlite"


class SQLConfiguration(pdts.BaseSettings):
    """Configuration for SQL data store."""

    framework: Framework = pdt.Field(
        default=Framework.SQLITE, description="Framework used for the SQL data store."
    )

    connection: "SQLConnectionConfiguration" = pdt.Field(
        description="Connection configuration for the SQL data store.",
    )
    query: "SQLQueryConfiguration" = pdt.Field(
        default=None,
        description="Query configuration for the SQL data store.",
    )


class SQLConnectionConfiguration(pdt.BaseModel):
    """Connection configuration for SQL data store."""

    uri: str = pdt.Field(description="URI of the SQL database.")


class SQLQueryConfiguration(pdt.BaseModel):
    """Configuration for SQL queries."""

    table: str = pdt.Field(
        ..., description="List of tables to query from the database."
    )
    columns: list[str] | None = pdt.Field(
        default=None,
        description="Optional list of columns to select from the tables. If None, all columns are selected.",
    )
    date_column: str | None = pdt.Field(
        default=None, description="Optional date column to filter data by date."
    )
    start_date: str | None = pdt.Field(
        default=None,
        description="Optional start date to filter data. Only used if date_column is set.",
    )
    end_date: str | None = pdt.Field(
        default=None,
        description="Optional end date to filter data. Only used if date_column is set.",
    )
    date_format: str = pdt.Field(
        default="%Y-%m-%d",
        description="Date format to use for date filtering. Defaults to '%Y-%m-%d'.",
    )
    limit: int | None = pdt.Field(
        default=None,
        description="Optional limit on the number of rows to return from the query. If None, no limit is applied.",
    )
