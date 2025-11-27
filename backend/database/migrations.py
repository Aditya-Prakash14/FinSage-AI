# backend/database/migrations.py
"""Database migration utilities for schema changes"""

from datetime import datetime
from typing import Callable, List, Dict
from .mongo_config import get_db, mongodb_manager


class Migration:
    """Base migration class"""
    
    def __init__(self, version: str, description: str):
        self.version = version
        self.description = description
        self.applied_at = None
    
    def up(self, db):
        """Apply migration"""
        raise NotImplementedError
    
    def down(self, db):
        """Rollback migration"""
        raise NotImplementedError


class MigrationManager:
    """Manage database migrations"""
    
    def __init__(self):
        self.db = None
        self.migrations: List[Migration] = []
    
    def register_migration(self, migration: Migration):
        """Register a migration"""
        self.migrations.append(migration)
        self.migrations.sort(key=lambda m: m.version)
    
    def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions"""
        if self.db is None:
            mongodb_manager.connect()
            self.db = get_db()
        
        if self.db is None:
            return []
        
        migrations_col = self.db.migrations
        applied = migrations_col.find().sort("version", 1)
        return [m["version"] for m in applied]
    
    def mark_migration_applied(self, migration: Migration):
        """Mark migration as applied"""
        if self.db is None:
            return
        
        self.db.migrations.insert_one({
            "version": migration.version,
            "description": migration.description,
            "applied_at": datetime.utcnow()
        })
    
    def mark_migration_reverted(self, version: str):
        """Mark migration as reverted"""
        if self.db is None:
            return
        
        self.db.migrations.delete_one({"version": version})
    
    def migrate(self, target_version: str = None):
        """Run pending migrations up to target version"""
        if self.db is None:
            mongodb_manager.connect()
            self.db = get_db()
        
        if self.db is None:
            print("❌ Cannot connect to database")
            return
        
        applied = set(self.get_applied_migrations())
        
        print("🔄 Running database migrations...")
        
        migrations_run = 0
        for migration in self.migrations:
            if migration.version in applied:
                continue
            
            if target_version and migration.version > target_version:
                break
            
            try:
                print(f"   ⏩ Applying {migration.version}: {migration.description}")
                migration.up(self.db)
                self.mark_migration_applied(migration)
                migrations_run += 1
                print(f"   ✅ Applied {migration.version}")
            except Exception as e:
                print(f"   ❌ Failed to apply {migration.version}: {e}")
                break
        
        if migrations_run == 0:
            print("✅ No pending migrations")
        else:
            print(f"✅ Applied {migrations_run} migration(s)")
    
    def rollback(self, steps: int = 1):
        """Rollback last N migrations"""
        if self.db is None:
            mongodb_manager.connect()
            self.db = get_db()
        
        if self.db is None:
            print("❌ Cannot connect to database")
            return
        
        applied = self.get_applied_migrations()
        
        if not applied:
            print("ℹ️  No migrations to rollback")
            return
        
        print(f"⏪ Rolling back {steps} migration(s)...")
        
        # Get migrations to rollback (in reverse order)
        to_rollback = applied[-steps:]
        to_rollback.reverse()
        
        for version in to_rollback:
            # Find migration object
            migration = next((m for m in self.migrations if m.version == version), None)
            
            if not migration:
                print(f"   ⚠️  Migration {version} not found in code")
                continue
            
            try:
                print(f"   ⏪ Rolling back {version}: {migration.description}")
                migration.down(self.db)
                self.mark_migration_reverted(version)
                print(f"   ✅ Rolled back {version}")
            except Exception as e:
                print(f"   ❌ Failed to rollback {version}: {e}")
                break
        
        print("✅ Rollback completed")


# Example migrations

class AddEmailIndexMigration(Migration):
    """Add unique index on user email"""
    
    def __init__(self):
        super().__init__("001", "Add unique index on user email")
    
    def up(self, db):
        db.users.create_index("email", unique=True)
    
    def down(self, db):
        db.users.drop_index("email_1")


class AddTransactionIndexesMigration(Migration):
    """Add indexes for transaction queries"""
    
    def __init__(self):
        super().__init__("002", "Add transaction indexes")
    
    def up(self, db):
        db.transactions.create_index([("user_id", 1), ("date", -1)])
        db.transactions.create_index("type")
        db.transactions.create_index("category")
    
    def down(self, db):
        db.transactions.drop_index("user_id_1_date_-1")
        db.transactions.drop_index("type_1")
        db.transactions.drop_index("category_1")


class AddCreatedAtFieldMigration(Migration):
    """Add created_at field to existing documents"""
    
    def __init__(self):
        super().__init__("003", "Add created_at field to existing documents")
    
    def up(self, db):
        now = datetime.utcnow()
        
        # Add to users without created_at
        db.users.update_many(
            {"created_at": {"$exists": False}},
            {"$set": {"created_at": now}}
        )
        
        # Add to transactions without created_at
        db.transactions.update_many(
            {"created_at": {"$exists": False}},
            {"$set": {"created_at": now}}
        )
    
    def down(self, db):
        # Optionally remove created_at field
        pass


# Initialize migration manager
migration_manager = MigrationManager()

# Register migrations
migration_manager.register_migration(AddEmailIndexMigration())
migration_manager.register_migration(AddTransactionIndexesMigration())
migration_manager.register_migration(AddCreatedAtFieldMigration())


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "migrate":
            migration_manager.migrate()
        elif command == "rollback":
            steps = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            migration_manager.rollback(steps)
        elif command == "status":
            applied = migration_manager.get_applied_migrations()
            print(f"Applied migrations: {len(applied)}")
            for version in applied:
                print(f"  - {version}")
        else:
            print("Usage: python migrations.py [migrate|rollback|status]")
    else:
        migration_manager.migrate()
