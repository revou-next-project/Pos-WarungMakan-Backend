from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi_sqlalchemy import db
from models.recipeItem_model import RecipeItem
from models.InventoryItem_model import InventoryItem
from models.product_model import Product
from schemas.recipe_schema import (
    RecipeUpdateSchema,
    RecipeCreateSchema
)
from sqlalchemy.exc import SQLAlchemyError  # <-- Add this import
from sqlalchemy.orm import Session


async def get_all_recipes():
    # recipes = db.session.query(RecipeItem).all()
    # return JSONResponse(content=[recipe.to_dict() for recipe in recipes], status_code=200)
    try:
        # Query to join RecipeItem with InventoryItem and Product
        recipes = db.session.query(RecipeItem).outerjoin(
            InventoryItem, RecipeItem.inventory_item_id == InventoryItem.id
        ).outerjoin(
            Product, RecipeItem.product_id == Product.id
        ).all()

        # Format the results to match the desired response format
        result = []
        for recipe in recipes:
            # Check if the recipe already exists in the result (group by product)
            recipe_data = next(
                (
                    item
                    for item in result
                    if item["id"] == recipe.product_id
                ),
                None,
            )

            # If the recipe doesn't exist in the result, create it
            if not recipe_data:
                recipe_data = {
                    "id": recipe.product_id,
                    "recipe_id": recipe.id,
                    "name": recipe.product.name,  # From Product model
                    "description": recipe.product.description,  # From Product model
                    "category": recipe.product.category,  # From Product model
                    "ingredients": [],
                }
                result.append(recipe_data)

            # Add the ingredient to the ingredients list
            recipe_data["ingredients"].append(
                {
                    "id": recipe.inventory_item_id,
                    "name": recipe.inventory_item.name,  # From InventoryItem model
                    "quantity": recipe.quantity_needed,
                    "unit": recipe.inventory_item.unit,  # From InventoryItem model
                }
            )

        # Return the formatted response
        return JSONResponse(content=result, status_code=200)

    except Exception as e:
        # Handle exceptions (e.g., database errors)
        raise HTTPException(status_code=500, detail=str(e))

def get_recipe_by_product_id(product_id: int):
    recipes = db.session.query(RecipeItem).filter_by(product_id=product_id).all()
    if not recipes:
        raise HTTPException(status_code=404, detail="Recipe item not found")
    return JSONResponse(content=[recipe.to_dict() for recipe in recipes], status_code=200)

# def create_recipe(data: CreateRecipeItemSchema):
#     recipe = RecipeItem(**data.dict())
#     db.session.add(recipe)
#     db.session.commit()
#     return JSONResponse(content=recipe.to_dict(), status_code=201)
# Create Recipe function
async def create_recipe(payload: RecipeCreateSchema):
    try:
        # 1) Atomic transaction
        with db.session.begin():
            # 2) Find or create the product
            product = (
                db.session.query(Product)
                .filter(Product.name.ilike(payload.name.strip()))
                .first()
            )
            if not product:
                product = Product(
                    name=payload.name.strip(),
                    description=payload.description,
                    category=payload.category,
                )
                db.session.add(product)
                # product.id will be available after flush/commit

            # 3) For each ingredient, confirm InventoryItem exists and then ensure a RecipeItem
            for ing in payload.ingredients:
                inv = (
                    db.session.query(InventoryItem)
                    .filter(InventoryItem.name.ilike(ing.name.strip()))
                    .first()
                )
                if not inv:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Inventory item '{ing.name}' not found"
                    )

                # Check for an existing RecipeItem
                exists = (
                    db.session.query(RecipeItem)
                    .filter_by(
                        product_id=product.id,
                        inventory_item_id=inv.id
                    )
                    .first()
                )
                if not exists:
                    db.session.add(RecipeItem(
                        product_id=product.id,
                        inventory_item_id=inv.id,
                        quantity_needed=ing.quantity
                    ))
                else:
                    # (optional) update quantity if you want:
                    # exists.quantity_needed = ing.quantity
                    pass

        # 4) After the transaction, reload all ingredients for this product
        ingredients = []
        recs = (
            db.session.query(RecipeItem)
            .join(InventoryItem, RecipeItem.inventory_item_id == InventoryItem.id)
            .filter(RecipeItem.product_id == product.id)
            .all()
        )
        for item in recs:
            ingredients.append({
                "id": item.inventory_item_id,
                "name": item.inventory_item.name,
                "quantity": item.quantity_needed,
                "unit": item.inventory_item.unit
            })

        # 5) Return as JSONResponse
        return JSONResponse(
            status_code=201,
            content={
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "category": product.category,
                "ingredients": ingredients
            }
        )

    except HTTPException:
        # re-raise 4xx errors
        raise

    except SQLAlchemyError as e:
        # DB problems roll back automatically
        raise HTTPException(
            status_code=500,
            detail=f"Database error occurred: {e}"
        )

    except Exception as e:
        # any other error
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create recipe: {e}"
        )

