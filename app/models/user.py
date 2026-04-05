

import enum
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserRole(str, enum.Enum):
  
    ADMIN   = "admin"
    ANALYST = "analyst"
    VIEWER  = "viewer"


class User(Base):
    __tablename__ = "users"

    user_id    = Column(Integer, primary_key=True, index=True)
    full_name  = Column(String(100), nullable=False)
    email      = Column(String(150), unique=True, index=True, nullable=False)
    hashed_pw  = Column(String(255), nullable=False)   # NEVER store plain passwords
    role       = Column(Enum(UserRole), default=UserRole.VIEWER, nullable=False)
    is_active  = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # One user can have many financial records
    records = relationship("FinancialRecord", back_populates="owner", cascade="all, delete")
