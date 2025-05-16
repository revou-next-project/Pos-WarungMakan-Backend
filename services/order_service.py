from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import joinedload
from fastapi_sqlalchemy import db
from sqlalchemy import and_, func
from models.InventoryItem_model import InventoryItem
from models.expense_model import Expense
from models.order_model import Order
from models.OrderItem_model import OrderItem
from models.cashBalance_model import CashBalance, TransactionType
from models.product_model import Product
from models.recipeItem_model import RecipeItem
from schemas.order_schema import ALLOWED_ORDER_TYPES, CreateOrderSchema, OrderWrapperSchema, PayOrderSchema, UpdateOrderSchema
from datetime import datetime

# def create_order(order_data: CreateOrderSchema, order_id: Optional[int] = None):
#     try:
#         if not order_data.items:
#             raise HTTPException(status_code=400, detail="Order must contain at least one item")

#         normalized_type = (order_data.order_type or "").strip().upper()
#         if normalized_type not in ALLOWED_ORDER_TYPES:
#             normalized_type = "TEMP"

#         order = None

#         if order_id:
#             order = db.session.query(Order).filter_by(id=order_id).first()
#             if not order:
#                 raise HTTPException(status_code=404, detail="Order not found")

#             db.session.query(OrderItem).filter_by(order_id=order.id).delete()
#             order.total_amount = order_data.total_amount
#             order.payment_method = order_data.payment_method
#             order.payment_status = order_data.payment_status
#             order.paid_at = datetime.now() if order_data.payment_status == "paid" else None
#             order.updated_at = datetime.now()

#         else:
#             order_number = generate_order_number(normalized_type)
#             order = Order(
#                 order_number=order_number,
#                 order_type=normalized_type,
#                 payment_status=order_data.payment_status,
#                 payment_method=order_data.payment_method,
#                 total_amount=order_data.total_amount,
#                 created_by=order_data.created_by,
#                 paid_at=datetime.now() if order_data.payment_status == "paid" else None
#             )
#             db.session.add(order)
#             db.session.flush()

#         for item in order_data.items:
#             db.session.add(OrderItem(
#                 order_id=order.id,
#                 product_id=item.product_id,
#                 quantity=item.quantity,
#                 price=item.price,
#                 note=item.note
#             ))

#         if order_data.payment_status == "paid" and order.payment_status != "paid":
#             db.session.add(CashBalance(
#                 transaction_type=TransactionType.SALE,
#                 amount=order.total_amount,
#                 reference_id=order.id,
#                 recorded_by=order_data.created_by
#             ))
#             order.payment_status = "paid"
#             order.paid_at = datetime.now()

#         db.session.commit()
#         return {"message": "Order created", "order_id": order.id}

#     except Exception as e:
#         db.session.rollback()
#         raise HTTPException(status_code=500, detail=str(e))



def save_order(wrapper: OrderWrapperSchema, employee_id: int):
    try:
        data = wrapper.order
        order_id = wrapper.order_id
        action = (wrapper.action or "").lower()

        if not data.items:
            raise HTTPException(status_code=400, detail="Order must contain at least one item")

        normalized_type = (data.order_type or "").strip().upper()
        if normalized_type not in ALLOWED_ORDER_TYPES:
            normalized_type = "TEMP"

        order = None

        if order_id:
            order = db.session.query(Order).filter_by(id=order_id).first()
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")

            db.session.query(OrderItem).filter_by(order_id=order.id).delete()
            order.total_amount = data.total_amount
            order.payment_method = data.payment_method
            order.payment_status = data.payment_status
            order.paid_at = datetime.now() if data.payment_status == "paid" else None
            order.updated_at = datetime.now()
        else:
            order_number = generate_order_number(normalized_type)
            order = Order(
                order_number=order_number,
                order_type=normalized_type,
                payment_status=data.payment_status,
                payment_method=data.payment_method,
                total_amount=data.total_amount,
                created_by=data.created_by or employee_id,
                paid_at=datetime.now() if data.payment_status == "paid" else None
            )
            db.session.add(order)
            db.session.flush()

        # Add items
        for item in data.items:
            db.session.add(OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price,
                note=item.note
            ))

        # Optional pay inline
        if action == "pay":
            if order.payment_status == "paid":
                raise HTTPException(409, "Order already paid")

            db.session.add(CashBalance(
                transaction_type=TransactionType.SALE,
                amount=order.total_amount,
                reference_id=order.id,
                recorded_by=employee_id
            ))
            order.payment_status = "paid"
            order.paid_at = datetime.now()
            order.updated_at = datetime.now()

            # Deduct stock
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
        return {
            "message": f"Order {'created' if not order_id else 'updated'} successfully",
            "order_id": order.id,
            "order_number": order.order_number,
            "paid": order.payment_status == "paid"
        }

    except HTTPException:
        raise
    except Exception as e:
        db.session.rollback()
        raise HTTPException(status_code=500, detail=str(e))



