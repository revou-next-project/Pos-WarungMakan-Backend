from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_sqlalchemy import db
from schemas.order_schema import CreateOrderSchema, OrderWrapperSchema, PayOrderSchema, UpdateOrderSchema
from services.order_service import cancel_order, get_order_by_id, list_orders, list_unpaid_orders, pay_order, save_order
from services.jwt_utils import get_current_user

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("")
def create_order_controller(
    wrapper: OrderWrapperSchema,
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] not in ["admin", "cashier"]:
        raise HTTPException(status_code=403, detail="Access denied")

    return save_order(wrapper, employee_id=current_user["id"])


# @router.patch("/{order_id}/pay")
# def pay_order_controller(
#     order_id: int,
#     data: PayOrderSchema,
#     current_user: dict = Depends(get_current_user)
# ):
#     if current_user["role"] not in ["admin", "cashier"]:
#         raise HTTPException(status_code=403, detail="Access denied")

#     employee_id = current_user["id"]
#     return pay_order(order_id, data, employee_id)


@router.patch("/{order_id}/cancel")
def cancel_order_controller(
    order_id: int,
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] not in ["admin", "cashier"]:
        raise HTTPException(403, detail="Access denied")

    return cancel_order(order_id, employee_id=current_user["id"])


# @router.put("/{order_id}")
# def update_order_controller(
#     order_id: int,
#     data: UpdateOrderSchema,
#     current_user: dict = Depends(get_current_user)
# ):
#     if current_user["role"] not in ["admin", "cashier"]:
#         raise HTTPException(status_code=403, detail="Access denied")

#     return update_order(order_id, data)

@router.get("")
def list_orders_controller(
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
        payment_status=payment_status,
        order_type=order_type,
        start_date=start_date,
        end_date=end_date,
        page=page,
        limit=limit
    )
    
@router.get("/orders/unpaid", tags=["Orders"])
def get_unpaid_orders(current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin", "cashier"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return list_unpaid_orders()

@router.get("/{order_id}")
def get_order_controller(order_id: int, current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin", "cashier"]:
        raise HTTPException(status_code=403, detail="Access denied")

    return get_order_by_id(order_id)
