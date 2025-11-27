# backend/database/__init__.py
"""Database configuration and connection management"""

from .mongo_config import MongoDBManager, mongodb_manager, get_db
from .repositories import (
    BaseRepository,
    UserRepository,
    TransactionRepository,
    BudgetRepository,
    GoalRepository,
    ForecastRepository,
    RepositoryFactory
)

__all__ = [
    # Connection management
    'MongoDBManager',
    'mongodb_manager',
    'get_db',
    
    # Repositories
    'BaseRepository',
    'UserRepository',
    'TransactionRepository',
    'BudgetRepository',
    'GoalRepository',
    'ForecastRepository',
    'RepositoryFactory',
]
