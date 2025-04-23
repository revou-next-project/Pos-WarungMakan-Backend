from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from typing import List

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

class Ingredient(BaseModel):
    # id: int
    name: str
    quantity: float
    unit: str

    class Config:
        from_attributes = True

class RecipeCreateSchema(BaseModel):
    name: str
    description: str
    category: str
    ingredients: List[Ingredient]

    class Config:
        from_attributes = True

class RecipeUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    ingredients: Optional[List[Ingredient]] = None

    class Config:
        from_attributes = True
