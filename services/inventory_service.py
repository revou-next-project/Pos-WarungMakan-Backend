from datetime import datetime
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from fastapi_sqlalchemy import db
from models.InventoryItem_model import InventoryItem
from models.cashBalance_model import CashBalance, TransactionType
from models.expense_model import Expense
from schemas.inventory_schema import (
    AddStockSchema,
    InventorySchema,
    UpdateInventorySchema
    
)

async def get_all_inventory(category: str = None, low_stock: bool = False):
    try:
        if category:
            inventories = db.session.query(InventoryItem).filter_by(category=category).all()
            return JSONResponse(content=[inventory.to_dict() for inventory in inventories], status_code=200)
        
        if low_stock:
            inventories = db.session.query(InventoryItem).filter(InventoryItem.current_stock < InventoryItem.min_threshold).all()
            return JSONResponse(content=[inventory.to_dict() for inventory in inventories], status_code=200)
        
        inventories = db.session.query(InventoryItem).all()
        return JSONResponse(content=[inventory.to_dict() for inventory in inventories], status_code=200)
    except SQLAlchemyError as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
async def get_inventory_byID(inventory_id: int):
    try:
        inventory = db.session.query(InventoryItem).filter_by(id=inventory_id).first()
        return JSONResponse(content=inventory.to_dict(), status_code=200)
    except SQLAlchemyError as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

async def create_inventory(inventory_data: InventorySchema):
    try:
        inventory = InventoryItem(
            name=inventory_data.name,
            current_stock=inventory_data.current_stock,
            unit=inventory_data.unit,
            min_threshold=inventory_data.min_threshold,
            category=inventory_data.category,
        )
        db.session.add(inventory)
        db.session.flush()

        if inventory_data.current_stock > 0 and inventory_data.price_per_unit:
            total_cost = inventory_data.current_stock * inventory_data.price_per_unit

            db.session.add(Expense(
                amount=total_cost,
                category="ingredient",
                description=f"Initial stock of {inventory.name}",
                date=datetime.now(),
                reference_order_id=None
            ))

            db.session.add(CashBalance(
                transaction_type=TransactionType.EXPENSE,
                amount=total_cost,
                reference_id=inventory.id,
                recorded_by=inventory_data.recorded_by or 0
            ))

        db.session.commit()
        return {"message": "Inventory item created"}
    except Exception as e:
        db.session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


async def update_inventory(inventory_id: int, inventory_data: UpdateInventorySchema):
    try:
        inventory = db.session.query(InventoryItem).filter_by(id=inventory_id).first()
        if not inventory:
            raise HTTPException(status_code=404, detail="Inventory not found")

        old_stock = inventory.current_stock

        for key, value in inventory_data.dict(exclude_unset=True).items():
            setattr(inventory, key, value)

        if (
            inventory_data.current_stock
            and inventory_data.current_stock > old_stock
            and inventory_data.price_per_unit
        ):
            diff = inventory_data.current_stock - old_stock
            total_cost = diff * inventory_data.price_per_unit

            db.session.add(Expense(
                amount=total_cost,
                category="ingredient",
                description=f"Stock refill for {inventory.name}",
                date=datetime.now(),
                reference_order_id=None
            ))

            db.session.add(CashBalance(
                transaction_type=TransactionType.EXPENSE,
                amount=total_cost,
                reference_id=inventory.id,
                recorded_by=inventory_data.recorded_by or 0
            ))

        db.session.commit()
        return {"message": "Inventory updated"}
    except Exception as e:
        db.session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


async def delete_inventory(inventory_id: int):
    try:
        inventory = db.session.query(InventoryItem).filter_by(id=inventory_id).first()
        if not inventory:
            raise HTTPException(status_code=404, detail="Inventory not found")

        db.session.delete(inventory)
        db.session.commit()
        return {"message": "Inventory deleted"}
    except Exception as e:
        db.session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
    
async def add_stock(inventory_id: int, data: AddStockSchema, employee_id: int):
    inventory = db.session.query(InventoryItem).filter_by(id=inventory_id).first()
    if not inventory:
        raise HTTPException(404, "Inventory item not found")
    
    total_cost = data.quantity * data.price_per_unit
    inventory.current_stock += data.quantity
    inventory.last_updated = datetime.now()

    # Create expense record
    db.session.add(Expense(
        amount=total_cost,
        category="ingredient",
        description=data.description,
        date=datetime.now()
    ))

    # Deduct cash
    db.session.add(CashBalance(
        transaction_type=TransactionType.EXPENSE,
        amount=total_cost,
        reference_id=inventory.id,
        recorded_by=employee_id
    ))

    db.session.commit()
    return {"message": "Stock added", "new_stock": inventory.current_stock}