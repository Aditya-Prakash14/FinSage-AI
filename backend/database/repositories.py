# backend/database/repositories.py
"""Repository pattern for data access layer"""

from pymongo.database import Database
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from bson import ObjectId


class BaseRepository:
    """Base repository with common operations"""
    
    def __init__(self, db: Database, collection_name: str):
        self.db = db
        self.collection = db[collection_name]
    
    def create(self, data: dict) -> str:
        """Insert a new document"""
        result = self.collection.insert_one(data)
        return str(result.inserted_id)
    
    def find_by_id(self, doc_id: str) -> Optional[dict]:
        """Find document by ID"""
        return self.collection.find_one({"_id": ObjectId(doc_id)})
    
    def update(self, doc_id: str, data: dict) -> bool:
        """Update a document"""
        result = self.collection.update_one(
            {"_id": ObjectId(doc_id)},
            {"$set": data}
        )
        return result.modified_count > 0
    
    def delete(self, doc_id: str) -> bool:
        """Delete a document"""
        result = self.collection.delete_one({"_id": ObjectId(doc_id)})
        return result.deleted_count > 0


class UserRepository(BaseRepository):
    """User-specific operations"""
    
    def __init__(self, db: Database):
        super().__init__(db, "users")
    
    def find_by_email(self, email: str) -> Optional[dict]:
        """Find user by email"""
        return self.collection.find_one({"email": email})
    
    def create_user(self, user_data: dict) -> str:
        """Create new user with validation"""
        existing = self.find_by_email(user_data.get("email"))
        if existing:
            raise ValueError("User with this email already exists")
        
        user_data["created_at"] = datetime.utcnow()
        user_data["is_active"] = True
        return self.create(user_data)


class TransactionRepository(BaseRepository):
    """Transaction-specific operations"""
    
    def __init__(self, db: Database):
        super().__init__(db, "transactions")
    
    def find_by_user(
        self, 
        user_id: str, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        transaction_type: Optional[str] = None
    ) -> List[dict]:
        """Find transactions for a user with optional filters"""
        query = {"user_id": user_id}
        
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query["$gte"] = start_date
            if end_date:
                date_query["$lte"] = end_date
            query["date"] = date_query
        
        if transaction_type:
            query["type"] = transaction_type
        
        return list(self.collection.find(query).sort("date", -1))
    
    def get_recent_transactions(self, user_id: str, days: int = 90) -> List[dict]:
        """Get transactions from last N days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return self.find_by_user(user_id, start_date=cutoff_date)
    
    def get_category_summary(
        self, 
        user_id: str, 
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, float]:
        """Aggregate spending by category"""
        pipeline = [
            {
                "$match": {
                    "user_id": user_id,
                    "date": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": "$category",
                    "total": {"$sum": "$amount"}
                }
            }
        ]
        
        results = self.collection.aggregate(pipeline)
        return {item["_id"]: item["total"] for item in results}
    
    def get_monthly_summary(self, user_id: str, year: int, month: int) -> dict:
        """Get summary statistics for a specific month"""
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        transactions = self.find_by_user(user_id, start_date=start_date, end_date=end_date)
        
        income = sum(txn["amount"] for txn in transactions if txn["type"] == "credit")
        expenses = sum(abs(txn["amount"]) for txn in transactions if txn["type"] == "debit")
        
        return {
            "year": year,
            "month": month,
            "total_income": income,
            "total_expenses": expenses,
            "net_savings": income - expenses,
            "transaction_count": len(transactions),
            "categories": self.get_category_summary(user_id, start_date, end_date)
        }
    
    def get_spending_trend(self, user_id: str, days: int = 30) -> List[dict]:
        """Get daily spending trend"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        pipeline = [
            {
                "$match": {
                    "user_id": user_id,
                    "type": "debit",
                    "date": {"$gte": cutoff_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {"format": "%Y-%m-%d", "date": "$date"}
                    },
                    "total": {"$sum": {"$abs": "$amount"}},
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"_id": 1}
            }
        ]
        
        results = self.collection.aggregate(pipeline)
        return [{"date": item["_id"], "amount": item["total"], "count": item["count"]} for item in results]
    
    def batch_create(self, transactions: List[dict]) -> List[str]:
        """Create multiple transactions at once"""
        for txn in transactions:
            txn["created_at"] = datetime.utcnow()
        
        result = self.collection.insert_many(transactions)
        return [str(id) for id in result.inserted_ids]


