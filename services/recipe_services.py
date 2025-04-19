from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi_sqlalchemy import db
from models.recipeItem_model import RecipeItem
from schemas.recipe_schema import CreateRecipeItemSchema, UpdateRecipeItemSchema

def get_all_recipes():
    recipes = db.session.query(RecipeItem).all()
    return JSONResponse(content=[recipe.to_dict() for recipe in recipes], status_code=200)

def get_recipe_by_product_id(product_id: int):
    recipes = db.session.query(RecipeItem).filter_by(product_id=product_id).all()
    if not recipes:
        raise HTTPException(status_code=404, detail="Recipe item not found")
    return JSONResponse(content=[recipe.to_dict() for recipe in recipes], status_code=200)

def create_recipe(data: CreateRecipeItemSchema):
    recipe = RecipeItem(**data.dict())
    db.session.add(recipe)
    db.session.commit()
    return JSONResponse(content=recipe.to_dict(), status_code=201)

def update_recipe(recipe_id: int, data: UpdateRecipeItemSchema):
    recipe = db.session.query(RecipeItem).filter_by(id=recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe item not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(recipe, key, value)

    db.session.commit()
    return JSONResponse(content=recipe.to_dict(), status_code=200)

def delete_recipe(recipe_id: int):
    recipe = db.session.query(RecipeItem).filter_by(id=recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe item not found")
    
    db.session.delete(recipe)
    db.session.commit()
    return JSONResponse(content={"message": "Recipe item deleted"}, status_code=200)
