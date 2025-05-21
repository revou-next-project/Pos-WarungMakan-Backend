from datetime import date
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
    

def time_based_analyis(start_date: date, end_date: date):
    peak_hours = (
        db.session.query(
            extract("hour", Order.created_at).label("hour"),
            func.count(Order.id).label("order_count")
        )
        .filter(Order.created_at.between(start_date, end_date))
        .filter(Order.payment_status == "paid")
        .group_by(extract("hour", Order.created_at))
        .order_by(func.count(Order.id).desc())
        .limit(3)
        .all()
    )
    
    busiest_days = (
        db.session.query(
            func.date(Order.created_at).label("day"),
            func.count(Order.id).label("order_count")
        )
        .filter(Order.created_at >= start_date, Order.created_at <= end_date)
        .filter(Order.payment_status == "paid")
        .group_by("day")
        .order_by(func.count(Order.id).desc())
        .limit(3)
        .all()
    )
    
    return {
        "peak_hours": [
            {"hour": int(row.hour), "order_count": row.order_count}
            for row in peak_hours
        ],
        "busiest_days": [
            {"day": row.day.strftime("%A, %d %B %Y"), "order_count": row.order_count}
            for row in busiest_days
        ]
    }


