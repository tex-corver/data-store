import abc
import logging
from typing import Any, Generator

import utils

from data_store import configurations, models

logger = logging.getLogger(__file__)


class ObjectStoreClient(abc.ABC):
    def __init__(
        self, config: dict[str, Any] | configurations.ObjectStoreConfiguration
    ) -> None:
        if isinstance(config, dict):
            config = configurations.ObjectStoreConfiguration(**config)
        self.config = config
        self.root_bucket = self.config.root_bucket

    def list_buckets(self, *args, **kwargs) -> Generator[models.Bucket, None, None]:
        buckets = self._list_buckets(*args, **kwargs)
        for bucket in buckets:
            yield bucket

    def download_file(
        self,
        key: str,
        file_path: str,
        bucket: str = None,
        *args,
        **kwargs,
    ):
        if bucket is None:
            bucket = self.root_bucket
        self._download_object(
            key=key,
            file_path=file_path,
            bucket=bucket,
            *args,
            **kwargs,
        )

    def upload_file(
        self,
        file_path: str,
        key: str,
        bucket: str = None,
        *args,
        **kwargs,
    ):
        bucket = bucket or self.root_bucket
        self._upload_object(
            file_path=file_path,
            key=key,
            bucket=bucket,
            *args,
            **kwargs,
        )

    def delete_object(
        self,
        key: str,
        bucket: str = None,
        version: str = None,
        *args,
        **kwargs,
    ):
        bucket = bucket or self.root_bucket
        self._delete_object(key=key, bucket=bucket, version=version, *args, **kwargs)

    def download_object(
        self,
        key: str,
        file_path: str = None,
        bucket: str = None,
        *args,
        **kwargs,
    ) -> Any:
        bucket = bucket or self.root_bucket
        file_path = file_path or key
        return self._download_object(
            key=key, file_path=file_path, bucket=bucket, *args, **kwargs
        )

    def get_object(
        self,
        key: str,
        bucket: str = None,
        *args,
        **kwargs,
    ):
        bucket = bucket or self.root_bucket
        s3_object = self._get_object(key=key, bucket=bucket, *args, **kwargs)
        return s3_object

    def list_objects(
        self,
        bucket: str = None,
        prefix: str = None,
        *args,
        **kwargs,
    ) -> Generator[models.Object, None, None]:
        bucket = bucket or self.root_bucket
        objects = self._list_objects(bucket=bucket, prefix=prefix, *args, **kwargs)
        for s3_object in objects:
            yield s3_object

    def upload_object(
        self,
        file_path: str,
        key: str,
        bucket: str = None,
        *args,
        **kwargs,
    ):
        bucket = bucket or self.root_bucket
        return self._upload_object(
            file_path=file_path,
            key=key,
            bucket=bucket,
            *args,
            **kwargs,
        )

    def put_object_v2(
        self,
        data: bytes,
        key: str,
        bucket: str | None = None,
        *args,
        **kwargs,
    ):
        bucket = bucket or self.root_bucket
        return self._put_object_v2(
            data=data,
            key=key,
            bucket=bucket,
            *args,
            **kwargs,
        )

    def copy_object(
        self,
        src_object: str,
        dst_object: str,
        src_bucket: str = None,
        dst_bucket: str = None,
        *args,
        **kwargs,
    ):
        src_bucket = src_bucket or self.root_bucket
        dst_bucket = dst_bucket or self.root_bucket
        return self._copy_object(
            src_object=src_object,
            dst_object=dst_object,
            src_bucket=src_bucket,
            dst_bucket=dst_bucket,
            *args,
            **kwargs,
        )

    @abc.abstractmethod
    def _list_buckets(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def _delete_object(self, key: str, bucket: str, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def _download_object(
        self,
        key: str,
        file_path: str,
        bucket: str,
        *args,
        **kwargs,
    ):
        raise NotImplementedError

    @abc.abstractmethod
    def _get_object(self, key: str, bucket: str, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def _upload_object(
        self,
        file_path: str,
        key: str,
        bucket: str,
        *args,
        **kwargs,
    ):
        raise NotImplementedError

    @abc.abstractmethod
    def _list_objects(self, bucket: str, prefix: str, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def _copy_object(
        self,
        src_object: str,
        dst_object: str,
        src_bucket: str,
        dst_bucket: str,
        *args,
        **kwargs,
    ):
        raise NotImplementedError

    @abc.abstractmethod
    def _put_object_v2(
        self,
        data: bytes,
        key: str,
        bucket: str | None = None,
        length: int = -1,
        *args,
        **kwargs,
    ):
        raise NotImplementedError


class ObjectStoreComponentFactory(abc.ABC):
    def __init__(
        self, config: dict[str, Any] | configurations.ObjectStoreConfiguration
    ) -> None:
        if isinstance(config, dict):
            config = configurations.ObjectStoreConfiguration(**config)
        self.config = config

    def create_client(self, *args, **kwargs) -> ObjectStoreClient:
        client = self._create_client(*args, **kwargs)
        return client

    @abc.abstractmethod
    def _create_client(self, *args, **kwargs) -> ObjectStoreClient:
        raise NotImplementedError
