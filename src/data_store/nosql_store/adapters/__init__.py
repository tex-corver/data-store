from . import mongodb_adapter

adapter_router = {"mongodb": mongodb_adapter.NoSQLStoreComponentFactory}
