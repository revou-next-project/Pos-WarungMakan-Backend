from fastapi import APIRouter
from schemas.product_schema import (
    ProductSchema,
    UpdateProductSchema
    
)

router = APIRouter()

from services.product_service import (
    get_all_products,
    get_product_byID,
    create_product,
    update_product,
    delete_product
)

@router.get("/products", tags=["Products"])
async def get_all_products_controller(category: str = None,):
    return await get_all_products(category)

@router.get("/products/{product_id}", tags=["Products"])
async def get_product_controller(product_id: int):
    return await get_product_byID(product_id)

@router.post("/products", tags=["Products"])
async def create_product_controller(product_data: ProductSchema):
    return await create_product(product_data)

@router.put("/products/{product_id}", tags=["Products"])
async def update_product_controller(product_id: int, product_data: UpdateProductSchema):
    return await update_product(product_id, product_data)

@router.delete("/products/{product_id}", tags=["Products"])
async def delete_product_controller(product_id: int):
    return await delete_product(product_id)