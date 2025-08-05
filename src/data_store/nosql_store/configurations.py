import enum

import pydantic as pdt
import pydantic_settings as pdts


class Framework(enum.StrEnum):
    MONGODB = "mongodb"
    COUCHDB = "couchdb"
    DYNAMODB = "dynamodb"


class NoSQLConnection(pdt.BaseModel):
    uri: str | None = pdt.Field(
        default=None,
        description="Complete connection URI. If provided, individual connection components will be ignored.",
    )
    host: str | None = pdt.Field(
        default=None,
        description="Database host address. Required if URI is not provided.",
    )
    port: int | None = pdt.Field(
        default=None,
        description="Database port number. Uses default port if not specified.",
    )
    username: str | None = pdt.Field(
        default=None, description="Username for database authentication."
    )
    password: str | None = pdt.Field(
        default=None, description="Password for database authentication."
    )
    database: str | None = pdt.Field(
        default=None, description="Default database name to connect to."
    )
    auth_source: str | None = pdt.Field(
        default=None, description="Authentication database name (MongoDB specific)."
    )
    ssl: bool | None = pdt.Field(
        default=False, description="Enable SSL/TLS connection encryption."
    )
    connection_timeout: int = pdt.Field(
        default=30,
        description="Connection timeout in seconds. Default is 30 seconds.",
    )

    @pdt.model_validator(mode="after")
    def validate_connection(self):
        """Validate that either URI is provided or host/port combination"""
        if not self.uri and not self.host:
            raise ValueError("Either 'uri' or 'host' must be provided")
        return self

    @pdt.computed_field
    @property
    def connection_uri(self) -> str:
        """Build URI from components if uri is not provided"""
        if self.uri:
            return self.uri

        if not self.host:
            raise ValueError("Host is required to build URI")

        # Build URI from components
        scheme = "mongodb+srv" if self.ssl else "mongodb"

        # Handle authentication
        auth_part = ""
        if self.username:
            if self.password:
                auth_part = f"{self.username}:{self.password}@"
            else:
                auth_part = f"{self.username}@"

        # Handle port
        port_part = f":{self.port}" if self.port else ""

        # Build base URI
        uri = f"{scheme}://{auth_part}{self.host}{port_part}"

        # Add database if provided
        if self.database:
            uri += f"/{self.database}"

        # Add auth source as query parameter if provided
        query_params = []
        if self.auth_source:
            query_params.append(f"authSource={self.auth_source}")

        if query_params:
            uri += "?" + "&".join(query_params)

        return uri


class NoSQLConfiguration(pdts.BaseSettings):
    framework: str | Framework = pdt.Field(
        default=Framework.MONGODB,
        description="NoSQL database framework to use (mongodb, couchdb, dynamodb).",
    )
    connection: NoSQLConnection = pdt.Field(
        description="Database connection configuration settings."
    )

    model_config = pdts.SettingsConfigDict(extra="allow", use_enum_values=True)
