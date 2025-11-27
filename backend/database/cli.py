#!/usr/bin/env python3
# backend/database/cli.py
"""Command-line interface for database management"""

import sys
import argparse
from datetime import datetime


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="FinSage AI Database Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Seed the database with sample data
  python -m database.cli seed

  # Clear all data
  python -m database.cli clear

  # Run health check
  python -m database.cli health

  # Run full validation
  python -m database.cli validate

  # Run migrations
  python -m database.cli migrate

  # Show database statistics
  python -m database.cli stats
        """
    )
    
    parser.add_argument(
        'command',
        choices=['seed', 'clear', 'health', 'validate', 'migrate', 'rollback', 'stats'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Skip confirmation prompts'
    )
    
    parser.add_argument(
        '--steps',
        type=int,
        default=1,
        help='Number of steps for rollback command'
    )
    
    args = parser.parse_args()
    
    # Execute command
    try:
        if args.command == 'seed':
            seed_database(args.force)
        
        elif args.command == 'clear':
            clear_database(args.force)
        
        elif args.command == 'health':
            health_check()
        
        elif args.command == 'validate':
            validate_database()
        
        elif args.command == 'migrate':
            run_migrations()
        
        elif args.command == 'rollback':
            rollback_migrations(args.steps)
        
        elif args.command == 'stats':
            show_statistics()
        
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


def seed_database(force: bool = False):
    """Seed database with sample data"""
    from .seed import seed_database as seed
    
    if not force:
        print("⚠️  This will clear existing data and populate with sample data.")
        confirm = input("Continue? (y/N): ")
        if confirm.lower() != 'y':
            print("❌ Cancelled")
            return
    
    seed(clear_existing=True)


def clear_database(force: bool = False):
    """Clear all database data"""
    from .seed import clear_database as clear
    
    if not force:
        print("⚠️  WARNING: This will permanently delete ALL data!")
        confirm = input("Are you absolutely sure? Type 'DELETE' to confirm: ")
        if confirm != 'DELETE':
            print("❌ Cancelled")
            return
    
    clear()


def health_check():
    """Run quick health check"""
    from .validator import quick_health_check
    
    print("🏥 Running health check...\n")
    
    result = quick_health_check()
    
    if result['healthy']:
        print("✅ Database is healthy!")
        print(f"\n📊 Statistics:")
        for collection, stats in result.get('statistics', {}).items():
            if 'error' not in stats:
                print(f"   {collection}: {stats['count']} documents ({stats['size']} bytes)")
    else:
        print(f"❌ Database unhealthy: {result['message']}")


def validate_database():
    """Run full database validation"""
    from .validator import DatabaseValidator
    
    validator = DatabaseValidator()
    results = validator.run_full_validation()


def run_migrations():
    """Run database migrations"""
    from .migrations import migration_manager
    
    migration_manager.migrate()


def rollback_migrations(steps: int = 1):
    """Rollback migrations"""
    from .migrations import migration_manager
    
    print(f"⏪ Rolling back {steps} migration(s)...")
    confirm = input("Continue? (y/N): ")
    if confirm.lower() != 'y':
        print("❌ Cancelled")
        return
    
    migration_manager.rollback(steps)


def show_statistics():
    """Show database statistics"""
    from .mongo_config import get_db, mongodb_manager
    
    print("📊 Database Statistics\n")
    
    mongodb_manager.connect()
    db = get_db()
    
    if db is None:
        print("❌ Cannot connect to database")
        return
    
    collections = ["users", "transactions", "budgets", "goals", "forecasts"]
    
    print(f"{'Collection':<20} {'Documents':<15} {'Indexes':<10}")
    print("-" * 45)
    
    total_docs = 0
    for collection_name in collections:
        try:
            collection = db[collection_name]
            count = collection.count_documents({})
            indexes = len(collection.index_information())
            total_docs += count
            
            print(f"{collection_name:<20} {count:<15} {indexes:<10}")
        except Exception as e:
            print(f"{collection_name:<20} {'Error':<15} {'-':<10}")
    
    print("-" * 45)
    print(f"{'TOTAL':<20} {total_docs:<15}")
    
    # Show database info
    try:
        db_stats = db.command("dbStats")
        print(f"\n💾 Storage:")
        print(f"   Data Size: {db_stats.get('dataSize', 0) / 1024:.2f} KB")
        print(f"   Index Size: {db_stats.get('indexSize', 0) / 1024:.2f} KB")
        print(f"   Total Size: {db_stats.get('storageSize', 0) / 1024:.2f} KB")
    except:
        pass


if __name__ == "__main__":
    main()
