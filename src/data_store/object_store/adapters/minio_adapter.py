import io
import tempfile
from typing import Any, Generator, Optional

import minio
import minio.commonconfig
import minio.datatypes
import urllib3.response
import utils
from icecream import ic

from data_store.object_store import abstract, configurations, models


def create_object_metadata(
    minio_object: minio.datatypes.Object,
    **kwargs,
) -> models.ObjectMetadata:
    metadata = models.ObjectMetadata(
        key=minio_object._object_name,
        updated_time=minio_object._last_modified,
        size=minio_object._size,
    )
    return metadata


def create_object(
    minio_response_object: urllib3.response.HTTPResponse, **kwargs
) -> models.Object:
    res = minio_response_object
    obj = models.Object(
        body=res.read(),
        updated_time=res.headers.get("Last-Modified"),
    )
    return obj


class ObjectStoreClient(abstract.ObjectStoreClient):
    config: configurations.ObjectStoreConfiguration

    def __init__(
        self,
        config: dict[str, Any] | configurations.ObjectStoreConfiguration,
    ) -> None:
        super().__init__(config)
        self._client = self._init_client()

    def _init_client(self) -> minio.Minio:
        connection_config = self.config.connection
        client = minio.Minio(
            endpoint=connection_config.endpoint,
            access_key=connection_config.access_key,
            secret_key=connection_config.secret_key,
            secure=connection_config.secure,
        )
        return client

    def _list_buckets(self) -> Generator[models.Bucket, None, None]:
        buckets = self._client.list_buckets()
        for bucket in buckets:
            yield models.Bucket(
                name=bucket._name,
                created_time=bucket._creation_date,
            )

    def _list_objects(
        self, bucket: str, prefix: str, *args, **kwargs
    ) -> Generator[models.ObjectMetadata, Any, None]:
        objects = self._client.list_objects(bucket, prefix=prefix, *args, **kwargs)
        for obj in objects:
            yield create_object_metadata(minio_object=obj)

    def _delete_object(
        self,
        key: str,
        bucket: str,
        version: str = None,
        *args,
        **kwargs,
    ):
        self._client.remove_object(
            bucket_name=bucket,
            object_name=key,
            version_id=version,
            *args,
            **kwargs,
        )

    def _download_object(
        self,
        key: str,
        file_path: str,
        bucket: str,
        *args,
        **kwargs,
    ):
        return self._client.fget_object(
            bucket_name=bucket,
            object_name=key,
            file_path=file_path,
            *args,
            **kwargs,
        )

    def _get_object(self, key: str, bucket: str, *args, **kwargs):
        response = None
        try:
            response = self._client.get_object(
                bucket_name=bucket, object_name=key, *args, **kwargs
            )
            obj = create_object(minio_response_object=response)
            return obj
        finally:
            if response:
                response.close()
                response.release_conn()

    def _upload_object(
        self,
        file_path: str,
        key: str,
        bucket: str,
        *args,
        **kwargs,
    ):
        res = self._client.fput_object(
            bucket_name=bucket,
            object_name=key,
            file_path=file_path,
            *args,
            **kwargs,
        )
        return res

    def _copy_object(
        self,
        src_object: str,
        dst_object: str,
        src_bucket: str = None,
        dst_bucket: str = None,
        *args,
        **kwargs,
    ):
        res = self._client.copy_object(
            bucket_name=dst_bucket,
            object_name=dst_object,
            source=minio.commonconfig.CopySource(
                bucket_name=src_bucket, object_name=src_object
            ),
        )
        return res

    def _put_object_v2(
        self,
        data: bytes,
        key: str,
        bucket: str,
        length: int = -1,
        *args,
        **kwargs,
    ):
        res = self._client.put_object(
            bucket_name=bucket,
            object_name=key,
            data=io.BytesIO(data),
            length=length,
            part_size=10 * 1024 * 1024,
            *args,
            **kwargs,
        )
        return res


class ObjectStoreComponentFactory(abstract.ObjectStoreComponentFactory):
    def __init__(self, config):
        super().__init__(config=config)

    def _create_client(self) -> ObjectStoreClient:
        return ObjectStoreClient(config=self.config)
