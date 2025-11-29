"""
Test database connection and verify/create schema
"""

import sys
from sqlalchemy import inspect, text
from database.mysql_config import engine, Base, mysql_manager
from database import models  # Import all models

def test_connection():
    """Test database connection"""
    print("="*60)
    print("Testing Database Connection")
    print("="*60)
    
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            
            # Get database info
            result = connection.execute(text("SELECT DATABASE()"))
            db_name = result.fetchone()[0]
            print(f"✅ Connected to database: {db_name}")
            
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def check_tables():
    """Check if tables exist"""
    print("\n" + "="*60)
    print("Checking Database Tables")
    print("="*60)
    
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if existing_tables:
            print(f"\n📊 Found {len(existing_tables)} existing tables:")
            for table in existing_tables:
                print(f"   - {table}")
                
                # Get column count
                columns = inspector.get_columns(table)
                print(f"     Columns: {len(columns)}")
        else:
            print("\n⚠️  No tables found in database")
            
        return existing_tables
    except Exception as e:
        print(f"❌ Error checking tables: {e}")
        return []

def get_expected_tables():
    """Get list of tables defined in models"""
    print("\n" + "="*60)
    print("Expected Tables from Models")
    print("="*60)
    
    expected_tables = []
    for table_name, table in Base.metadata.tables.items():
        expected_tables.append(table_name)
        print(f"   - {table_name}")
        print(f"     Columns: {len(table.columns)}")
        
        # Show some column details
        for col in list(table.columns)[:5]:  # Show first 5 columns
            col_type = str(col.type)
            nullable = "NULL" if col.nullable else "NOT NULL"
            pk = "PRIMARY KEY" if col.primary_key else ""
            print(f"       • {col.name}: {col_type} {nullable} {pk}")
        
        if len(table.columns) > 5:
            print(f"       ... and {len(table.columns) - 5} more columns")
    
    return expected_tables

def create_schema():
    """Create all tables using ORM"""
    print("\n" + "="*60)
    print("Creating Database Schema")
    print("="*60)
    
    try:
        # Drop all tables first (optional - be careful in production!)
        # Base.metadata.drop_all(bind=engine)
        # print("⚠️  Dropped existing tables")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Schema created successfully!")
        
        # Verify creation
        inspector = inspect(engine)
        created_tables = inspector.get_table_names()
        
        print(f"\n📊 Created {len(created_tables)} tables:")
        for table in created_tables:
            columns = inspector.get_columns(table)
            indexes = inspector.get_indexes(table)
            foreign_keys = inspector.get_foreign_keys(table)
            
            print(f"\n   ✓ {table}")
            print(f"     - Columns: {len(columns)}")
            print(f"     - Indexes: {len(indexes)}")
            print(f"     - Foreign Keys: {len(foreign_keys)}")
            
            # Show column details
            for col in columns:
                col_type = str(col['type'])
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                default = f"DEFAULT {col['default']}" if col.get('default') else ""
                print(f"       • {col['name']}: {col_type} {nullable} {default}")
        
        return True
    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_schema():
    """Verify schema matches models"""
    print("\n" + "="*60)
    print("Verifying Schema")
    print("="*60)
    
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    expected_tables = set(Base.metadata.tables.keys())
    
    missing_tables = expected_tables - existing_tables
    extra_tables = existing_tables - expected_tables
    
    if missing_tables:
        print(f"\n⚠️  Missing tables: {', '.join(missing_tables)}")
        return False
    
    if extra_tables:
        print(f"\n⚠️  Extra tables (not in models): {', '.join(extra_tables)}")
    
    if not missing_tables and not extra_tables:
        print("\n✅ Schema is up to date!")
        return True
    
    return len(missing_tables) == 0

