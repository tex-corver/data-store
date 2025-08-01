import pydantic
from typing import Optional

import enum


class Framework(enum.Enum):
    MINIO = "minio"
    BOTO3 = "boto3"


class ObjectStoreConnectionConfiguration(pydantic.BaseModel):
    endpoint: str
    access_key: str
    secret_key: str
    secure: Optional[bool] = False


class ObjectStoreConfiguration(pydantic.BaseModel):
    framework: Optional[str | Framework] = pydantic.Field(default=Framework.MINIO)
    root_bucket: str
    connection: ObjectStoreConnectionConfiguration
