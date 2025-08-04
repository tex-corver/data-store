import logging
from typing import Any

import pymongo
import pymongo.collection
import pymongo.database
import pymongo.errors
import utils
from bson import ObjectId

from data_store.nosql_store import abstract, configurations, models

logger = logging.getLogger(__name__)


class NoSQLStore(abstract.NoSQLStore):
    """MongoDB implementation of NoSQL store"""

    config: configurations.NoSQLConfiguration

    def __init__(
        self,
        config: dict[str, Any] | configurations.NoSQLConfiguration,
    ) -> None:
        super().__init__(config)
        self._client: pymongo.MongoClient | None = None
        self._database: pymongo.database.Database | None = None

    def _init_client(self) -> pymongo.MongoClient:
        """Initialize MongoDB client using connection configuration"""
        connection_config = self.config.connection
        connection_uri = connection_config.connection_uri
        connection_timeout = connection_config.connection_timeout

        client = pymongo.MongoClient(
            connection_uri, serverSelectionTimeoutMS=connection_timeout * 1000
        )

        # Test the connection
        try:
            client.admin.command("ping")
            logger.info("Successfully connected to MongoDB")
        except pymongo.errors.ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise RuntimeError(
                "Failed to connect to MongoDB. Check your connection settings."
                f" Error: {e}"
            ) from e
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

        return client

    def _get_database(self) -> pymongo.database.Database:
        """Get database instance"""
        if not self._client:
            raise RuntimeError("MongoDB client not initialized. Call connect() first.")

        if self._database is None:
            db_name = self.config.connection.database
            if not db_name:
                raise ValueError("Database name is required in configuration")
            self._database = self._client[db_name]

        return self._database

    def _get_collection(self, collection: str) -> pymongo.collection.Collection:
        """Get collection instance"""
        database = self._get_database()
        return database[collection]

    def _connect(self):
        """Establish database connection"""
        if not self._client:
            self._client = self._init_client()
        return self._client

    def _close(self):
        """Close connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None
            logger.info("MongoDB connection closed")

    def _insert(self, collection: str, data: dict) -> str:
        """Insert a document into a collection"""
        _collection = self._get_collection(collection)
        result = _collection.insert_one(data)
        return str(result.inserted_id)

    def _find(
        self,
        collection: str,
        filters: dict | None = None,
        projections: list[str] | None = None,
        skip: int = 0,
        limit: int = 0,
    ) -> list:
        """Find documents in a collection"""
        _collection = self._get_collection(collection)

        # Build projection dict from list
        projection_dict = None
        if projections:
            projection_dict = {field: 1 for field in projections}

        cursor = _collection.find(
            filter=filters or {},
            projection=projection_dict,
            skip=skip,
            limit=limit if limit > 0 else 0,
        )

        # Convert ObjectId to string for JSON serialization
        documents = []
        for doc in cursor:
            if "_id" in doc and isinstance(doc["_id"], ObjectId):
                doc["_id"] = str(doc["_id"])
            documents.append(doc)

        return documents

    def _update(
        self, collection: str, filters: dict, update_data: dict, upsert: bool = False
    ) -> int:
        """Update documents in a collection"""
        _collection = self._get_collection(collection)

        # Wrap update_data in $set if it doesn't contain operators
        if not any(key.startswith("$") for key in update_data.keys()):
            update_data = {"$set": update_data}

        result = _collection.update_many(filters, update_data, upsert=upsert)
        return result.modified_count

    def _delete(self, collection: str, filters: dict) -> int:
        """Delete documents from a collection"""
        _collection = self._get_collection(collection)
        result = _collection.delete_many(filters)
        return result.deleted_count

    def _bulk_insert(self, collection: str, data: list[dict]) -> str:
        """Insert multiple documents into a collection"""
        if not data:
            return "0"

        _collection = self._get_collection(collection)
        result = _collection.insert_many(data)
        return f"{len(result.inserted_ids)}"

    def _bulk_update(
        self,
        collection: str,
        filters: dict,
        update_data: list[dict],
        upsert: bool = False,
    ) -> int:
        """Update multiple documents in a collection"""
        if not update_data:
            return 0

        _collection = self._get_collection(collection)
        total_modified = 0

        # Process each update operation
        for update_doc in update_data:
            # Wrap update_doc in $set if it doesn't contain operators
            if not any(key.startswith("$") for key in update_doc.keys()):
                update_doc = {"$set": update_doc}

            result = _collection.update_many(filters, update_doc, upsert=upsert)
            total_modified += result.modified_count

        return total_modified

    def _bulk_delete(self, collection: str, filters: dict | list) -> int:
        """Delete multiple documents from a collection"""
        _collection = self._get_collection(collection)
        total_deleted = 0

        if isinstance(filters, dict):
            # Single filter for all documents
            result = _collection.delete_many(filters)
            total_deleted = result.deleted_count
        elif isinstance(filters, list):
            # Multiple filters
            for filter_doc in filters:
                result = _collection.delete_many(filter_doc)
                total_deleted += result.deleted_count
        else:
            raise ValueError("Filters must be dict or list of dicts")

        return total_deleted


class NoSQLStoreComponentFactory(abstract.NoSQLStoreComponentFactory):
    """Factory for creating MongoDB NoSQL store clients"""

    def __init__(self, config: dict[str, Any] | configurations.NoSQLConfiguration):
        super().__init__(config=config)

    def _create_client(self, *args, **kwargs) -> NoSQLStore:
        """Create MongoDB NoSQL store client"""
        return NoSQLStore(config=self.config)
