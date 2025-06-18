
from datetime import datetime
from unittest.mock import Base

from sqlalchemy import Boolean, Column, DateTime, Integer, String


class Owner(Base):
    __tablename__ = 'Owner'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    contact = Column(String(20), nullable=True)
    hall_name = Column(String(100), nullable=True)
    profile_picture = Column(String(255), nullable=True)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
