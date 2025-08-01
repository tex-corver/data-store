from . import mysql_adapter, postgresql_adapter, sqlite_adapter

adapter_routers = {
    "sqlite": sqlite_adapter.SQLComponentFactory,
    "mysql": mysql_adapter.SQLComponentFactory,
    "postgresql": postgresql_adapter.SQLComponentFactory,
}
