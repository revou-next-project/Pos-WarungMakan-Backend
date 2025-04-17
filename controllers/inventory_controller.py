from fastapi import APIRouter
from schemas.inventory_schema import (
    InventorySchema,
    UpdateInventorySchema
    
)

router = APIRouter()

from services.inventory_service import (
    get_all_inventory,
    get_inventory_byID,
    create_inventory,
    update_inventory,
    delete_inventory
)


@router.get("/inventory", tags=["Inventory"])
async def get_all_inventory_controller(category: str = None, low_stock: bool = False):
    return await get_all_inventory(category, low_stock)

@router.get("/inventory/{inventory_id}", tags=["Inventory"])
async def get_inventory_controller(inventory_id: int):
    return await get_inventory_byID(inventory_id)

@router.post("/inventory", tags=["Inventory"])
async def create_inventory_controller(inventory_data: InventorySchema): 
    return await create_inventory(inventory_data)

@router.put("/inventory/{inventory_id}", tags=["Inventory"])
async def update_inventory_controller(inventory_id: int, inventory_data: UpdateInventorySchema):
    return await update_inventory(inventory_id, inventory_data)

@router.delete("/inventory/{inventory_id}", tags=["Inventory"])
async def delete_inventory_controller(inventory_id: int):
    return await delete_inventory(inventory_id)