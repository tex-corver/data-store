# Data Store
This is part of common libraries.

We provide a data store with the following features:
- Object store
- NoSQL store
- SQL store
- Vector store

# Installation
Use poetry to install the data store:

```bash
poetry add git+ssh://git@github.com:tex-corver/data-store.git
```

# Configuration
The data store can be configured using a configuration file, default in `.configs`. The configuration file should be in YAML format and can include the following sections:
```yaml
data_store:
    object_store:
        framework: "minio"  # Only minio is supported
        root_bucket: "your_root_bucket"  # The root bucket for the object store
        connection:
            endpoint: "192.168.0.100:9000"  # Endpoint of the object store
            access_key: "your_access"
            secret_key: "your_secret"
            secure: false  # Set to true if using HTTPS
    nosql_store:
        framework: "mongodb"  # Only mongodb is supported
        connection:
            uri: "mongodb://localhost:27017" # URI of the MongoDB database
            database: "your_database" # Name of the MongoDB database
            collection: "your_collection" # Name of the collection to query from the database
        query: # use this to specify the query to run against the NoSQL store
            fields: ["field1", "field2"]  # List of field names to include in the output (if None, all fields are returned)
            date_field: "date_field"  # Optional, field name for date filtering. start_date or end_date must be provided if this is set.
            start_date: "2023-01-01"  # Optional, start date for filtering 
            end_date: "2023-12-31"  # Optional, end date for filtering
            date_format: "%Y-%m-%d"  # Format of the date field. Default is "%Y-%m-%d"
            limit: 10 # Optional, maximum number of documents to return. Default is None.
```


# Usage

## Object Store
```python
import date_store
object_store = data_store.ObjectStore()

```

## NoSQL Store
```python
import data_store
nosql_store = data_store.NoSQLStore()

data = nosql_store.load_data() # Return polars DataFrame
```