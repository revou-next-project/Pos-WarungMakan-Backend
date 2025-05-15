from sqlalchemy import Column, Integer, Float, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func
from models.base import Base
from enum import Enum as PyEnum

# Enum for transaction types
class TransactionType(PyEnum):
    OPENING = "opening"
    CLOSING = "closing"
    SALE = "sale"
    EXPENSE = "expense"
    ADJUSTMENT = "adjustment"
    REFUND = "refund"

class CashBalance(Base):
    __tablename__ = "cash_balance"
    id = Column(Integer, primary_key=True, index=True)
    transaction_date = Column(DateTime(timezone=True), default=func.now())
    transaction_type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    reference_id = Column(Integer, nullable=True)  # Can reference order_id, expense_id, '' , etc.
    notes = Column(Text, nullable=True)
    recorded_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    
    # Relationship with the user who recorded it
    user = relationship("User", back_populates="cash_transactions")
    expenses = relationship("Expense", back_populates="cash_log")

    def to_dict(self):
        return {
            "id": self.id,
            "transaction_date": self.transaction_date.isoformat() if self.transaction_date else None,
            "transaction_type": self.transaction_type.value,
            "amount": self.amount,
            "reference_id": self.reference_id,
            "notes": self.notes,
            "recorded_by": self.recorded_by
        }
