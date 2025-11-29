"""
MySQL Database Configuration and Connection Management
"""

from sqlalchemy import create_engine, event
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
engine = create_engine(
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

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

class MySQLManager:
    """Manages MySQL database connections and operations"""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
        self.is_connected = False
        
    def connect(self):
        """Test database connection and create tables"""
        try:
            # Test connection
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            
            print("✅ MySQL database connected successfully")
            
            # Create all tables
            Base.metadata.create_all(bind=self.engine)
            print("✅ Database tables created/verified")
            
            self.is_connected = True
            return True
            
        except Exception as e:
            print(f"⚠️  MySQL connection failed: {e}")
            print("   Running in demo mode without database persistence")
            self.is_connected = False
            return False
    
    @contextmanager
    def get_session(self):
        """Get database session with automatic cleanup"""
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
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    def close(self):
        """Close database connections"""
        try:
            self.engine.dispose()
            print("✅ MySQL connection closed")
        except Exception as e:
            print(f"⚠️  Error closing MySQL connection: {e}")

# Create global instance
mysql_manager = MySQLManager()

# Convenience function to get session
def get_db_session():
    """Get database session for use in routes"""
    return mysql_manager.get_session()
