from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class OrderItemCreateSchema(BaseModel):
    product_id: int
    quantity: int
    price: float
    note: Optional[str] = None

class CreateOrderSchema(BaseModel):
    order_type: str  # Dine In, GoFood, etc.
    status: str = "waiting"  # waiting, cooking, etc.
    payment_status: str = "unpaid"  # unpaid or paid
    payment_method: Optional[str] = None
    total_amount: float
    created_by: Optional[int] = None  # employee_id
    items: List[OrderItemCreateSchema]

class PayOrderSchema(BaseModel):
    payment_method: str
    paid_at: Optional[datetime] = None
    
class UpdateOrderItemSchema(BaseModel):
    product_id: Optional[int] = None
    quantity: Optional[int] = None
    price: Optional[float] = None
    note: Optional[str] = None

class UpdateOrderSchema(BaseModel):
    order_type: Optional[str] = None
    status: Optional[str] = None
    total_amount: Optional[float] = None
    items: Optional[List[UpdateOrderItemSchema]] = None

