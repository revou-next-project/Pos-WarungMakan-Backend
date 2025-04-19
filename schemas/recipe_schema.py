from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RecipeItemBase(BaseModel):
    product_id: int
    inventory_item_id: int
    quantity_needed: float

class CreateRecipeItemSchema(RecipeItemBase):
    pass

class UpdateRecipeItemSchema(BaseModel):
    product_id: Optional[int]
    inventory_item_id: Optional[int]
    quantity_needed: Optional[float]

class RecipeItemOut(RecipeItemBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
