"""
MySQL Database Setup Script
Creates the database and tables if they don't exist
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "finsage_db")

def create_database():
    """Create database if it doesn't exist"""
    try:
        # Connect to MySQL server (without specifying database)
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✅ Database '{MYSQL_DATABASE}' created successfully (or already exists)")
            
            cursor.close()
            connection.close()
            return True
            
    except Error as e:
        print(f"❌ Error creating database: {e}")
        return False

def setup_tables():
    """Setup tables using SQLAlchemy"""
    try:
        from database.mysql_config import engine, Base
        from database import models  # Import models to register them with Base
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ All database tables created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_connection():
    """Test database connection"""
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            record = cursor.fetchone()
            
            print(f"\n✅ Connected to MySQL Server version {db_info}")
            print(f"✅ Current database: {record[0]}")
            
            # Show tables
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            
            if tables:
                print(f"\n📊 Tables in database:")
                for table in tables:
                    print(f"   - {table[0]}")
            else:
                print("\n⚠️  No tables found in database")
            
            cursor.close()
            connection.close()
            return True
            
    except Error as e:
        print(f"\n❌ Error connecting to MySQL: {e}")
        print("\n💡 Setup Instructions:")
        print("   1. Install MySQL: https://dev.mysql.com/downloads/mysql/")
        print("   2. Start MySQL server")
        print("   3. Update .env file with your MySQL credentials:")
        print(f"      MYSQL_HOST={MYSQL_HOST}")
        print(f"      MYSQL_PORT={MYSQL_PORT}")
        print(f"      MYSQL_USER={MYSQL_USER}")
        print(f"      MYSQL_PASSWORD=your_password")
        print(f"      MYSQL_DATABASE={MYSQL_DATABASE}")
        return False

def main():
    """Main setup function"""
    print("="*60)
    print("FinSage AI - MySQL Database Setup")
    print("="*60)
    
    # Step 1: Create database
    print("\n[1/3] Creating database...")
    if not create_database():
        print("\n❌ Database creation failed. Please check your MySQL configuration.")
        return
    
    # Step 2: Create tables
    print("\n[2/3] Creating tables...")
    if not setup_tables():
        print("\n❌ Table creation failed.")
        return
    
    # Step 3: Verify setup
    print("\n[3/3] Verifying setup...")
    if check_connection():
        print("\n" + "="*60)
        print("🎉 MySQL database setup completed successfully!")
        print("="*60)
        print("\nYou can now start the FinSage AI backend server:")
        print("   cd backend && python main.py")
    else:
        print("\n❌ Setup verification failed.")

if __name__ == "__main__":
    main()
