# backend/schemas/transaction.py

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, Literal


class TransactionBase(BaseModel):
    """Base transaction schema"""
    date: datetime
    amount: float = Field(..., description="Transaction amount (positive for credit, negative for debit)")
    type: Literal["credit", "debit"]
    category: Optional[str] = Field(None, description="Expense/income category")
    description: Optional[str] = Field(None, max_length=500)
    source: Optional[str] = Field(None, description="Platform/client/payment source")
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v == 0:
            raise ValueError('Amount cannot be zero')
        return v


class TransactionCreate(TransactionBase):
    """Schema for creating a new transaction"""
    pass


class Transaction(TransactionBase):
    """Full transaction with ID"""
    id: str
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class TransactionBatch(BaseModel):
    """Batch transaction upload"""
    transactions: list[TransactionCreate]
