from fastapi import HTTPException
from passlib.hash import bcrypt
from models.user_model import User
from services.jwt_utils import create_access_token
from fastapi_sqlalchemy import db


def login(username: str, password: str):
    user = db.session.query(User).filter_by(username=username).first()
    if not user or not bcrypt.verify(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "sub": str(user.id),
        "role": user.role,
        "username": user.username
    })
    return {"access_token": token, "token_type": "bearer"}

def create_user(data):
    existing = db.session.query(User).filter_by(username=data.username).first()
    if existing:
        raise HTTPException(status_code=409, detail="Username already exists")

    hashed_pw = bcrypt.hash(data.password)
    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hashed_pw,
        role=data.role
    )
    db.session.add(user)
    db.session.commit()
    return {"message": "User created", "user_id": user.id}