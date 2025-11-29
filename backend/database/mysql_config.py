"""
MySQL Database Configuration and Connection Management
"""

from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "finsage_db")

# Create Database URL with SSL for TiDB Cloud
DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4&ssl_verify_cert=false&ssl_verify_identity=false"

# Create SQLAlchemy Engine
# We'll create a placeholder engine first, but the real one is managed by MySQLManager
# This allows us to switch to SQLite if MySQL fails
DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4&ssl_verify_cert=false&ssl_verify_identity=false"

# Create Base class for models
Base = declarative_base()

class MySQLManager:
    """Manages MySQL database connections and operations"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.is_connected = False
        self.is_sqlite = False
        
        # Initialize with MySQL config by default
        self._create_mysql_engine()
        
    def _create_mysql_engine(self):
        """Create MySQL engine"""
        self.engine = create_engine(
            DATABASE_URL,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False,
            connect_args={
                "ssl": {
                    "ssl_verify_cert": False,
                    "ssl_verify_identity": False
                }
            }
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def _create_sqlite_engine(self):
        """Create SQLite engine for fallback"""
        print("⚠️  Switching to SQLite (in-memory) fallback...")
        self.engine = create_engine(
            "sqlite:///./finsage_fallback.db",
            connect_args={"check_same_thread": False}
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.is_sqlite = True

    def connect(self):
        """Test database connection and create tables"""
        try:
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            print("✅ MySQL database connected successfully")
            self.is_connected = True
            
        except Exception as e:
            print(f"⚠️  MySQL connection failed: {e}")
            # Switch to SQLite
            self._create_sqlite_engine()
            self.is_connected = True
            
        # Create all tables (works for both MySQL and SQLite)
        try:
            Base.metadata.create_all(bind=self.engine)
            print(f"✅ Database tables created/verified ({'SQLite' if self.is_sqlite else 'MySQL'})")
            return True
        except Exception as e:
            print(f"❌ Failed to create tables: {e}")
            return False
    
    @contextmanager
    def get_session(self):
        """Get database session with automatic cleanup"""
        if not self.SessionLocal:
            self.connect()
            
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_db(self):
        """Dependency for FastAPI routes"""
        if not self.SessionLocal:
            self.connect()
            
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    def close(self):
        """Close database connections"""
        try:
            if self.engine:
                self.engine.dispose()
                print("✅ Database connection closed")
        except Exception as e:
            print(f"⚠️  Error closing database connection: {e}")

# Create global instance
mysql_manager = MySQLManager()

# Convenience function to get session
def get_db_session():
    """Get database session for use in routes"""
    return mysql_manager.get_session()