# def update_recipe(recipe_id: int, data: UpdateRecipeItemSchema):
#     recipe = db.session.query(RecipeItem).filter_by(id=recipe_id).first()
#     if not recipe:
#         raise HTTPException(status_code=404, detail="Recipe item not found")

#     for key, value in data.dict(exclude_unset=True).items():
#         setattr(recipe, key, value)

#     db.session.commit()
#     return JSONResponse(content=recipe.to_dict(), status_code=200)
async def update_recipe(product_id: int, data: RecipeUpdateSchema):
    try:
        # All operations in one atomic transaction
        with db.session.begin():
            # 1) Load the product
            product = db.session.query(Product).filter_by(id=product_id).first()
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")

            # 2) Update only the fields provided
            update_fields = data.dict(exclude_unset=True, exclude={"ingredients"})
            for key, value in update_fields.items():
                setattr(product, key, value)

            # 3) Handle ingredients if present
            if data.ingredients:
                for ingredient in data.ingredients:
                    inv = db.session.query(InventoryItem).filter_by(name=ingredient.name).first()
                    if not inv:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Inventory item '{ingredient.name}' not found"
                        )

                    # find existing RecipeItem
                    ri = db.session.query(RecipeItem).filter_by(
                        product_id=product.id,
                        inventory_item_id=inv.id
                    ).first()

                    if ri:
                        ri.quantity_needed = ingredient.quantity
                    else:
                        db.session.add(RecipeItem(
                            product_id=product.id,
                            inventory_item_id=inv.id,
                            quantity_needed=ingredient.quantity,
                        ))

        # At this point the transaction is committed

        # 4) Re-fetch the ingredients to build the response
        ingredients = []
        for item in (
            db.session.query(RecipeItem)
            .join(InventoryItem, RecipeItem.inventory_item_id == InventoryItem.id)
            .filter(RecipeItem.product_id == product.id)
            .all()
        ):
            ingredients.append({
                "id": item.inventory_item_id,
                "name": item.inventory_item.name,
                "quantity": item.quantity_needed,
                "unit": item.inventory_item.unit,
            })

        return JSONResponse(
            status_code=200,
            content={
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "category": product.category,
                "ingredients": ingredients,
            }
        )

    except HTTPException:
        # Re-raise HTTPException (404, 400, etc.)
        raise

    except SQLAlchemyError as e:
        # Any SQLAlchemy error will have already rolled back
        raise HTTPException(status_code=500, detail=f"Database error occurred: {str(e)}")

    except Exception as e:
        # Fallback for any other error
        raise HTTPException(status_code=400, detail=f"Failed to update recipe: {str(e)}")


async def delete_recipe(product_id: int):
    try:
        # All-or-nothing: if anything fails, nothing is removed
        with db.session.begin():
            # Delete every RecipeItem whose product_id == recipe_id
            deleted_count = (
                db.session.query(RecipeItem)
                .filter_by(product_id=product_id)
                .delete(synchronize_session=False)
            )

            if deleted_count == 0:
                # No rows matched that product_id
                raise HTTPException(status_code=404, detail="Recipe not found")

        # If we reach here, transaction committed successfully
        return JSONResponse(
            status_code=200,
            content={
                "message": f"Deleted {deleted_count} ingredient(s) for recipe {product_id}"
            }
        )

    except HTTPException:
        # Propagate our 404
        raise

    except SQLAlchemyError as e:
        # Any DB error automatically rolls back
        raise HTTPException(status_code=500, detail=f"Database error occurred: {e}")

    except Exception as e:
        # Fallback for any other error
        raise HTTPException(status_code=400, detail=f"Failed to delete recipe: {e}")
