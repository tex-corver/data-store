import dataclasses
from datetime import datetime
from typing import IO

@dataclasses.dataclass(frozen=True)
class Bucket:
    """_summary_
    """

    name: str
    created_time: datetime


@dataclasses.dataclass(frozen=True)
class ObjectMetadata:
    """_summary_
    """

    key: str
    updated_time: datetime
    size: int


@dataclasses.dataclass(frozen=True)
class Object:
    """_summary_
    """

    body: IO[bytes]
    updated_time: datetime

