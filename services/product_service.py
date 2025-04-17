from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from app import db
from models.product_model import Product
from schemas.product_schema import (
    ProductSchema,
    UpdateProductSchema
)

async def get_all_products(category: str = None):
    try:
        if category:
            products = db.session.query(Product).filter_by(category=category).all()
            return JSONResponse(content=[product.to_dict() for product in products], status_code=200)
        
        else:
            products = db.session.query(Product).all()
            return JSONResponse(content=[product.to_dict() for product in products], status_code=200)
    except SQLAlchemyError as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
async def get_product_byID(product_id: int):
    try:
        product = db.session.query(Product).filter_by(id=product_id).first()
        return JSONResponse(content=product.to_dict(), status_code=200)
    except SQLAlchemyError as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

async def create_product(product_data: ProductSchema):
    try:
        product = Product(
            name=product_data.name,
            price=product_data.price,
            category=product_data.category,
            unit=product_data.unit,
            is_package=product_data.is_package,
            image=product_data.image
        )
        db.session.add(product)
        db.session.commit()
        return JSONResponse(content=product.to_dict(), status_code=201)
    except SQLAlchemyError as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
async def update_product(product_id: int, product_data: UpdateProductSchema):
    try:
        product = db.session.query(Product).filter_by(id=product_id).first()

        if not product:
            return JSONResponse(content={"error": "Product not found"}, status_code=404)
        
        update_product = product_data.dict(exclude_unset=True)
        for key, value in update_product.items():
            setattr(product, key, value)

        db.session.commit()
        return JSONResponse(content=product.to_dict(), status_code=200)
    except SQLAlchemyError as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

async def delete_product(product_id: int):
    try:
        product = db.session.query(Product).filter_by(id=product_id).first()

        if not product:
            return JSONResponse(content={"error": "Product not found"}, status_code=404)
        
        db.session.delete(product)
        db.session.commit()
        return JSONResponse(content={"message": "Product deleted successfully"}, status_code=200)
    except SQLAlchemyError as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)