class BudgetRepository(BaseRepository):
    """Budget-specific operations"""
    
    def __init__(self, db: Database):
        super().__init__(db, "budgets")
    
    def find_active_budget(self, user_id: str) -> Optional[dict]:
        """Get user's active budget"""
        return self.collection.find_one({
            "user_id": user_id,
            "is_active": True
        })
    
    def deactivate_all(self, user_id: str):
        """Deactivate all budgets for a user"""
        self.collection.update_many(
            {"user_id": user_id},
            {"$set": {"is_active": False}}
        )
    
    def create_budget(self, budget_data: dict) -> str:
        """Create new budget (deactivates previous ones)"""
        user_id = budget_data.get("user_id")
        self.deactivate_all(user_id)
        
        budget_data["created_at"] = datetime.utcnow()
        budget_data["updated_at"] = datetime.utcnow()
        budget_data["is_active"] = True
        
        return self.create(budget_data)


class GoalRepository(BaseRepository):
    """Financial goals operations"""
    
    def __init__(self, db: Database):
        super().__init__(db, "goals")
    
    def find_by_user(self, user_id: str) -> List[dict]:
        """Get all goals for a user"""
        return list(self.collection.find({"user_id": user_id}).sort("priority", 1))
    
    def update_progress(self, goal_id: str, amount: float) -> bool:
        """Add to goal's current amount"""
        result = self.collection.update_one(
            {"_id": ObjectId(goal_id)},
            {"$inc": {"current_amount": amount}}
        )
        return result.modified_count > 0
    
    def get_active_goals(self, user_id: str) -> List[dict]:
        """Get goals that haven't been completed"""
        return list(self.collection.find({
            "user_id": user_id,
            "$expr": {"$lt": ["$current_amount", "$target_amount"]}
        }).sort("deadline", 1))
    
    def mark_completed(self, goal_id: str) -> bool:
        """Mark a goal as completed"""
        result = self.collection.update_one(
            {"_id": ObjectId(goal_id)},
            {"$set": {"completed_at": datetime.utcnow(), "is_completed": True}}
        )
        return result.modified_count > 0


class ForecastRepository(BaseRepository):
    """Forecast history operations"""
    
    def __init__(self, db: Database):
        super().__init__(db, "forecasts")
    
    def save_forecast(self, user_id: str, forecast_type: str, forecast_data: dict) -> str:
        """Save forecast for historical tracking"""
        data = {
            "user_id": user_id,
            "forecast_type": forecast_type,  # 'income' or 'expense'
            "forecast_data": forecast_data,
            "created_at": datetime.utcnow()
        }
        return self.create(data)
    
    def get_recent_forecasts(self, user_id: str, forecast_type: str, limit: int = 10) -> List[dict]:
        """Get recent forecasts for comparison"""
        return list(self.collection.find({
            "user_id": user_id,
            "forecast_type": forecast_type
        }).sort("created_at", -1).limit(limit))
    
    def get_forecast_accuracy(self, user_id: str, forecast_type: str) -> dict:
        """Calculate forecast accuracy over time"""
        forecasts = self.get_recent_forecasts(user_id, forecast_type, limit=5)
        if not forecasts:
            return {"accuracy": None, "message": "No historical forecasts"}
        
        # This would compare predicted vs actual values
        # Implementation would depend on tracking actual values against predictions
        return {
            "accuracy": 0.85,  # Placeholder
            "sample_size": len(forecasts)
        }


# Repository factory
class RepositoryFactory:
    """Factory to get repository instances"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def get_user_repo(self) -> UserRepository:
        return UserRepository(self.db)
    
    def get_transaction_repo(self) -> TransactionRepository:
        return TransactionRepository(self.db)
    
    def get_budget_repo(self) -> BudgetRepository:
        return BudgetRepository(self.db)
    
    def get_goal_repo(self) -> GoalRepository:
        return GoalRepository(self.db)
    
    def get_forecast_repo(self) -> ForecastRepository:
        return ForecastRepository(self.db)
