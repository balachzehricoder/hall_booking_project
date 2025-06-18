from fastapi import FastAPI
from app.routes import auth_admin
from app.database import Base, engine
from app.models import admin
from app.routes import auth_user
from app.routes import auth_owner
from app.models import user
from app.models import owner
app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth_admin.router)
app.include_router(auth_user.router)
app.include_router(auth_owner.router)


