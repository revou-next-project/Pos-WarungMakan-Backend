from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EmployeeCreateSchema(BaseModel):
    user_id: Optional[int] = None
    name: str
    role: str
    hourly_rate: Optional[float] = None
    monthly_salary: Optional[float] = None

class EmployeeUpdateSchema(BaseModel):
    name: Optional[str]
    role: Optional[str]
    hourly_rate: Optional[float]
    monthly_salary: Optional[float]

class EmployeeSchema(BaseModel):
    id: int
    user_id: Optional[int]
    name: str
    role: str
    hourly_rate: Optional[float]
    monthly_salary: Optional[float]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
