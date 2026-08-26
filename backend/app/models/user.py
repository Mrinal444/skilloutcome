import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Enum, DateTime
from app.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    TRAINEE = "TRAINEE"
    PROVIDER = "PROVIDER"
    EMPLOYER = "EMPLOYER"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
