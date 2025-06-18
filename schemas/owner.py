from pydantic import BaseModel, EmailStr

class OwnerCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    contact: str
    hall_name: str

class OwnerLogin(BaseModel):
    username: str
    password: str
