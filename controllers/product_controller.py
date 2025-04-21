from fastapi import APIRouter, Depends, HTTPException
from schemas.product_schema import ProductSchema, UpdateProductSchema
from services.product_service import (
    get_all_products,
    get_product_byID,
    create_product,
    update_product,
    delete_product
)
from services.jwt_utils import get_current_user

router = APIRouter()


@router.get("/products", tags=["Products"])
async def get_all_products_controller(
    category: str = None,
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] not in ["admin", "cashier"]:
        raise HTTPException(status_code=403, detail="Access denied")
    return await get_all_products(category)

@router.get("/products/{product_id}", tags=["Products"])
async def get_product_controller(product_id: int,current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin", "cashier"]:
        raise HTTPException(status_code=403, detail="Access denied")
    return await get_product_byID(product_id)


@router.post("/products", tags=["Products"])
async def create_product_controller(
    product_data: ProductSchema,
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can add products")
    return await create_product(product_data, current_user)


@router.put("/products/{product_id}", tags=["Products"])
async def update_product_controller(
    product_id: int,
    product_data: UpdateProductSchema,
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update products")
    return await update_product(product_id, product_data, current_user)


@router.delete("/products/{product_id}", tags=["Products"])
async def delete_product_controller(
    product_id: int,
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete products")
    return await delete_product(product_id, current_user)
