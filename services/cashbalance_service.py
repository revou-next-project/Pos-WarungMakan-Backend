from datetime import datetime
from sqlalchemy import func, and_
from models.cashBalance_model import CashBalance, TransactionType
from models.order_model import Order
from models.OrderItem_model import OrderItem
from models.product_model import Product
from models.InventoryItem_model import InventoryItem
from fastapi_sqlalchemy import db
from fastapi import HTTPException
from fastapi.responses import JSONResponse

def get_cashflow_summary(period: str = "day", page: int = 1, limit: int = 10, start_date: str = None, end_date: str = None, transaction_type: str = None):
    now = datetime.now()

    if period == "day":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "month":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif period == "year":
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        raise ValueError("Invalid period")

    if transaction_type == "SALE":
        sales = db.session.query(func.sum(CashBalance.amount)).filter(
            CashBalance.transaction_type == TransactionType.SALE,
            CashBalance.transaction_date >= start
        ).scalar() or 0
    else:
        sales = db.session.query(func.sum(CashBalance.amount)).filter(
            CashBalance.transaction_type == TransactionType.SALE,
            CashBalance.transaction_date >= start
        ).scalar() or 0

    if transaction_type == "EXPENSE":
        expenses = db.session.query(func.sum(CashBalance.amount)).filter(
            CashBalance.transaction_type == TransactionType.EXPENSE,
            CashBalance.transaction_date >= start
        ).scalar() or 0
    else:
        expenses = db.session.query(func.sum(CashBalance.amount)).filter(
            CashBalance.transaction_type == TransactionType.EXPENSE,
            CashBalance.transaction_date >= start
        ).scalar() or 0

    history_query = db.session.query(CashBalance).filter(
        CashBalance.transaction_date >= start
    )
    
    if transaction_type:
        history_query = history_query.filter(CashBalance.transaction_type == transaction_type)
    
    history = history_query.order_by(CashBalance.transaction_date.desc()).offset((page - 1) * limit).limit(limit).all()

    history_data = []
    for item in history:
        if item.transaction_type == TransactionType.SALE:
            source = {"order_id": item.reference_id, "order_type": "Dine In", "total_amount": item.amount}
            order_items = db.session.query(OrderItem).filter(OrderItem.order_id == item.reference_id).all()
            products = []
            for order_item in order_items:
                product = db.session.query(Product).filter(Product.id == order_item.product_id).first()
                if product:
                    products.append({
                        "product_id": product.id,
                        "product_name": product.name,
                        "purchased_quantity": order_item.quantity,
                        "purchase_date": item.transaction_date.isoformat()
                    })
            source["products"] = products
        elif item.transaction_type == TransactionType.EXPENSE:
            source = {"expense_id": item.reference_id, "category": "ingredient", "description": "Rice purchase"}
            
            inventory_item = db.session.query(InventoryItem).filter(InventoryItem.id == item.reference_id).first()
            if inventory_item:
                product = db.session.query(Product).filter(Product.id == inventory_item.product_id).first()
                if product:
                    source["product"] = {
                        "product_id": product.id,
                        "product_name": product.name,
                        "purchased_quantity": inventory_item.current_stock,
                        "purchase_date": item.transaction_date.isoformat()
                    }
        else:
            source = {}

        history_data.append({
            "id": item.id,
            "date": item.transaction_date.isoformat(),
            "type": item.transaction_type.value,
            "amount": item.amount,
            "notes": item.notes,
            "source": source
        })

    return {
        "total_sales": sales,
        "total_expenses": expenses,
        "net_cashflow": sales - expenses,
        "history": history_data,
        "page": page,
        "limit": limit
    }

async def get_cashflow_incomes(
        start_date: str,
        end_date: str,
        transaction_type: str
):
    try:
        ttype = (transaction_type or "").strip().lower()
        if ttype == "sale":
            query = db.session.query(Order).filter(Order.payment_status == "paid")

            if start_date and end_date:
                query = query.filter(
                    and_(Order.timestamp >= start_date, Order.timestamp < end_date)
                )
            total = query.count()
            orders = query.order_by(Order.timestamp.desc()).all()
            result = [
            {
                "id":             o.id,
                "amount":         o.total_amount,
                "payment_status": o.payment_status,
                "type":           "income",          
                "descriptions":   "Daily sales",     
                "category":       "sales",
                "created_at":     o.created_at.isoformat() if o.created_at else None,
            }
            for o in orders
        ]
            return JSONResponse(content={"data": result, "total": total}, status_code=200)
        else:
            return JSONResponse(content={
                "message": "Transaction still not designed"
            }, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))