from pydantic import BaseModel

class AdminCreate(BaseModel):
    username: str
    email: str
    password: str

class AdminOut(BaseModel):
    id: int
    username: str
    class Config:
        orm_mode = True

class AdminLogin(BaseModel):
    username: str
    password: str
