from pydantic import BaseModel
from typing import Optional

class ProductSchema(BaseModel):
    name: str
    price: float
    category: str
    unit: str
    is_package: bool = False
    image: Optional[str] = None

    class Config:
        from_attributes = True

class UpdateProductSchema(BaseModel):
    name: Optional[str] =  None
    price: Optional[float] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    is_package: Optional[bool] = None
    image: Optional[str] = None

    class Config:
        from_attributes = True