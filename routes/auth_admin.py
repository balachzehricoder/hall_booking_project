from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.admin import Admin
from app.schemas.admin import AdminCreate, AdminOut, AdminLogin
from app.utils.hash import hash_password, verify_password
from app.utils.jwt import create_access_token

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/admin/register", response_model=AdminOut)
def register(admin: AdminCreate, db: Session = Depends(get_db)):
    db_admin = db.query(Admin).filter(Admin.username == admin.username).first()
    if db_admin:
        raise HTTPException(status_code=400, detail="Admin already exists")
    
    hashed_pw = hash_password(admin.password)
    new_admin = Admin(username=admin.username, email=admin.email, password=hashed_pw)
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin

@router.post("/admin/login")
def login(admin: AdminLogin, db: Session = Depends(get_db)):
    db_admin = db.query(Admin).filter(Admin.username == admin.username).first()
    if not db_admin or not verify_password(admin.password, db_admin.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    token = create_access_token({"sub": db_admin.username})
    return {"access_token": token, "token_type": "bearer"}