# def update_order(order_id: int, data: UpdateOrderSchema):
#     order = db.session.query(Order).filter_by(id=order_id).first()
#     if not order:
#         raise HTTPException(404, "Order not found")

#     if order.payment_status == "paid":
#         raise HTTPException(400, "Cannot edit a paid order")

#     if order.status in ["completed", "canceled"]:
#         raise HTTPException(400, f"Cannot edit order with status '{order.status}'")

#     update_data = data.dict(exclude_unset=True)
#     ALLOWED_ORDER_TYPES = ["DINE IN", "GOJEK", "GRAB", "SHOPEE", "OTHER"]

#     if "order_type" in update_data:
#         new_order_type = update_data["order_type"].strip().upper()

#         if new_order_type not in ALLOWED_ORDER_TYPES:
#             raise HTTPException(400, f"Invalid order_type: {new_order_type}")

#         old_order_type = (order.order_type or "").strip().upper()
#         if new_order_type != old_order_type:
#             parts = order.order_number.split("-")
#             if len(parts) == 4 and parts[0] == "ORD":
#                 parts[1] = new_order_type.replace(" ", "")
#                 order.order_number = "-".join(parts)

#         order.order_type = new_order_type

#     for key, value in update_data.items():
#         if key not in ["order_type", "order_number", "items"]:
#             setattr(order, key, value)

#     if data.items:
#         db.session.query(OrderItem).filter_by(order_id=order.id).delete()
#         for item in data.items:
#             db.session.add(OrderItem(
#                 order_id=order.id,
#                 product_id=item.product_id,
#                 quantity=item.quantity,
#                 price=item.price,
#                 note=item.note
#             ))

#     order.updated_at = datetime.now()

#     db.session.commit()
#     return {"message": "Order updated", "order_id": order.id, "order_number": order.order_number}


def pay_order(order_id: int, data: PayOrderSchema, employee_id: int):
    try:
        order = db.session.query(Order).filter_by(id=order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        if order.payment_status == "paid":
            raise HTTPException(status_code=409, detail="Order already paid")

        order.payment_status = "paid"
        order.payment_method = data.payment_method
        order.paid_at = datetime.now()
        order.updated_at = datetime.now()

        db.session.add(CashBalance(
            transaction_type=TransactionType.SALE,
            amount=order.total_amount,
            reference_id=order.id,
            recorded_by=employee_id
        ))

        for item in order.items:
            recipe_items = db.session.query(RecipeItem).filter_by(product_id=item.product_id).all()
            for recipe in recipe_items:
                inventory_item = db.session.query(InventoryItem).filter_by(id=recipe.inventory_item_id).first()
                if inventory_item:
                    deduction = recipe.quantity_needed * item.quantity
                    if inventory_item.current_stock < deduction:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Not enough stock for {inventory_item.name}"
                        )
                    inventory_item.current_stock -= deduction
                    db.session.add(inventory_item)

        db.session.commit()
        return {"message": "Order paid successfully", "order_id": order.id}

    except HTTPException:
        raise
    except Exception as e:
        db.session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

