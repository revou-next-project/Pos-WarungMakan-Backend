from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from app import db
from models.InventoryItem_model import InventoryItem
from schemas.inventory_schema import (
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
            min_threshold=inventory_data.min_threshold,
            unit=inventory_data.unit,
            category=inventory_data.category
        )
        db.session.add(inventory)
        db.session.commit()
        return JSONResponse(content=inventory.to_dict(), status_code=201)
    except SQLAlchemyError as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    

async def update_inventory(inventory_id: int, inventory_data: UpdateInventorySchema):
    try:
        inventory = db.session.query(InventoryItem).filter_by(id=inventory_id).first()

        if not inventory:
            return JSONResponse(content={"error": "Inventory not found"}, status_code=404)
        
        update_inventory = inventory_data.dict(exclude_unset=True)
        for key, value in update_inventory.items():
            setattr(inventory, key, value)

        db.session.commit()
        return JSONResponse(content=inventory.to_dict(), status_code=200)
    except SQLAlchemyError as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

async def delete_inventory(inventory_id: int):
    try:
        inventory = db.session.query(InventoryItem).filter_by(id=inventory_id).first()

        if not inventory:
            return JSONResponse(content={"error": "Inventory not found"}, status_code=404)
        
        db.session.delete(inventory)
        db.session.commit()
        return JSONResponse(content={"message": "Inventory deleted successfully"}, status_code=200)
    except SQLAlchemyError as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)