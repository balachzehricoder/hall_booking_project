from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from jose import jwt, JWTError
from datetime import datetime, timedelta
from app.database import get_db
from app.schemas.owner import OwnerCreate, OwnerLogin
from app.utils.hash import hash_password, verify_password
from app.utils.email import send_verification_email
from app import models, schemas
from app.utils import hash  as Hash
from app.utils.email import send_verification_email
from app import models
from app.database import get_db
from app.models.owner import Owner



router = APIRouter(prefix="/Owner", tags=["Owner Auth"])

# JWT Config
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

@router.post("/register")
def register_Owner(owner: OwnerCreate, db: Session = Depends(get_db)):
    # ✅ Use imported Owner model class
    existing_owner = db.query(Owner).filter(Owner.email == owner.email).first()
    if existing_owner:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(owner.password)
    new_owner = Owner(
        username=owner.username,
        email=owner.email,
        password=hashed_password,
        contact=owner.contact,
        hall_name=owner.hall_name,
        is_verified=False
    )
    db.add(new_owner)
    db.commit()
    db.refresh(new_owner)

    # Send email verification
    token_data = {"sub": new_owner.email, "exp": datetime.utcnow() + timedelta(minutes=60)}
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    send_verification_email(new_owner.email, token)

    return {"msg": "Owner registered. Please verify your email."}


# ------------------ Verify Email ------------------
@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=400, detail="Invalid token")

        Owner = db.query(models.Owner).filter(models.Owner.email == email).first()
        if not Owner:
            raise HTTPException(status_code=404, detail="Owner not found")

        if Owner.is_verified:
            return {"msg": "Email already verified"}

        Owner.is_verified = True
        db.commit()
        return {"msg": "Email verified successfully"}
    
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

# ------------------ Login ------------------
@router.post("/login")
def login_Owner(owner: OwnerLogin, db: Session = Depends(get_db)):
    db_owner = db.query(Owner).filter(Owner.username == owner.username).first()

    if not db_owner or not verify_password(owner.password, db_owner.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not db_owner.is_verified:
        raise HTTPException(status_code=403, detail="Please verify your email before logging in")

    token_data = {
        "sub": db_owner.username,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": token, "token_type": "bearer"}

# ------------------ Get Owner Profile ------------------