from fastapi import APIRouter, HTTPException, Depends
from schemas.recipe_schema import (
    RecipeCreateSchema, UpdateRecipeItemSchema,
    RecipeUpdateSchema

)
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
async def get_all(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    return await get_all_recipes()

@router.get("/{product_id}")
def get_one(product_id: int, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    return get_recipe_by_product_id(product_id)

# @router.post("")
# def create(data: RecipeCreateSchema, current_user: dict = Depends(get_current_user)):
#     if current_user["role"] != "admin":
#         raise HTTPException(status_code=403, detail="Access denied")
#     return create_recipe(data)
@router.post("")
async def create(
    recipe_data: RecipeCreateSchema, current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    try:
        # Call the service layer function to create the recipe
        return await create_recipe(recipe_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while creating the recipe.")

@router.put("/{product_id}")
async def update(product_id: int, data: RecipeUpdateSchema, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    return await update_recipe(product_id, data)

@router.delete("/{product_id}")
async def delete(product_id: int, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    return await delete_recipe(product_id)
