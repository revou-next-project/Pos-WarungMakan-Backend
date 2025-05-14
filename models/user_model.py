from sqlalchemy import Column, Float, Integer, String, DateTime, Boolean
from models.base import Base
from datetime import datetime
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # admin, cashier
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.now)
    discount = Column(Float, nullable=False)  
    
    employee_profile = relationship("Employee", back_populates="user", uselist=False, cascade="all, delete-orphan")
    cash_transactions = relationship("CashBalance", back_populates="user", cascade="all, delete-orphan")
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }