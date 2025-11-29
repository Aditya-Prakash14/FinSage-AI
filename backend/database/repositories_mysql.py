"""
Database repository layer for MySQL operations
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from database.models import User, Transaction, Budget, Forecast, AIInsight, AgentAnalysis

class UserRepository:
    """User data access layer"""
    
    @staticmethod
    def create_user(db: Session, user_data: dict) -> User:
        """Create a new user"""
        user = User(**user_data)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def update_user(db: Session, user_id: str, update_data: dict) -> Optional[User]:
        """Update user profile"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            user.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(user)
        return user
    
    @staticmethod
    def delete_user(db: Session, user_id: str) -> bool:
        """Delete user and all related data"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
            return True
        return False

class TransactionRepository:
    """Transaction data access layer"""
    
    @staticmethod
    def create_transaction(db: Session, transaction_data: dict) -> Transaction:
        """Create a new transaction"""
        transaction = Transaction(**transaction_data)
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction
    
    @staticmethod
    def create_transactions_batch(db: Session, transactions_data: List[dict]) -> List[Transaction]:
        """Create multiple transactions"""
        transactions = [Transaction(**data) for data in transactions_data]
        db.add_all(transactions)
        db.commit()
        for transaction in transactions:
            db.refresh(transaction)
        return transactions
    
    @staticmethod
    def get_transactions(
        db: Session,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        transaction_type: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 1000
    ) -> List[Transaction]:
        """Get user transactions with filters"""
        query = db.query(Transaction).filter(Transaction.user_id == user_id)
        
        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)
        if transaction_type:
            query = query.filter(Transaction.type == transaction_type)
        if category:
            query = query.filter(Transaction.category == category)
        
        return query.order_by(desc(Transaction.date)).limit(limit).all()
    
    @staticmethod
    def get_transaction_summary(
        db: Session,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get transaction summary for date range"""
        transactions = db.query(Transaction).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.date >= start_date,
                Transaction.date <= end_date
            )
        ).all()
        
        total_income = sum(t.amount for t in transactions if t.type == 'income')
        total_expenses = sum(t.amount for t in transactions if t.type == 'expense')
        
        # Category breakdown
        expense_by_category = {}
        for t in transactions:
            if t.type == 'expense':
                expense_by_category[t.category] = expense_by_category.get(t.category, 0) + t.amount
        
        return {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_savings': total_income - total_expenses,
            'savings_rate': (total_income - total_expenses) / total_income if total_income > 0 else 0,
            'transaction_count': len(transactions),
            'expense_by_category': expense_by_category
        }
    
    @staticmethod
    def delete_transaction(db: Session, transaction_id: int, user_id: str) -> bool:
        """Delete a transaction"""
        transaction = db.query(Transaction).filter(
            and_(Transaction.id == transaction_id, Transaction.user_id == user_id)
        ).first()
        if transaction:
            db.delete(transaction)
            db.commit()
            return True
        return False

class BudgetRepository:
    """Budget data access layer"""
    
    @staticmethod
    def create_budget(db: Session, budget_data: dict) -> Budget:
        """Create a new budget"""
        budget = Budget(**budget_data)
        db.add(budget)
        db.commit()
        db.refresh(budget)
        return budget
    
    @staticmethod
    def get_budgets(db: Session, user_id: str, is_active: bool = True) -> List[Budget]:
        """Get user budgets"""
        query = db.query(Budget).filter(Budget.user_id == user_id)
        if is_active is not None:
            query = query.filter(Budget.is_active == is_active)
        return query.all()
    
    @staticmethod
    def update_budget(db: Session, budget_id: int, user_id: str, update_data: dict) -> Optional[Budget]:
        """Update budget"""
        budget = db.query(Budget).filter(
            and_(Budget.id == budget_id, Budget.user_id == user_id)
        ).first()
        if budget:
            for key, value in update_data.items():
                if hasattr(budget, key):
                    setattr(budget, key, value)
            budget.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(budget)
        return budget
    
    @staticmethod
    def delete_budget(db: Session, budget_id: int, user_id: str) -> bool:
        """Delete budget"""
        budget = db.query(Budget).filter(
            and_(Budget.id == budget_id, Budget.user_id == user_id)
        ).first()
        if budget:
            db.delete(budget)
            db.commit()
            return True
        return False

class ForecastRepository:
    """Forecast data access layer"""
    
    @staticmethod
    def create_forecasts(db: Session, forecasts_data: List[dict]) -> List[Forecast]:
        """Create multiple forecasts"""
        forecasts = [Forecast(**data) for data in forecasts_data]
        db.add_all(forecasts)
        db.commit()
        for forecast in forecasts:
            db.refresh(forecast)
        return forecasts
    
    @staticmethod
    def get_forecasts(
        db: Session,
        user_id: str,
        forecast_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Forecast]:
        """Get forecasts for user"""
        query = db.query(Forecast).filter(Forecast.user_id == user_id)
        
        if forecast_type:
            query = query.filter(Forecast.forecast_type == forecast_type)
        if start_date:
            query = query.filter(Forecast.forecast_date >= start_date)
        if end_date:
            query = query.filter(Forecast.forecast_date <= end_date)
        
        return query.order_by(Forecast.forecast_date).all()
    
    @staticmethod
    def delete_old_forecasts(db: Session, user_id: str, before_date: datetime) -> int:
        """Delete old forecasts"""
        result = db.query(Forecast).filter(
            and_(
                Forecast.user_id == user_id,
                Forecast.forecast_date < before_date
            )
        ).delete()
        db.commit()
        return result

class AIInsightRepository:
    """AI Insight data access layer"""
    
    @staticmethod
    def create_insight(db: Session, insight_data: dict) -> AIInsight:
        """Create a new insight"""
        insight = AIInsight(**insight_data)
        db.add(insight)
        db.commit()
        db.refresh(insight)
        return insight
    
    @staticmethod
    def get_insights(
        db: Session,
        user_id: str,
        is_read: Optional[bool] = None,
        is_dismissed: Optional[bool] = False,
        limit: int = 50
    ) -> List[AIInsight]:
        """Get user insights"""
        query = db.query(AIInsight).filter(AIInsight.user_id == user_id)
        
        if is_read is not None:
            query = query.filter(AIInsight.is_read == is_read)
        if is_dismissed is not None:
            query = query.filter(AIInsight.is_dismissed == is_dismissed)
        
        return query.order_by(desc(AIInsight.created_at)).limit(limit).all()
    
    @staticmethod
    def mark_insight_read(db: Session, insight_id: int, user_id: str) -> Optional[AIInsight]:
        """Mark insight as read"""
        insight = db.query(AIInsight).filter(
            and_(AIInsight.id == insight_id, AIInsight.user_id == user_id)
        ).first()
        if insight:
            insight.is_read = True
            db.commit()
            db.refresh(insight)
        return insight

class AgentAnalysisRepository:
    """Agent Analysis data access layer"""
    
    @staticmethod
    def create_analysis(db: Session, analysis_data: dict) -> AgentAnalysis:
        """Save agent analysis results"""
        analysis = AgentAnalysis(**analysis_data)
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        return analysis
    
    @staticmethod
    def get_latest_analysis(db: Session, user_id: str) -> Optional[AgentAnalysis]:
        """Get most recent analysis for user"""
        return db.query(AgentAnalysis).filter(
            AgentAnalysis.user_id == user_id
        ).order_by(desc(AgentAnalysis.analysis_date)).first()
    
    @staticmethod
    def get_analysis_history(db: Session, user_id: str, limit: int = 10) -> List[AgentAnalysis]:
        """Get analysis history for user"""
        return db.query(AgentAnalysis).filter(
            AgentAnalysis.user_id == user_id
        ).order_by(desc(AgentAnalysis.analysis_date)).limit(limit).all()
