import enum

import pydantic as pdt
import pydantic_settings as pdts


class Framework(enum.StrEnum):
    MONGODB = "mongodb"


class NoSQLQueryConfiguration(pdt.BaseModel):
    """Configuration for NoSQL queries."""

    database: str = pdt.Field(description="Name of the MongoDB database.")
    collection: str = pdt.Field(
        description="Name of the collection to query from the database."
    )

    fields: list[str] | None = pdt.Field(
        default=None,
        description="Projection: list of field names to include in the output (if None, all fields are returned).",
    )
    date_field: str | None = pdt.Field(
        default=None, description="Field storing date values."
    )
    start_date: str | None = pdt.Field(
        default=None, description="Start date for filtering."
    )
    end_date: str | None = pdt.Field(
        default=None, description="End date for filtering."
    )
    date_format: str = pdt.Field(
        default="%Y-%m-%d",
        description="Date format to use for date filtering. Defaults to '%Y-%m-%d'.",
    )
    limit: int | None = pdt.Field(
        default=None, description="Maximum number of documents to return."
    )


class NoSQLConnectionConfiguration(pdt.BaseModel):
    """Connection configuration for NoSQL data store."""

    uri: str = pdt.Field(description="URI of the MongoDB database.")


class NoSQLConfiguration(pdts.BaseSettings):
    """Configuration for NoSQL data store."""

    framework: str | None = pdt.Field(
        default=None, description="Framework used for the NoSQL data store."
    )

    connection: NoSQLConnectionConfiguration = pdt.Field(
        description="Connection configuration for the NoSQL data store.",
    )
    query: NoSQLQueryConfiguration | None = pdt.Field(
        default=None,
        description="Example query configuration for the NoSQL data store.",
    )
