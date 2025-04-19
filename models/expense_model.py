from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float, Text
from models.base import Base
from datetime import datetime
from sqlalchemy.orm import relationship


class Expense(Base):
    __tablename__ = "expenses"
    
    iid = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), default=datetime.now)
    amount = Column(Float, nullable=False)
    category = Column(String(50), nullable=False)  # e.g. "sale", "ingredient", "gas", etc.
    expense_type = Column(String(10), nullable=False, default="DEBIT")  # "DEBIT" or "CREDIT"
    description = Column(Text, nullable=True)
    reference_order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.now)

    order = relationship("Order", backref="related_expenses")

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'amount': self.amount,
            'category': self.category,
            'expense_type': self.expense_type,
            'description': self.description,
            'reference_order_id': self.reference_order_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }