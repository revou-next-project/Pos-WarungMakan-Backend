from fastapi import APIRouter
from controllers import (
    auth_controller,
    product_controller,
    inventory_controller,
    orders_controller,
    recipe_controller
)

router = APIRouter()

# Include all route groups
router.include_router(auth_controller.router)
router.include_router(product_controller.router)
router.include_router(inventory_controller.router)
router.include_router(orders_controller.router)
router.include_router(recipe_controller.router)
