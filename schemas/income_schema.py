from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class Category(str, Enum):
    OTHER_INCOME = "other_income"
    INVESTMENT = "investment"
class CreateIncomeSchema(BaseModel):
    date: Optional[datetime] = None
    amount: float
    category: Category
    descriptions: Optional[str] = None