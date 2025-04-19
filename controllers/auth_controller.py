from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from schemas.auth_schema import CreateUserSchema, LoginSchema
from services.auth_service import create_user, login
from services.jwt_utils import get_current_user

router = APIRouter()  # ← THIS must be declared at top level!

@router.post("/auth/login",tags=["Auth"])
def login_controller(data: LoginSchema):  # data = JSON
    return login(data.username, data.password)

@router.post("/auth/register",tags=["Auth"])
def register_controller(data: CreateUserSchema):
    return create_user(data)


