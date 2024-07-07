from . import minio_adapter

adaper_routers = {"minio": minio_adapter.ObjectStoreComponentFactory}
