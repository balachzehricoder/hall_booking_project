
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from jose import jwt, JWTError
from datetime import datetime, timedelta
from app.schemas import UserCreate, UserLogin
from app import models, schemas
from app.database import get_db
from app.utils.hash import hash_password, verify_password
from app.utils.email import send_verification_email

router = APIRouter(prefix="/user", tags=["User Auth"])

# JWT Config
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# ----------------- Register -----------------
@router.post("/register")
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user.password)
    new_user = models.User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        contact=user.contact,
        is_verified=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create email verification token
    token_data = {"sub": new_user.email, "exp": datetime.utcnow() + timedelta(minutes=60)}
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    send_verification_email(new_user.email, token)

    return {"msg": "User registered. Please check your email to verify."}

# ----------------- Email Verify -----------------
@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=400, detail="Invalid token")

        user = db.query(models.User).filter(models.User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.is_verified:
            return {"msg": "Email already verified"}

        user.is_verified = True
        db.commit()
        return JSONResponse(status_code=200, content={"msg": "Email verified successfully"})
    
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

# ----------------- Login -----------------
@router.post("/login")
def login_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not db_user.is_verified:
        raise HTTPException(status_code=403, detail="Please verify your email before logging in")

    return {"msg": "Login successful"}
