# seed.py
from sqlalchemy.orm import Session
from models import User
from database import SessionLocal

def seed_database():
    db = SessionLocal()

    # Create some initial data
    users = [
        User(name="Alice", email="alice@example.com"),
        User(name="Bob", email="bob@example.com"),
    ]

    # Check if the data already exists before inserting
    if db.query(User).count() == 0:
        db.add_all(users)
        db.commit()

    # Close session
    db.close()

    print("Database seeded with initial data.")