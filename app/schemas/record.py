

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator

from app.models.record import RecordCategory, TransactionType


# ── Request schemas 

class RecordCreateRequest(BaseModel):
 
    amount:   float           = Field(..., gt=0, example=1500.00,
                                      description="Must be greater than zero")
    txn_type: TransactionType = Field(..., example="income")
    category: RecordCategory  = Field(..., example="salary")
    txn_date: date            = Field(..., example="2024-03-15")
    notes:    Optional[str]   = Field(None, max_length=500, example="March salary")

    @validator("amount")
    def round_amount(cls, value):
        # Always store money rounded to 2 decimal places
        return round(value, 2)


class RecordUpdateRequest(BaseModel):
    #All fields are optional — partial updates are supported."""
    amount:   Optional[float]           = Field(None, gt=0)
    txn_type: Optional[TransactionType] = None
    category: Optional[RecordCategory]  = None
    txn_date: Optional[date]            = None
    notes:    Optional[str]             = Field(None, max_length=500)

    @validator("amount", pre=True, always=True)
    def round_amount(cls, value):
        if value is not None:
            return round(value, 2)
        return value


# ── Response schemas 

class RecordResponse(BaseModel):
    #Full record details returned by the API.
    record_id:  int
    amount:     float
    txn_type:   TransactionType
    category:   RecordCategory
    txn_date:   date
    notes:      Optional[str]
    owner_id:   int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedRecordsResponse(BaseModel):
    
    total_count:  int
    page:         int
    page_size:    int
    total_pages:  int
    records:      List[RecordResponse]


# ── Analytics / Summary schemas ──────────────────────────────────────────────

class BalanceSummaryResponse(BaseModel):
    
    total_income:   float
    total_expenses: float
    net_balance:    float           # income − expenses


class MonthlySummaryEntry(BaseModel):
    year:           int
    month:          int
    total_income:   float
    total_expenses: float
    net_balance:    float


class CategoryBreakdownEntry(BaseModel):
    category:   RecordCategory
    txn_type:   TransactionType
    total:      float
    count:      int
