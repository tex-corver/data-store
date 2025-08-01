import logging
from collections.abc import Generator
from typing import Any

import utils
from icecream import ic

__all__ = ["ObjectStore"]
from data_store.object_store import abstract, adapters, configurations, models

logger = logging.getLogger(__file__)

DEFAULT_S3_FRAMEWORK = "minio"


class ObjectStore:
    config: configurations.ObjectStoreConfiguration
    component_factory: abstract.ObjectStoreComponentFactory
    client: abstract.ObjectStoreClient

    def __init__(self, config: dict[str, Any] = None):
        config = config or utils.get_config().get("data_store")
        if config is None:
            raise ValueError("Configuration not found")

        self.config = configurations.ObjectStoreConfiguration(**config)
        self.root_bucket = self.config.root_bucket
        self.component_factory = self.__init_component_factory()

    @property
    def client(self) -> abstract.ObjectStoreClient:
        if not hasattr(self, "_client"):
            self._client = self.component_factory.create_client()
        return self._client

    def list_buckets(self, *args, **kwargs) -> Generator[models.Bucket, None, None]:
        buckets = self.client.list_buckets(*args, **kwargs)
        return buckets

    def delete_file(
        self,
        key: str,
        version: str = None,
        bucket: str = None,
        *args,
        **kwargs,
    ):
        self.client.delete_object(
            key=key,
            version=version,
            bucket=bucket,
            *args,
            **kwargs,
        )

    def download_file(
        self,
        key: str,
        file_path: str,
        bucket: str = None,
        *args,
        **kwargs,
    ):
        return self.client.download_file(
            key=key,
            file_path=file_path,
            bucket=bucket,
            *args,
            **kwargs,
        )

    def get_file(
        self,
        key: str,
        bucket: str = None,
        *args,
        **kwargs,
    ) -> models.Object:
        return self.client.get_object(
            key=key,
            bucket=bucket,
            *args,
            **kwargs,
        )

    def list_files(
        self,
        prefix: str = "",
        bucket: str = None,
        *args,
        **kwargs,
    ) -> Generator[models.ObjectMetadata, None, None]:
        objects = self.list_objects(
            prefix=prefix,
            bucket=bucket,
            *args,
            **kwargs,
        )

        for obj in objects:
            yield obj

    def upload_file(
        self,
        file_path: str,
        key: str,
        bucket: str = None,
        *args,
        **kwargs,
    ):
        path = self.client.upload_file(
            file_path=file_path,
            key=key,
            bucket=bucket,
            *args,
            **kwargs,
        )

        return path

    def delete_object(
        self,
        key: str,
        bucket: str = None,
        version: str = None,
        *args,
        **kwargs,
    ) -> dict[str, Any]:
        return self.client.delete_object(
            key=key,
            bucket=bucket,
            version=version,
            *args,
            **kwargs,
        )

    def download_object(
        self,
        key: str,
        file_path: str = None,
        bucket: str = None,
        *args,
        **kwargs,
    ) -> Any:
        return self.client.download_object(
            key=key,
            file_path=file_path,
            bucket=bucket,
            *args,
            **kwargs,
        )

    def get_object(
        self,
        key: str,
        bucket: str = None,
        *args,
        **kwargs,
    ) -> models.Object:
        return self.client.get_object(
            key=key,
            bucket=bucket,
            *args,
            **kwargs,
        )

    def list_objects(
        self,
        prefix: str = "",
        bucket: str = None,
        *args,
        **kwargs,
    ) -> Generator[models.ObjectMetadata, None, None]:
        objects = self.client.list_objects(
            prefix=prefix,
            bucket=bucket,
            *args,
            **kwargs,
        )

        logger.debug(msg=objects)
        for obj in objects:
            yield obj

    def upload_object(
        self,
        file_path: str,
        key: str,
        bucket: str = None,
        *args,
        **kwargs,
    ) -> dict[str, Any]:
        return self.client.upload_object(
            file_path=file_path,
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
    ) -> dict[str, Any]:
        return self.client.copy_object(
            src_object=src_object,
            dst_object=dst_object,
            src_bucket=src_bucket,
            dst_bucket=dst_bucket,
            *args,
            **kwargs,
        )

    def __init_component_factory(self) -> abstract.ObjectStoreComponentFactory:
        framework = self.config.framework or DEFAULT_S3_FRAMEWORK
        if framework not in adapters.adaper_routers:
            raise ValueError(f"Doesn't support framework: {framework}")

        return adapters.adaper_routers[framework](self.config)
