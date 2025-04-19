from pydantic import BaseModel, EmailStr

class LoginSchema(BaseModel):
    username: str
    password: str
    
class CreateUserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str  # admin or cashier