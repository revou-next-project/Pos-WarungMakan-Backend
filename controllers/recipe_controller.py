from fastapi import APIRouter, HTTPException, Depends
from schemas.recipe_schema import CreateRecipeItemSchema, UpdateRecipeItemSchema
from services import recipe_services
from services.recipe_services import (
    get_all_recipes,
    get_recipe_by_product_id,
    create_recipe,
    update_recipe,
    delete_recipe
)
from services.jwt_utils import get_current_user

router = APIRouter(prefix="/recipes", tags=["Recipes"])

@router.get("")
def get_all(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    return recipe_services.get_all_recipes()

@router.get("/{product_id}")
def get_one(product_id: int, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    return recipe_services.get_recipe_by_product_id(product_id)

@router.post("")
def create(data: CreateRecipeItemSchema, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    return recipe_services.create_recipe(data)

@router.put("/{recipe_id}")
def update(recipe_id: int, data: UpdateRecipeItemSchema, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    return recipe_services.update_recipe(recipe_id, data)

@router.delete("/{recipe_id}")
def delete(recipe_id: int, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    return recipe_services.delete_recipe(recipe_id)
