
from sqlalchemy import Column, Integer, String, DateTime, Float, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base
from datetime import datetime

class RecipeItem(Base):
    __tablename__ = "recipe_items"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"))
    quantity_needed = Column(Float, nullable=False)  # in unit of InventoryItem (e.g., grams, pcs)

    created_at = Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.now)

    # Relationships
    product = relationship("Product", backref="recipe_items")
    inventory_item = relationship("InventoryItem", backref="used_in_recipes")
    
    
    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "inventory_item_id": self.inventory_item_id,
            "quantity_needed": self.quantity_needed,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }   
