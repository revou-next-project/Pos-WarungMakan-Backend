from sqlalchemy import Column, Integer, String, DateTime, Float
from models.base import Base
from datetime import datetime

class InventoryItem(Base):
    __tablename__ = "inventory_items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    current_stock = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)
    min_threshold = Column(Float, nullable=False)
    last_updated = Column(DateTime(timezone=True), onupdate=datetime.now)
    category = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'current_stock': self.current_stock,
            'unit': self.unit,
            'min_threshold': self.min_threshold,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }