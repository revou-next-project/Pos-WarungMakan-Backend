from pydantic import BaseModel
from typing import Optional

class InventorySchema(BaseModel):
    name: str
    current_stock: float
    unit: str
    min_threshold: float
    category: str
    price_per_unit: Optional[float] = None
    recorded_by: Optional[int] = None 
    class Config:
        from_attributes = True

class UpdateInventorySchema(BaseModel):
    name: Optional[str]
    current_stock: Optional[float]
    unit: Optional[str]
    min_threshold: Optional[float]
    category: Optional[str]
    price_per_unit: Optional[float] = None
    recorded_by: Optional[int] = None

    class Config:
        from_attributes = True
        
class AddStockSchema(BaseModel):
    quantity: float
    price_per_unit: float
    description: Optional[str] = "Stock replenishment"