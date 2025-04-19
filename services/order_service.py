from fastapi import HTTPException
from fastapi_sqlalchemy import db
from sqlalchemy import and_, func
from models.InventoryItem_model import InventoryItem
from models.expense_model import Expense
from models.order_model import Order
from models.OrderItem_model import OrderItem
from models.cashBalance_model import CashBalance, TransactionType
from models.recipeItem_model import RecipeItem
from schemas.order_schema import CreateOrderSchema, PayOrderSchema, UpdateOrderSchema
from datetime import datetime

def create_order(order_data: CreateOrderSchema):
    try:
        if not order_data.items:
            raise HTTPException(status_code=400, detail="Order must contain at least one item")

        order_number = generate_order_number(order_data.order_type)
        order = Order(
            order_number=order_number,
            order_type=order_data.order_type,
            status=order_data.status or "waiting",
            payment_status=order_data.payment_status,
            payment_method=order_data.payment_method,
            total_amount=order_data.total_amount,
            created_by=order_data.created_by,
            paid_at=datetime.now() if order_data.payment_status == "paid" else None
        )
        db.session.add(order)
        db.session.flush()

        for item in order_data.items:
            db.session.add(OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price,
                note=item.note
            ))

        if order_data.payment_status == "paid":
            db.session.add(CashBalance(
                transaction_type=TransactionType.SALE,
                amount=order.total_amount,
                reference_id=order.id,
                recorded_by=order_data.created_by
            ))
            db.session.add(Expense(
                amount=order.total_amount,
                category="sale",
                description=f"Direct sale on creation for order #{order.order_number}",
                reference_order_id=order.id,
                date=order.paid_at
            ))

        db.session.commit()
        return {"message": "Order created", "order_id": order.id}
    except Exception as e:
        db.session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    

def pay_order(order_id: int, data: PayOrderSchema, employee_id: int):
    try:
        order = db.session.query(Order).filter_by(id=order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        if order.payment_status == "paid":
            raise HTTPException(status_code=409, detail="Order already paid")
        if order.status == "canceled":
            raise HTTPException(status_code=400, detail="Cannot pay a canceled order")

        order.payment_status = "paid"
        order.payment_method = data.payment_method
        order.paid_at = datetime.now()

        db.session.add(CashBalance(
            transaction_type=TransactionType.SALE,
            amount=order.total_amount,
            reference_id=order.id,
            recorded_by=employee_id
        ))

        db.session.add(Expense(
            amount=order.total_amount,
            category="sale",
            description=f"Payment received for order #{order.order_number}",
            reference_order_id=order.id,
            date=order.paid_at
        ))

        for item in order.items:
            recipe_items = db.session.query(RecipeItem).filter_by(product_id=item.product_id).all()
            for recipe in recipe_items:
                inventory_item = db.session.query(InventoryItem).filter_by(id=recipe.inventory_item_id).first()
                if inventory_item:
                    deduction = recipe.quantity_needed * item.quantity
                    if inventory_item.current_stock < deduction:
                        raise HTTPException(400, f"Not enough stock for {inventory_item.name}")
                    inventory_item.current_stock -= deduction
                    db.session.add(inventory_item)

        db.session.commit()
        return {"message": "Order paid successfully", "order_id": order.id}
    except Exception as e:
        db.session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
def cancel_order(order_id: int):
    order = db.session.query(Order).filter_by(id=order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")

    if order.payment_status == "paid":
        raise HTTPException(400, "Cannot cancel a paid order")

    if order.status in ["completed", "cooking", "canceled"]:
        raise HTTPException(400, f"Cannot cancel an order with status {order.status}")

    order.status = "canceled"
    db.session.commit()
    return {"message": "Order canceled"}

def update_order(order_id: int, data: UpdateOrderSchema):
    order = db.session.query(Order).filter_by(id=order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")

    if order.payment_status == "paid":
        raise HTTPException(400, "Cannot edit a paid order")
    
    if order.status in ["completed", "canceled"]:
        raise HTTPException(400, f"Cannot edit order with status {order.status}")

    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        if key not in ["items", "order_number"]:
            setattr(order, key, value)

   
    if data.items:
        db.session.query(OrderItem).filter_by(order_id=order.id).delete()
        for item in data.items:
            db.session.add(OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price,
                note=item.note
            ))

    db.session.commit()
    return {"message": "Order updated"}

def list_orders(
    status=None,
    payment_status=None,
    order_type=None,
    start_date=None,
    end_date=None,
    page=1,
    limit=10
):
    try:
        query = db.session.query(Order)

        # Filtering
        if status:
            query = query.filter(Order.status == status)
        if payment_status:
            query = query.filter(Order.payment_status == payment_status)
        if order_type:
            query = query.filter(Order.order_type == order_type)
        if start_date and end_date:
            query = query.filter(
                and_(Order.timestamp >= start_date, Order.timestamp <= end_date)
            )

        # Count total for pagination
        total = query.count()

        # Pagination
        offset = (page - 1) * limit
        orders = query.order_by(Order.timestamp.desc()).offset(offset).limit(limit).all()

        return {
            "total": total,
            "page": page,
            "limit": limit,
            "data": [order.to_dict() for order in orders]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def generate_order_number(order_type: str):
    today_str = datetime.now().strftime("%Y%m%d")
    today_date = datetime.now().date()
    prefix = f"ORD-{order_type.upper().replace(' ', '')}"

    count_today = db.session.query(func.count(Order.id)).filter(
        func.date(Order.created_at) == today_date,
        Order.order_type == order_type
    ).scalar()

    return f"{prefix}-{today_str}-{count_today + 1:04d}"


