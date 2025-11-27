# database/mongo_config.py
"""Root-level MongoDB configuration (forwards to backend implementation)"""

import sys
from pathlib import Path

# Add backend to path for imports
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Import and re-export from backend
from database.mongo_config import MongoDBManager, mongodb_manager, get_db

__all__ = ['MongoDBManager', 'mongodb_manager', 'get_db']
