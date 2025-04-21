from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from fastapi_sqlalchemy import db
from models.user_model import User
from schemas.user_schema import (
    UserUpdateSchema
)

async def get_all_users():
    try:
        users = db.session.query(User).all()
        return JSONResponse(content=[user.to_dict() for user in users], status_code=200)
    except SQLAlchemyError as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
async def update_user(user_id: int, user_data: UserUpdateSchema):
    try:
        user = db.session.query(User).filter_by(id=user_id).first()

        if not user:
            return JSONResponse(content={"error": "User not found"}, status_code=404)

        update_fields = user_data.dict(exclude_unset=True)
        for key, value in update_fields.items():
            setattr(user, key, value)

        db.session.commit()
        return JSONResponse(content=user.to_dict(), status_code=200)

    except SQLAlchemyError as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
async def delete_user(user_id: int):
    try:
        user = db.session.query(User).filter_by(id=user_id).first()

        if not user:
            return JSONResponse(content={"error": "User not found"}, status_code=404)

        db.session.delete(user)
        db.session.commit()
        return JSONResponse(content={"message": "User deleted successfully"}, status_code=200)

    except SQLAlchemyError as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)