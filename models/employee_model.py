from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float, Text
from sqlalchemy.orm import relationship
from models.base import Base
from datetime import datetime

class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, unique=True)
    name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False)
    hourly_rate = Column(Float, nullable=True)
    monthly_salary = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)

    user = relationship("User", back_populates="employee_profile")
    payroll_entries = relationship("PayrollEntry", back_populates="employee")  # if it exists

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'role': self.role,
            'hourly_rate': self.hourly_rate,
            'monthly_salary': self.monthly_salary,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }