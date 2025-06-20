# schemas/user.py
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    contact: str

class UserLogin(BaseModel):
    username: str
    password: str
