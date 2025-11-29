# backend/database/__init__.py
"""Database configuration and connection management"""

from .mysql_config import mysql_manager, Base
from . import models

__all__ = [
    # MySQL Connection management
    'mysql_manager',
    'Base',
    'models',
]
