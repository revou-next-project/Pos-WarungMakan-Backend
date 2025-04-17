# seed.py
from sqlalchemy.orm import Session
from models import Product, InventoryItem
from .database import SessionLocal

def seed_database():
    db = SessionLocal()

    # Check if products table is empty
    product_count = db.query(Product).count()
    if product_count == 0:
        # Sample products
        sample_products = [
            Product(
                name="Rice Box Chicken",
                price=20000,
                category="Food",
                unit="box",
                is_package=False,
                image="https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=300&q=80"
            ),
            Product(
                name="Fishball Satay",
                price=10000,
                category="Food",
                unit="stick",
                is_package=False,
                image="https://images.unsplash.com/photo-1529042410759-befb1204b468?w=300&q=80"
            ),
            Product(
                name="Iced Tea",
                price=5000,
                category="Drinks",
                unit="cup",
                is_package=False,
                image="https://images.unsplash.com/photo-1556679343-c1c1c9308e4e?w=300&q=80"
            ),
            Product(
                name="Mineral Water",
                price=3000,
                category="Drinks",
                unit="bottle",
                is_package=False,
                image="https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=300&q=80"
            ),
            Product(
                name="French Fries",
                price=15000,
                category="Snacks",
                unit="portion",
                is_package=False,
                image="https://images.unsplash.com/photo-1630384060421-cb20d0e0649d?w=300&q=80"
            ),
            Product(
                name="Package A",
                price=25000,
                category="Packages",
                unit="package",
                is_package=True,
                image="https://images.unsplash.com/photo-1607877742574-a7d9a7449af3?w=300&q=80"
            ),
        ]
        
        db.add_all(sample_products)
        db.commit()
        print(f"Added {len(sample_products)} sample products.")

    # Check if inventory table is empty
    inventory_count = db.query(InventoryItem).count()
    if inventory_count == 0:
        # Sample inventory items
        sample_inventory = [
            InventoryItem(
                name="Ayam Fillet",
                current_stock=5.5,
                unit="kg",
                min_threshold=2,
                category="Protein"
            ),
            InventoryItem(
                name="Beras",
                current_stock=25,
                unit="kg",
                min_threshold=10,
                category="Carbs"
            ),
            InventoryItem(
                name="Minyak Goreng",
                current_stock=8,
                unit="liter",
                min_threshold=5,
                category="Oil"
            ),
            InventoryItem(
                name="Fish Ball",
                current_stock=1.5,
                unit="pack",
                min_threshold=3,
                category="Frozen"
            ),
            InventoryItem(
                name="Gula",
                current_stock=4,
                unit="kg",
                min_threshold=2,
                category="Seasoning"
            ),
        ]
        
        db.add_all(sample_inventory)
        db.commit()
        print(f"Added {len(sample_inventory)} sample inventory items.")

    db.close()

    print("Database seeded with initial data.")