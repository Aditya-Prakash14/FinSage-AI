# backend/database/mongo_config.py
"""MongoDB configuration and connection pooling"""

from pymongo import MongoClient
from pymongo.database import Database
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


class MongoDBManager:
    """Singleton MongoDB connection manager"""
    
    _instance: Optional['MongoDBManager'] = None
    _client: Optional[MongoClient] = None
    _db: Optional[Database] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def connect(self, connection_string: Optional[str] = None, db_name: Optional[str] = None):
        """Establish MongoDB connection"""
        if self._client is None:
            conn_str = connection_string or os.getenv(
                "MONGODB_URI", 
                "mongodb://localhost:27017/"
            )
            database_name = db_name or os.getenv("MONGODB_DB_NAME", "finsage_db")
            
            try:
                self._client = MongoClient(
                    conn_str,
                    maxPoolSize=50,
                    minPoolSize=10,
                    serverSelectionTimeoutMS=5000
                )
                self._db = self._client[database_name]
                
                # Test connection
                self._client.server_info()
                
                # Create indexes for better query performance
                self._create_indexes()
                
                print(f"✅ Connected to MongoDB: {database_name}")
            except Exception as e:
                print(f"⚠️  Warning: MongoDB not available: {e}")
                print("   API will run in demo mode without persistence")
                self._client = None
                self._db = None
    
    def _create_indexes(self):
        """Create necessary database indexes"""
        if self._db is None:
            return
        
        try:
            # User indexes
            self._db.users.create_index("email", unique=True)
            
            # Transaction indexes
            self._db.transactions.create_index([("user_id", 1), ("date", -1)])
            self._db.transactions.create_index("type")
            self._db.transactions.create_index("category")
            
            # Budget indexes
            self._db.budgets.create_index([("user_id", 1), ("is_active", -1)])
            
            # Goals indexes
            self._db.goals.create_index([("user_id", 1), ("deadline", 1)])
            
            print("✅ Database indexes created")
        except Exception as e:
            print(f"⚠️  Warning: Could not create indexes: {e}")
    
    def get_database(self) -> Database:
        """Get database instance"""
        if self._db is None:
            self.connect()
        return self._db
    
    def close(self):
        """Close MongoDB connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None


# Global instance
mongodb_manager = MongoDBManager()

def get_db() -> Database:
    """Dependency injection for database"""
    return mongodb_manager.get_database()
