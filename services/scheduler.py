from apscheduler.schedulers.background import BackgroundScheduler
from services.analytics_service import get_least_ordered_products
from models.product_model import Product
from datetime import datetime
from fastapi_sqlalchemy import db  
scheduler = BackgroundScheduler()
MEAL_TIMES = {
    "breakfast": (6, 10),
    "lunch": (11, 14),
    "dinner": (17, 21)
}

def apply_dynamic_discounts():
    now = datetime.now().hour

    if 6 <= now < 10:
        period = "breakfast"
    elif 11 <= now < 14:
        period = "lunch"
    elif 17 <= now < 21:
        period = "dinner"
    else:
        print("Not in a meal window, skipping.")
        return

    print(f"🔎 Checking least ordered products for {period}...")

    try:
        with db():
            products = get_least_ordered_products(meal_period=period, payment_status="paid", limit=3)

            for item in products:
                product = db.session.query(Product).filter_by(id=item["product_id"]).first()
                if product:
                    product.discount = 0.2
                    product.updated_at = datetime.now()
                    db.session.add(product)

            db.session.commit()
            print(f"Applied discount to {[p['product_name'] for p in products]}")

    except Exception as e:
        db.session.rollback()
        print("Scheduler error:", str(e))

