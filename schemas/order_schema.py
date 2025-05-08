from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime

ALLOWED_ORDER_TYPES = ["DINE-IN", "GOJEK", "GRAB", "SHOPEE", "OTHER"]


class OrderItemCreateSchema(BaseModel):
    product_id: int
    quantity: int
    price: float
    note: Optional[str] = None

class UpdateOrderItemSchema(BaseModel):
    product_id: Optional[int] = None
    quantity: Optional[int] = None
    price: Optional[float] = None
    note: Optional[str] = None

class CreateOrderSchema(BaseModel):
    order_type: Optional[str] = None
    payment_status: str = "unpaid"  # unpaid or paid
    payment_method: Optional[str] = None
    total_amount: float
    created_by: Optional[int] = None  # employee_id
    items: List[OrderItemCreateSchema]

    @validator("order_type", pre=True, always=True)
    def normalize_order_type(cls, v):
        if not v:
            return None
        return v.strip().upper()

class UpdateOrderSchema(BaseModel):
    order_type: Optional[str] = None
    total_amount: Optional[float] = None
    payment_method: Optional[str] = None
    items: Optional[List[UpdateOrderItemSchema]] = None

    @validator("order_type")
    def validate_order_type(cls, v):
        v = v.strip().upper()
        if v not in ALLOWED_ORDER_TYPES:
            raise ValueError(f"Invalid order_type: {v}")
        return v

class PayOrderSchema(BaseModel):
    payment_method: str
    paid_at: Optional[datetime] = None  # frontend bisa kirim waktu bayar jika offline mode


class OrderWrapperSchema(BaseModel):
    order_id: Optional[int] = None
    action: Optional[str] = None  # "pay" or None
    order: CreateOrderSchema