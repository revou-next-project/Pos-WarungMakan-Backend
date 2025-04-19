from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship
from models.base import Base
from datetime import datetime

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(20), nullable=False, unique=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.now)
    status = Column(String(20), nullable=False)  # waiting, cooking, completed, canceled
    order_type = Column(String(20), nullable=False)  # Dine In, GoFood, Grab, Shopee, Other
    total_amount = Column(Float, nullable=False)
    
    payment_status = Column(String(20), nullable=False, default="unpaid")
    paid_at = Column(DateTime(timezone=True), nullable=True)
    payment_method = Column(String(20), nullable=True)  # optional
    
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.now)
    created_by = Column(Integer, ForeignKey("employees.id"), nullable=True)
    employee = relationship("Employee", backref="orders_created")
    # Relationship with OrderItem
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'timestamp': self.timestamp.isoformat() if self.created_at else None, 
            'status': self.status,
            'order_type': self.order_type,
            'total_amount': self.total_amount,
            'payment_status': self.payment_status,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'payment_method': self.payment_method,
            'created_at': self.created_at.isoformat() if self.created_at else None, 
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            
        }