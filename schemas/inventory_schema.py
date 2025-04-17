from pydantic import BaseModel
from typing import Optional

class InventorySchema(BaseModel):
    name: str
    current_stock: int
    min_threshold: int
    unit: str
    category: str

    class Config:
        from_attributes = True

class UpdateInventorySchema(BaseModel):
    name: Optional[str] = None
    current_stock: Optional[int] = None
    min_threshold: Optional[int] = None
    unit: Optional[str] = None
    category: Optional[str] = None

    class Config:
        from_attributes = True