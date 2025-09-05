# NoSQL Store Development
This section provides detailed information for developers working on the NoSQL store functionality of the data-store library.

## Integration with Base Classes and Adapters

The `NoSQLStore` class:
- Utilizes an abstract factory (`NoSQLStoreComponentFactory`) to create an underlying client.
- Supports multiple frameworks through an adapter router (`adapters.adapter_routers`).
- Ensures proper instantiation and connection based on provided configuration.