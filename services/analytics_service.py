from sqlalchemy import extract, func
from models.order_model import Order
from models.OrderItem_model import OrderItem
from models.product_model import Product
from fastapi_sqlalchemy import db
from fastapi import HTTPException

MEAL_PERIODS = {
    "breakfast": (6, 10),
    "lunch": (11, 14),
    "dinner": (17, 21)
}

def get_least_ordered_products(
    meal_period: str,
    limit: int = 5,
    raise_http: bool = False
):
    if meal_period not in MEAL_PERIODS:
        if raise_http:
            raise HTTPException(status_code=400, detail=f"Invalid meal period: {meal_period}")
        else:
            raise ValueError(f"Invalid meal period: {meal_period}")


    start_hour, end_hour = MEAL_PERIODS[meal_period]

    result = (
        db.session.query(
            OrderItem.product_id,
            Product.name,
            func.sum(OrderItem.quantity).label("total_sold")
        )
        .join(Order, Order.id == OrderItem.order_id)
        .join(Product, Product.id == OrderItem.product_id)
        .filter(Order.payment_status.in_(["paid", "unpaid"]))
        .filter(Product.status.in_(["active", "inactive"]))
        .filter(extract("hour", Order.created_at).between(start_hour, end_hour))
        .group_by(OrderItem.product_id, Product.name)
        .order_by(func.sum(OrderItem.quantity).asc())
        .limit(limit)
        .all()
    )

    return [
        {
            "product_id": row.product_id,
            "product_name": row.name,
            "total_sold": int(row.total_sold or 0)
        }
        for row in result
    ]
