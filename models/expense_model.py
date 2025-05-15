from sqlalchemy import Column, Integer, Enum, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from models.base import Base
from enum import Enum as PyEnum


class category(PyEnum):
    INGREDIENT = "ingredient"
    ELECTRICITY = "electricity"
    UTILITIES = "utilities"
    RENT = "rent"
    SALARY = "salary"
    EQUIPMENT = "equipment"
    MARKETING = "marketing"
    OTHER= "other"

class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    cash_log_id = Column(Integer, ForeignKey("cash_balance.id", ondelete="CASCADE"), nullable=True) 
    date = Column(DateTime(timezone=True), default=datetime.now)
    amount = Column(Float, nullable=False)
    category = Column(Enum(category), nullable=False)  # e.g. "ingredient", "electricity", etc.
    descriptions = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.now)

    cash_log = relationship("CashBalance", back_populates="expenses")

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'amount': self.amount,
            'type': "expense",
            'category': self.category,
            'descriptions': self.descriptions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
