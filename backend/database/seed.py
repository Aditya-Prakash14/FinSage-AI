# backend/database/seed.py
"""Database seeding utilities for testing and demo purposes"""

from datetime import datetime, timedelta
from typing import List, Dict
import random
from .mongo_config import get_db, mongodb_manager
from .repositories import RepositoryFactory


# Sample data for seeding
SAMPLE_CATEGORIES = {
    "credit": ["Freelance Payment", "Uber Earnings", "Food Delivery", "Consulting Fee", "Project Payment"],
    "debit": ["Groceries", "Transport", "Rent", "Utilities", "Food", "Entertainment", "Healthcare", "Mobile Recharge"]
}

SAMPLE_USERS = [
    {
        "email": "demo@finsage.ai",
        "name": "Demo User",
        "phone": "+919876543210",
        "primary_income_source": "Freelancing",
        "occupation": "Software Developer"
    },
    {
        "email": "test@finsage.ai",
        "name": "Test User",
        "phone": "+919876543211",
        "primary_income_source": "Food Delivery",
        "occupation": "Delivery Partner"
    }
]


def generate_sample_transactions(user_id: str, days: int = 90) -> List[dict]:
    """Generate sample transactions for a user"""
    transactions = []
    today = datetime.utcnow()
    
    for i in range(days):
        date = today - timedelta(days=i)
        
        # Random 2-4 transactions per day
        num_transactions = random.randint(2, 4)
        
        for _ in range(num_transactions):
            is_credit = random.random() > 0.3  # 70% expenses, 30% income
            txn_type = "credit" if is_credit else "debit"
            category = random.choice(SAMPLE_CATEGORIES[txn_type])
            
            if is_credit:
                # Income: ₹500 - ₹5000
                amount = random.randint(500, 5000)
            else:
                # Expenses: ₹50 - ₹2000
                amount = -random.randint(50, 2000)
            
            transactions.append({
                "user_id": user_id,
                "date": date,
                "amount": amount,
                "type": txn_type,
                "category": category,
                "description": f"{category} - {date.strftime('%Y-%m-%d')}",
                "source": "Payment App" if is_credit else "Card Payment",
                "created_at": datetime.utcnow()
            })
    
    return transactions


def seed_database(clear_existing: bool = False):
    """Seed the database with sample data"""
    print("🌱 Starting database seeding...")
    
    try:
        # Connect to database
        mongodb_manager.connect()
        db = get_db()
        
        if db is None:
            print("❌ Database connection failed. Cannot seed.")
            return
        
        repo_factory = RepositoryFactory(db)
        user_repo = repo_factory.get_user_repo()
        txn_repo = repo_factory.get_transaction_repo()
        budget_repo = repo_factory.get_budget_repo()
        goal_repo = repo_factory.get_goal_repo()
        
        # Clear existing data if requested
        if clear_existing:
            print("🗑️  Clearing existing data...")
            db.users.delete_many({})
            db.transactions.delete_many({})
            db.budgets.delete_many({})
            db.goals.delete_many({})
            print("✅ Existing data cleared")
        
        # Create sample users
        print("👤 Creating sample users...")
        user_ids = []
        for user_data in SAMPLE_USERS:
            try:
                user_id = user_repo.create_user(user_data)
                user_ids.append(user_id)
                print(f"   ✅ Created user: {user_data['email']}")
            except ValueError as e:
                # User already exists
                existing_user = user_repo.find_by_email(user_data['email'])
                if existing_user:
                    user_ids.append(str(existing_user['_id']))
                    print(f"   ℹ️  User exists: {user_data['email']}")
        
        # Generate transactions for each user
        print("💰 Generating sample transactions...")
        for user_id in user_ids:
            transactions = generate_sample_transactions(user_id, days=90)
            txn_ids = txn_repo.batch_create(transactions)
            print(f"   ✅ Created {len(txn_ids)} transactions for user {user_id}")
        
        # Create sample budgets
        print("📊 Creating sample budgets...")
        for user_id in user_ids:
            budget_data = {
                "user_id": user_id,
                "period": "monthly",
                "total_budget": 50000,
                "categories": {
                    "Groceries": 10000,
                    "Transport": 5000,
                    "Rent": 15000,
                    "Utilities": 3000,
                    "Food": 8000,
                    "Entertainment": 5000,
                    "Healthcare": 4000
                }
            }
            budget_id = budget_repo.create_budget(budget_data)
            print(f"   ✅ Created budget for user {user_id}")
        
        # Create sample financial goals
        print("🎯 Creating sample financial goals...")
        for user_id in user_ids:
            goals = [
                {
                    "user_id": user_id,
                    "goal_name": "Emergency Fund",
                    "target_amount": 100000,
                    "current_amount": 25000,
                    "deadline": datetime.utcnow() + timedelta(days=365),
                    "priority": 1,
                    "created_at": datetime.utcnow()
                },
                {
                    "user_id": user_id,
                    "goal_name": "New Laptop",
                    "target_amount": 60000,
                    "current_amount": 15000,
                    "deadline": datetime.utcnow() + timedelta(days=180),
                    "priority": 2,
                    "created_at": datetime.utcnow()
                }
            ]
            
            for goal in goals:
                goal_id = goal_repo.create(goal)
            print(f"   ✅ Created {len(goals)} goals for user {user_id}")
        
        print("\n✨ Database seeding completed successfully!")
        print(f"   - Users created: {len(user_ids)}")
        print(f"   - Transactions per user: ~{90 * 3}")
        print(f"   - Budgets created: {len(user_ids)}")
        print(f"   - Goals created: {len(user_ids) * 2}")
        
        # Print access information
        print("\n📝 Sample User Credentials:")
        for user in SAMPLE_USERS:
            print(f"   - Email: {user['email']}")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        raise


def clear_database():
    """Clear all data from the database"""
    print("🗑️  Clearing database...")
    
    try:
        mongodb_manager.connect()
        db = get_db()
        
        if db is None:
            print("❌ Database connection failed.")
            return
        
        collections = ["users", "transactions", "budgets", "goals", "forecasts"]
        
        for collection_name in collections:
            result = db[collection_name].delete_many({})
            print(f"   ✅ Cleared {collection_name}: {result.deleted_count} documents")
        
        print("✨ Database cleared successfully!")
        
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        raise


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        clear_database()
    else:
        seed_database(clear_existing=True)
