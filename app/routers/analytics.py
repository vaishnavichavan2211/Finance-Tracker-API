
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_analyst_or_above
from app.models.user import User
from app.schemas.record import (
    BalanceSummaryResponse,
    CategoryBreakdownEntry,
    MonthlySummaryEntry,
)
from app.services import record_service

router = APIRouter()


@router.get(
    "/summary",
    response_model=BalanceSummaryResponse,
    summary="Get overall financial summary (income, expenses, balance)",
)
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_or_above),
):
    
    return record_service.get_balance_summary(db, current_user)


@router.get(
    "/monthly",
    response_model=List[MonthlySummaryEntry],
    summary="Month-by-month income and expense breakdown",
)
def get_monthly_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_or_above),
):
  
    return record_service.get_monthly_summary(db, current_user)


@router.get(
    "/categories",
    response_model=List[CategoryBreakdownEntry],
    summary="Spending and income broken down by category",
)
def get_category_breakdown(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_or_above),
):
  
    return record_service.get_category_breakdown(db, current_user)


@router.get(
    "/top-categories",
    response_model=List[CategoryBreakdownEntry],
    summary="Top N expense categories (custom endpoint!)",
)
def get_top_expense_categories(
    top_n: int = Query(5, ge=1, le=20, description="How many top categories to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_or_above),
):
   
    all_categories = record_service.get_category_breakdown(db, current_user)

    # Filter to expenses only, then return the top N
    expense_categories = [c for c in all_categories if c["txn_type"] == "expense"]
    return expense_categories[:top_n]
