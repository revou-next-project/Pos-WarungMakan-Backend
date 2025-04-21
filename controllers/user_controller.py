from fastapi import APIRouter, Depends, HTTPException
from services.user_service import (
    get_all_users,
    update_user,
    delete_user
)
from services.jwt_utils import get_current_user
from schemas.user_schema import (
    UserUpdateSchema
)

router = APIRouter()


@router.get("/users", tags=["Users"])
async def get_all_users_controller(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view users")
    return await get_all_users()

@router.put("/users/{user_id}", tags=["Users"])
async def update_user_controller(
    user_id: int,
    user_data: UserUpdateSchema,
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update users")
    return await update_user(user_id, user_data)


@router.delete("/users/{user_id}", tags=["Users"])
async def delete_user_controller(
    user_id: int,
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete users")
    return await delete_user(user_id)