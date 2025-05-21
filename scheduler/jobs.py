from datetime import datetime
from fastapi_sqlalchemy import db
from models.InventoryItem_model import InventoryItem
from models.product_model import Product
from models.recipeItem_model import RecipeItem
from services.analytics_service import get_least_ordered_products

def apply_dynamic_discounts():
    now = datetime.now().hour
    if 6 <= now < 10:
        period = "breakfast"
    elif 11 <= now < 14:
        period = "lunch"
    elif 17 <= now < 21:
        period = "dinner"
    else:
        print("Outside meal period")
        return

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
            print(f"✅ Discounts applied: {[p['product_name'] for p in products]}")

    except Exception as e:
        db.session.rollback()
        print("Discount error:", str(e))

def update_product_status_based_on_inventory():
    print("Checking product availability based on inventory...")

    try:
        with db():
            all_products = db.session.query(Product).all()

            for product in all_products:
                recipes = db.session.query(RecipeItem).filter_by(product_id=product.id).all()

                if not recipes:
                    product.status = "inactive"  # no recipe = cannot be produced
                    db.session.add(product)
                    continue

                can_make = True

                for recipe in recipes:
                    inventory = db.session.query(InventoryItem).filter_by(id=recipe.inventory_item_id).first()
                    if not inventory:
                        can_make = False
                        break

                    # Check if current stock is sufficient
                    if inventory.current_stock < recipe.quantity_needed or inventory.current_stock < inventory.min_threshold:
                        can_make = False
                        break

                product.status = "active" if can_make else "inactive"
                product.updated_at = datetime.now()
                db.session.add(product)

            db.session.commit()
            print("Product statuses updated based on inventory.")
    
    except Exception as e:
        db.session.rollback()
        print("Error updating product status:", str(e))