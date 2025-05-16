from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class Category(str, Enum):
    INGREDIENT   = "ingredient"
    ELECTRICITY  = "electricity"
    UTILITIES    = "utilities"
    RENT         = "rent"
    SALARY       = "salary"
    EQUIPMENT    = "equipment"
    MARKETING    = "marketing"
    OTHER        = "other"
class CreateExpenseSchema(BaseModel):
    date: Optional[datetime] = None
    amount: float
    category: Category
    descriptions: Optional[str] = None

class UpdateExpenseSchema(BaseModel):
    date: Optional[datetime]
    amount: Optional[float]
    category: Optional[str]
    descriptions: Optional[str]

class ExpenseOut(BaseModel):
    id: int
    date: Optional[datetime]
    amount: float
    category: str
    descriptions: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
