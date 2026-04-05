

import enum
from datetime import datetime

from sqlalchemy import (
    Column, Date, DateTime, Enum, Float,
    ForeignKey, Integer, String, Text,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class TransactionType(str, enum.Enum):
 
    INCOME  = "income"
    EXPENSE = "expense"


class RecordCategory(str, enum.Enum):

    SALARY      = "salary"
    FREELANCE   = "freelance"
    INVESTMENT  = "investment"
    FOOD        = "food"
    TRANSPORT   = "transport"
    HOUSING     = "housing"
    HEALTHCARE  = "healthcare"
    EDUCATION   = "education"
    SHOPPING    = "shopping"
    UTILITIES   = "utilities"
    TRAVEL      = "travel"
    ENTERTAINMENT = "entertainment"
    OTHER       = "other"


class FinancialRecord(Base):
    __tablename__ = "financial_records"

    record_id    = Column(Integer, primary_key=True, index=True)
    amount       = Column(Float, nullable=False)                      # Money amount (positive)
    txn_type     = Column(Enum(TransactionType), nullable=False)      # income or expense
    category     = Column(Enum(RecordCategory), nullable=False)       # what bucket it falls into
    txn_date     = Column(Date, nullable=False)                       # date of the transaction
    notes        = Column(Text, nullable=True)                        # optional description
    created_at   = Column(DateTime, default=datetime.utcnow)
    updated_at   = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign key links this record to a specific user
    owner_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    owner    = relationship("User", back_populates="records")
