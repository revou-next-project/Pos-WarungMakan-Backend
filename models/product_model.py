from sqlalchemy import Column, Integer, String, DateTime, Float, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base
from datetime import datetime


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    name = Column(String(255), nullable=False)
    price = Column(Numeric(16, 2), nullable=False)
    category = Column(String(50), nullable=False)
    unit = Column(String(50), nullable=False)
    is_package = Column(Boolean, nullable=False)
    image = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.now)

    # Relationship with OrderItem
    order_items = relationship("OrderItem", back_populates="product")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': float(self.price) if self.price is not None else None,  
            'category': self.category,
            'unit': self.unit,
            'image': self.image,
            'created_at': self.created_at.isoformat() if self.created_at else None, 
            'updated_at': self.updated_at.isoformat() if self.updated_at else None  
        }