def cancel_order(order_id: int, employee_id: Optional[int] = None):
    try:
        order = db.session.query(Order).filter_by(id=order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        if order.payment_status == "paid":
            raise HTTPException(status_code=400, detail="Cannot cancel a paid order")

        if order.payment_status == "canceled":
            raise HTTPException(status_code=400, detail="Order is already canceled")


        order.payment_status = "canceled"
        order.updated_at = datetime.now()

        db.session.commit()
        return {"message": "Order canceled", "order_id": order.id}

    except Exception as e:
        db.session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


def list_orders(
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


def list_unpaid_orders():
    try:
        orders = db.session.query(Order).filter(
            Order.payment_status != "paid",
            Order.status != "canceled"
        ).order_by(Order.timestamp.desc()).all()

        return [order.to_dict() for order in orders]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def get_favorite_products(category=None, start_date=None, end_date=None):
    query = db.session.query(
        Product.name.label("product_name"),
        Product.category,
        func.sum(OrderItem.quantity).label("total_quantity"),
        func.sum(OrderItem.price * OrderItem.quantity).label("total_paid")
    ).join(OrderItem, Product.id == OrderItem.product_id) \
     .join(Order, Order.id == OrderItem.order_id) \
     .filter(Order.payment_status == "paid")

    if category:
        query = query.filter(Product.category == category)
    if start_date and end_date:
        query = query.filter(Order.paid_at.between(start_date, end_date))

    query = query.group_by(Product.id).order_by(func.sum(OrderItem.price * OrderItem.quantity).desc())

    result = query.all()

    return [
        {
            "product_name": row.product_name,
            "category": row.category,
            "total_sales": int(row.total_quantity)
        }
        for row in result
    ]
   
def get_sales_by_price_range(start_date=None, end_date=None):
    from collections import defaultdict

    # Define price ranges (min, max)
    ranges = [
        ("< 10K", 0, 10000),
        ("10K - 25K", 10000, 25000),
        ("25K - 50K", 25000, 50000),
        ("50K - 100K", 50000, 100000),
        ("> 100K", 100000, float("inf")),
    ]

    range_result = defaultdict(lambda: {"items_sold": 0, "products": []})

    query = (
        db.session.query(Product.price, func.sum(OrderItem.quantity).label("qty"))
        .join(OrderItem, Product.id == OrderItem.product_id)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.payment_status == "paid")
        .group_by(Product.id)
    )

    if start_date and end_date:
        query = query.filter(Order.paid_at.between(start_date, end_date))

    results = query.all()

    total_sold = sum(row.qty for row in results)

    for row in results:
        price = float(row.price)
        qty = int(row.qty)

        for label, min_price, max_price in ranges:
            if min_price <= price < max_price:
                range_result[label]["items_sold"] += qty
                range_result[label]["products"].append({"price": price, "quantity": qty})
                break

    response = []
    for label, data in range_result.items():
        sold = data["items_sold"]
        percent = (sold / total_sold * 100) if total_sold > 0 else 0
        response.append({
            "range": label,
            "items_sold": sold,
            "percentage": round(percent, 1),
            "products": data["products"],
        })

    response.sort(key=lambda x: x["items_sold"], reverse=True)
    return {
        "best_range": response[0]["range"] if response else None,
        "total_sold": total_sold,
        "ranges": response
    }
    
    
def get_order_by_id(order_id: int):
    order = (
        db.session.query(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.product))
        .filter_by(id=order_id)
        .first()
    )

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return {
        "id": order.id,
        "order_number": order.order_number,
        "order_type": order.order_type,
        "total_amount": order.total_amount,
        "payment_status": order.payment_status,
        "payment_method": order.payment_method,
        "paid_at": order.paid_at.isoformat() if order.paid_at else None,
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "product_name": item.product.name if item.product else None,
                "quantity": item.quantity,
                "price": item.price,
                "note": item.note
            }
            for item in order.items
        ]
    }
    
    
    

    


