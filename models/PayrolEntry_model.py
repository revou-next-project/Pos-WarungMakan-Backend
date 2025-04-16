from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base
from datetime import datetime

class PayrollEntry(Base):
    __tablename__ = "payroll_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    hours_worked = Column(Float, nullable=True)
    amount_paid = Column(Float, nullable=False)
    payment_date = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False)  # pending, paid
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.now)
    
    # Relationship with Employee
    employee = relationship("Employee", back_populates="payroll_entries")

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None,
            'hours_worked': self.hours_worked,
            'amount_paid': self.amount_paid,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }