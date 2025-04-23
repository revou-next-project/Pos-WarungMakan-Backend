from fastapi import APIRouter, Depends, HTTPException
from schemas.inventory_schema import AddStockSchema, InventorySchema, UpdateInventorySchema
from services.inventory_service import (
    add_stock,
    get_all_inventory,
    get_inventory_byID,
    create_inventory,
    update_inventory,
    delete_inventory
)
from services.jwt_utils import get_current_user

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("")
async def get_all_inventory_controller(
    category: str = None,
    low_stock: bool = False,
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] not in ["admin", "cashier"]:
        raise HTTPException(status_code=403, detail="Access denied")
    return await get_all_inventory(category, low_stock)


@router.get("/{inventory_id}")
async def get_inventory_controller(
    inventory_id: int,
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] not in ["admin", "cashier"]:
        raise HTTPException(status_code=403, detail="Access denied")
    return await get_inventory_byID(inventory_id)

@router.post("")
async def create_inventory_controller(
    inventory_data: InventorySchema,
    current_user: dict = Depends(get_current_user)
): 
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    inventory_data.recorded_by = current_user["id"]
    return await create_inventory(inventory_data)


@router.put("/{inventory_id}")
async def update_inventory_controller(
    inventory_id: int,
    inventory_data: UpdateInventorySchema,
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    inventory_data.recorded_by = current_user["id"]
    return await update_inventory(inventory_id, inventory_data)


@router.delete("/{inventory_id}")
async def delete_inventory_controller(
    inventory_id: int,
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return await delete_inventory(inventory_id)


@router.patch("/{inventory_id}/add-stock")
async def add_stock_controller(
    inventory_id: int,
    stock_data: AddStockSchema,
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only access")
    
    return await add_stock(inventory_id, stock_data, current_user["id"])