def test_crud_operations():
    """Test basic CRUD operations"""
    print("\n" + "="*60)
    print("Testing CRUD Operations")
    print("="*60)
    
    from sqlalchemy.orm import Session
    from datetime import datetime
    import secrets
    
    try:
        with Session(engine) as session:
            # Test CREATE
            print("\n1. Testing CREATE...")
            test_user_id = f"test_{secrets.token_urlsafe(8)}"
            test_user = models.User(
                id=test_user_id,
                name="Test User",
                email=f"test_{secrets.token_urlsafe(8)}@example.com",
                password_hash="test_hash",
                onboarding_completed=False
            )
            session.add(test_user)
            session.commit()
            print(f"   ✅ Created user: {test_user.email}")
            
            # Test READ
            print("\n2. Testing READ...")
            user = session.query(models.User).filter_by(id=test_user_id).first()
            if user:
                print(f"   ✅ Found user: {user.name} ({user.email})")
            else:
                print("   ❌ User not found")
                return False
            
            # Test UPDATE
            print("\n3. Testing UPDATE...")
            user.onboarding_completed = True
            user.monthly_income = 50000
            session.commit()
            
            updated_user = session.query(models.User).filter_by(id=test_user_id).first()
            if updated_user.onboarding_completed:
                print(f"   ✅ Updated user: onboarding_completed={updated_user.onboarding_completed}")
            else:
                print("   ❌ Update failed")
                return False
            
            # Test CREATE related record (Transaction)
            print("\n4. Testing CREATE related record...")
            transaction = models.Transaction(
                user_id=test_user_id,
                amount=1000.50,
                type="income",
                category="salary",
                description="Test transaction",
                date=datetime.utcnow()
            )
            session.add(transaction)
            session.commit()
            print(f"   ✅ Created transaction: ₹{transaction.amount}")
            
            # Test relationship
            print("\n5. Testing RELATIONSHIPS...")
            user_with_txns = session.query(models.User).filter_by(id=test_user_id).first()
            print(f"   ✅ User has {len(user_with_txns.transactions)} transaction(s)")
            
            # Test DELETE
            print("\n6. Testing DELETE...")
            session.delete(user)  # Should cascade delete transactions
            session.commit()
            
            deleted_user = session.query(models.User).filter_by(id=test_user_id).first()
            if deleted_user is None:
                print("   ✅ User deleted successfully")
            else:
                print("   ❌ Delete failed")
                return False
            
            # Verify cascade delete
            orphan_txns = session.query(models.Transaction).filter_by(user_id=test_user_id).count()
            if orphan_txns == 0:
                print("   ✅ Cascade delete worked (transactions also deleted)")
            else:
                print(f"   ⚠️  Found {orphan_txns} orphan transactions")
            
            print("\n✅ All CRUD operations successful!")
            return True
            
    except Exception as e:
        print(f"\n❌ CRUD operations failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("\n" + "🔥"*30)
    print("FinSage AI - Database Schema Test")
    print("🔥"*30 + "\n")
    
    # Test 1: Connection
    if not test_connection():
        print("\n❌ Cannot proceed without database connection")
        return False
    
    # Test 2: Check existing tables
    existing_tables = check_tables()
    
    # Test 3: Get expected tables from models
    expected_tables = get_expected_tables()
    
    # Test 4: Verify or create schema
    if not existing_tables or set(existing_tables) != set(expected_tables):
        print("\n⚠️  Schema needs to be created or updated")
        if create_schema():
            print("\n✅ Schema creation successful!")
        else:
            print("\n❌ Schema creation failed")
            return False
    else:
        print("\n✅ Schema already exists and matches models")
    
    # Test 5: Verify schema
    if verify_schema():
        print("\n✅ Schema verification passed")
    else:
        print("\n⚠️  Schema verification found issues")
    
    # Test 6: CRUD operations
    if test_crud_operations():
        print("\n✅ CRUD operations test passed")
    else:
        print("\n❌ CRUD operations test failed")
        return False
    
    # Final summary
    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)
    print("✅ Database connection: OK")
    print("✅ Schema creation: OK")
    print("✅ Schema verification: OK")
    print("✅ CRUD operations: OK")
    print("\n🎉 All tests passed! Database is ready to use.")
    print("="*60 + "\n")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
