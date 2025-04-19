from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_sqlalchemy import db
from schemas.order_schema import CreateOrderSchema, PayOrderSchema, UpdateOrderSchema
from services.order_service import cancel_order, create_order, list_orders, pay_order, update_order
from services.jwt_utils import get_current_user

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("")
def create_order_controller(
    order_data: CreateOrderSchema,
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] not in ["admin", "cashier"]:
        raise HTTPException(status_code=403, detail="Access denied")

    return create_order(order_data)


@router.patch("/{order_id}/pay")
def pay_order_controller(
    order_id: int,
    data: PayOrderSchema,
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] not in ["admin", "cashier"]:
        raise HTTPException(status_code=403, detail="Access denied")

    employee_id = current_user["id"]
    return pay_order(order_id, data, employee_id)


@router.patch("/{order_id}/cancel")
def cancel_order_controller(
    order_id: int,
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] not in ["admin", "cashier"]:
        raise HTTPException(status_code=403, detail="Access denied")

    return cancel_order(order_id)


@router.put("/{order_id}")
def update_order_controller(
    order_id: int,
    data: UpdateOrderSchema,
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] not in ["admin", "cashier"]:
        raise HTTPException(status_code=403, detail="Access denied")

    return update_order(order_id, data)

@router.get("")
def list_orders_controller(
    status: str = None,
    payment_status: str = None,
    order_type: str = None,
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
    page: int = 1,
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] not in ["admin", "cashier"]:
        raise HTTPException(status_code=403, detail="Access denied")

    return list_orders(
        status=status,
        payment_status=payment_status,
        order_type=order_type,
        start_date=start_date,
        end_date=end_date,
        page=page,
        limit=limit
    )
